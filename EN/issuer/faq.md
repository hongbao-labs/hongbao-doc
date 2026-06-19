# Issuer FAQ

## Contract

**Q: Does the contract have an owner? Can I control it?**
No owner, no pause, no admin, no upgrades. We deliberately removed all privileged operations — this is both a trustless design choice and the path of least compliance friction. The only actions available to you are deposit and expiry reclaim.

**Q: Can I set a shorter expiry, like 7 days?**
No. `MIN_LOCK_TIME = 30 days` is a hardcoded contract constant. The reason: cardholders need sufficient time to claim, and a short lock period invites disputes between issuers and cardholders. If your campaign specifically requires a shorter window, you can fork the contract and modify it — but that is no longer our standard contract, and you will need to conduct your own audit.

**Q: Can I do a privileged reclaim — take back unclaimed funds before expiry?**
No. If you could reclaim early, you could invalidate a user's gift at any time, which defeats the fundamental promise of a red packet. If you need that capability, please reconsider whether Hongbao is the right fit.

**Q: Has the contract been audited?**
No third-party audit yet. The team has a security background and the contract was designed and reviewed by a senior auditor internally. At this stage we have determined that a third-party audit is not cost-justified; we will revisit based on order volume and client requirements. The code is fully public at https://github.com/hongbao-labs/contracts — you are welcome to review it yourself or commission an independent audit.

**Q: Does the contract take any fees?**
None. Zero on-chain fees, zero protocol take — by design, to minimize compliance friction. Hongbao's revenue comes from hardware sales, issuer customization service fees, and ecosystem partnership revenue (wallets, exchanges, Dapps) — all **outside the protocol layer**, fully decoupled from issuer funds.

**Q: How will the contract be upgraded?**
**It won't be.** A Pool is a one-time, immutable deployment. If issues are found or new features are needed in the future, we will deploy a new contract version (new Factory). Existing pools continue running under the logic they were deployed with; assets already deposited are unaffected.

## Operations

**Q: Do I need to write scripts for on-chain operations like approve / batchDeposit / Pool deployment?**
No. The Web Dapp wraps Factory deployment, Pool creation, approve, batch deposit, and batch withdrawExpired behind buttons. Connect your deposit wallet, upload your batch JSON, set parameters, and click Lock. If your team wants to interact directly at the contract layer or build a custom issuer client, refer to the open-source repo (https://github.com/hongbao-labs/contracts).

**Q: How many cards can I issue in a single transaction?**
You don't need to think about this. The Web Dapp automatically splits batches according to the target chain's gas limit, with real-time progress feedback and retry support for failures. The underlying constraint is that a single batch is bounded by the gas limit ([TBD: typical batch size per chain]).

**Q: Can I lock multiple asset types to a single card?**
No. One Pool is bound to one asset. Multiple assets require multiple Pools — but each card can receive one deposit per Pool.

**Note:** This is not recommended. A card can only sign once. If a card has assets locked across multiple Pools, the cardholder can only claim from one Pool per signature; assets in the remaining Pools are permanently locked until expiry reclaim.

**Q: Can a single card have assets locked on multiple chains simultaneously?**
Technically yes, but **not recommended**. A card can only sign once — wherever the cardholder claims, assets on all other chains are locked until expiry. Unless you intentionally design a campaign around this "mutually exclusive multi-chain lock" mechanic, avoid it.

**Q: Can I top up a card's ERC20 balance multiple times?**
Yes. Run another deposit for the same card in the same batch in the Web Dapp. The expiry is fixed to the first deposit's lockTime — any lockTime passed in subsequent top-ups is ignored at the contract level.

**Q: Is there support for multiple depositors funding the same card?**
At the contract level, yes (an "open mode" Pool). The Web Dapp does not currently expose this flow directly. Developer teams who need this should interact at the contract layer — see the open-source repo (https://github.com/hongbao-labs/contracts).

**Q: How soon can I reclaim unclaimed funds?**
After the `lockTime` set at deposit (minimum 30 days). Use one-click Withdraw Expired in the Web Dapp; assets return to your wallet immediately.

**Q: Can I top up a card that has already been claimed?**
Plain card: No — once claimed, the card is marked complete on-chain. Task card: Top-ups go to the basic amount only (task slots are immutable after creation), and the card must not yet have a bound recipient address, must not be expired, and must not be closed.

## Tasks and Data

**Q: How do task cards work?**
The card's balance is split into a "basic amount + task amount." The cardholder scans the card and presses the button once to claim the basic amount — **this signature simultaneously locks the recipient address to the card**. After that, each completed task unlocks one task amount, and funds flow automatically to the locked address. Up to 255 tasks are supported, each with an independent amount.

**Q: Who decides whether a task is complete?**
You do. The unlock credential (preimage) for each task is generated by you. You can host it on Hongbao Web and have us distribute it, or export it to your own backend and distribute it yourself — **completion authority is entirely in your hands**.

**Q: If a preimage leaks, can someone else claim the task amount?**
No. Task funds are **forced to the address the cardholder locked in during their first signature**. Even if a preimage leaks, submitting it sends funds only to the original cardholder's address. Additionally, each preimage is bound to a specific (chain, Pool, card, task slot) — it cannot be replayed across chains, cards, or tasks.

**Q: What happens to task amounts the cardholder never completes?**
After expiry, you run `withdrawExpired` to reclaim all remaining funds (unclaimed basic amount + unlocked task amounts) and close the card. Amounts already claimed by the cardholder are unaffected.

**Q: What user data do you provide, and how is it collected?**
Primarily public on-chain data: cardholder addresses, gas consumption, DEX interactions, and other behavioral signals derived from on-chain analytics. The Web dashboard tracks this in real time, supports export, and can generate analysis reports with one-click AI summarization.

**Q: How is data privacy handled?**
Tiered approach: a cardholder only binds a social account and unlocks a detailed profile when they **complete tasks**. Cardholders who do not engage with tasks are represented only by an on-chain address — no forced binding to real social identity. Privacy boundaries are governed by the user agreement.

> The task system and data dashboard are still being built out; capabilities will roll out incrementally.

## App and Relayer

**Q: Do cardholders have to use the Hongbao App?**
Yes. The Hongbao official App / Web is the only standard cardholder interface. Hardware, client, and contract are tightly coupled — unified firmware auditing, BLE protocol, and UX are core to the product's security and experience guarantees, and serve as the integration point for Hongbao's ecosystem partners (wallets, exchanges, Dapps). Issuers who want branded presentation should use **co-branded card customization** (Hongbao logo retained, all other areas open — see [customization.md](customization.md)). App-level customization is not offered.

**Q: Do I have to use your Relayer?**
No. `withdraw(unlockAddress, to, v, r, s)` has no `msg.sender` restriction — any EOA can submit the transaction. You can use ours (the default), run your own, or have cardholders submit directly through another wallet (provided the user or you covers gas).

**Q: Does using your Relayer cost anything?**
By default we cover gas on your behalf, currently at no charge — this is an early-stage promotion and may be subject to a fair-use policy in the future. If your distribution volume is large or you require an SLA, self-hosting the Relayer is recommended. See the open-source repo (https://github.com/hongbao-labs/contracts) for details.

**Q: Can cardholders pay their own gas?**
At the contract level there is no restriction on who submits (no `msg.sender` check on `withdraw`). The Hongbao official App defaults to Relayer-sponsored transactions — that is the standard cardholder experience. If your team builds a custom client on top of the contract ABI, you can have users pay gas from their own wallet (see the open-source repo https://github.com/hongbao-labs/contracts), but this requires users to hold native tokens and degrades the experience.

## Loss and After-Sales

**Q: What if cards arrive damaged?**
Handled per the DOA policy in your commercial contract (case by case). Please perform sampling inspection upon receipt.

**Q: A cardholder lost their card. Can they recover the funds?**
Not before expiry. The card is the private key — losing the card means losing the key and losing the ability to transfer assets. After expiry, you can run `withdrawExpired` to reclaim the funds and issue the cardholder a replacement card with a new deposit. **This is our recommended lost-card SOP:** cardholder reports loss → you log it → wait for expiry reclaim → reissue new card + new deposit.

**Q: Can you provide device serial numbers or card anti-counterfeiting traceability?**
Each card's ETH address is its unique identifier. We do not offer an additional anti-counterfeiting or tracking service — if you need this, you can build a SKU system on top of the ETH addresses. Custom solutions available [TBD].

**Q: What is the card's battery life?**
Approximately 3 years by design (negligible drain in deep sleep; minimal consumption during active use). The battery is not replaceable.

## Legal and Compliance

**Q: Who is responsible for compliance?**
**You are.** We provide a trustless hardware and contract toolkit. The specific act of distribution — who receives what assets, in what amounts — is executed by you. Tax obligations, KYC, AML, and regional compliance requirements are your responsibility. Our contract charges no fees, holds no admin key, and retains no privileged access — by design, to minimize our own compliance surface. See your contract for specifics.

**Q: Do you retain records of cardholder claims?**
Our Relayer maintains minimal operational logs for abuse prevention and troubleshooting, but we do not retain user information beyond what is operationally necessary. If you have concerns about these logs, self-host the Relayer.

**Q: If Hongbao's service has issues — server downtime, Relayer outage — can my distributed cards still be claimed?**

**Assets are 100% safe.** The contract is deployed on a public chain with no owner and no dependency on any centralized service — your assets are guaranteed by the protocol itself, independent of any centralized service's operational status.

**Claim access:** Under normal conditions, cardholders use the Hongbao official Web / App, and brief outages will recover automatically. In an extreme scenario, anyone can submit a claim transaction via the public interfaces: the contract ABI is public, the BLE interface spec is public, and the CLI tool is open-source — a technically capable party can implement their own client. For those who cannot, our technical support team is available to step in. **Under no circumstances will your assets be permanently stuck in the contract.**

---

## Product Positioning

**Q: How does Hongbao compare to hardware wallets (the multi-use signing devices commonly sold to end users)?**
Entirely different products. A hardware wallet is a multi-use signing device sold to end users for long-term private key management — it is a persistent relationship between device and user. Hongbao is a **one-time signing device plus an on-chain distribution protocol**, sold to asset distributors (issuers, exchanges, enterprises). The card transfers ownership to the recipient on delivery and is then spent — it is not the user's "wallet."

If you want to give an employee a long-term wallet, buy a hardware wallet. If you want to precisely distribute an asset to 1,000 users and complete their onboarding, use Hongbao.

**Q: How does Hongbao compare to crypto gift card products on the market?**
They are **custodial** — the platform collects funds upfront and cardholders redeem against a platform balance. Hongbao is a **protocol with fully decoupled asset flow** — the issuer locks assets directly into the contract; we never touch a single dollar, never distribute a single dollar, and never hold any balance. **This is not a marginal improvement — it is a generational architectural difference.**

## More Questions?

Business and purchasing: hello@hongbao.digital
Technical questions: zwx@hongbao.digital
