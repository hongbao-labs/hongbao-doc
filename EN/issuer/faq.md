# FAQ

## Contract

**Q: Does the contract have an owner? Can I control it?**
No owner, no pause, no admin, no upgrades — every privileged operation has been stripped out. This is trustless by design: once deployed, the contract runs on its own, the funds stay entirely under the issuer's control, and Hongbao never touches them. The only things you can do are deposit and reclaim after expiry.

**Q: Can I set a shorter expiry, like 7 days?**
No. `MIN_LOCK_TIME = 30 days` is hardcoded as a contract constant. The reason: it gives cardholders enough time to claim and avoids disputes between issuers and cardholders that a short lock period would invite. If your campaign genuinely needs a shorter lock, you can fork the contract and modify it yourself — but at that point it is no longer our standard contract, and you will need to audit it yourself.

**Q: Can I do a privileged reclaim — take back unclaimed funds before expiry?**
No. Reclaiming early would mean you could invalidate a user's "gift" at any time, which breaks the fundamental promise of a red packet. If you need that capability, please reconsider whether Hongbao is the right fit.

**Q: Has the contract been audited?**
Not by a third party yet. The team comes from a security background, and the contract was designed by a senior auditor and reviewed internally. A third-party audit is already planned; the exact timing depends on order volume and customer needs, and the report will be published here once it is ready. The code is fully public at [github.com/hongbao-labs/contracts](https://github.com/hongbao-labs/contracts) — you are welcome to review it yourself or commission an independent audit.

**Q: Does the contract take any fees?**
No. Zero on-chain fees, zero take — by design. Hongbao never touches issuer funds; the whole flow is on-chain and the funds stay under the issuer's own control. Our revenue comes from hardware sales, customization service fees for issuers, and in-app revenue sharing with ecosystem partners such as wallets and exchanges — all of it outside the protocol layer and fully decoupled from issuer funds.

**Q: How will the contract be upgraded?**
It won't be. A Pool is a one-time, immutable deployment. If a problem turns up or a new feature is needed down the line, we ship a new contract version (a new Factory); existing Pools keep running under the logic they were deployed with, and already-deposited assets are unaffected.

## Operations

**Q: Do I have to write my own scripts for on-chain operations like approve / batchDeposit / deploying a Pool?**
No. The Web Dapp already wraps Factory deployment, Pool creation, approve, batch deposit, and batch withdrawExpired behind buttons — you just connect your deposit wallet, upload the batch JSON, set the parameters, and click Lock. If your team prefers to work directly at the contract layer or build its own issuer client, see the [open-source repo](https://github.com/hongbao-labs/contracts).

**Q: How many cards can I issue in a single transaction?**
You don't need to worry about it. The Web Dapp automatically splits batches to fit the target chain's gas limit, shows real-time progress for each transaction, and lets you retry failures. The underlying constraint is that a single batch is bounded by the target chain's gas limit, and the Web Dapp adapts the batch size per chain automatically.

**Q: Can I lock multiple asset types to a single card?**
No. One Pool is bound to one asset. Multiple assets mean multiple Pools — but each card can receive one deposit in each Pool.

> Not recommended — a card can only sign once. If a card has assets locked across multiple Pools, the user can only claim from one of them when redeeming; the assets in the other Pools are stuck there until expiry, when you can reclaim them.

**Q: Can a single card hold assets locked on multiple chains at once?**
Technically yes, but not recommended. A card can only sign once — whichever chain the user claims on, the assets on the other chains stay locked until expiry, when you can reclaim them. Unless you intend this "mutually exclusive multi-chain lock" as a campaign mechanic, don't use it this way.

**Q: Can I top up a card's ERC20 balance multiple times?**
Yes. Just run another deposit for the same card in the same batch in the Web Dapp; the expiry follows the first deposit (the contract ignores any new lockTime passed in on a top-up).

**Q: Do you support the advanced setup where multiple depositors fund the same card?**
It is supported at the contract level (an "open mode" Pool), but the Web Dapp does not currently expose this path directly. Developer teams that need it should work at the contract layer — see the [open-source repo](https://github.com/hongbao-labs/contracts).

**Q: How soon can I get back funds a user never claimed?**
Once the `lockTime` set at deposit expires (minimum 30 days). Click Withdraw Expired in the Web Dapp, and the assets return to your wallet immediately.

**Q: Can a card that has already been claimed be topped up?**
Plain card: no — once claimed, it is already marked complete on-chain. Task card: a top-up only adds to the basic amount (task slots are immutable once created), and it requires that the card has not yet bound a recipient address, has not expired, and has not been closed.

## Tasks and Data

**Q: How do task cards work?**
The card's balance is split into a "basic amount + task amount." The user scans the card and presses the button once to claim the basic amount — and that same signature locks the recipient address onto the card. From then on, each completed task unlocks one task amount, with the funds flowing automatically to the locked address. Up to 255 tasks are supported, each with its own independent amount.

**Q: Who decides whether a task is complete?**
You do. You generate the unlock credential (preimage) for each task. You can host it on Hongbao Web and have us distribute it for you, or export it to your own backend and distribute it yourself — the authority to judge completion stays in your hands.

**Q: If an unlock credential leaks, can someone else claim it?**
No. Task funds are forced to the address the user locked in with their first signature. Even if the credential leaks, submitting it only sends the money to the original cardholder's address. On top of that, each credential is bound to a specific chain, Pool, card, and task slot, so it cannot be replayed across chains, cards, or tasks.

**Q: What happens to task amounts the user never completes?**
After expiry, you reclaim all remaining funds (unclaimed basic amount + unlocked task amounts) with a single `withdrawExpired` and close the card. Amounts the user has already claimed are unaffected.

**Q: What user data do you return to me, and how is it collected?**
Mainly public on-chain data: user addresses, gas consumption, DEX interactions, and other behavior derived from on-chain analytics. The Web dashboard tracks it in real time, supports export, and can generate an AI analysis report in one click.

**Q: How is data privacy handled?**
A tiered approach. A user only binds a social account and unlocks a detailed profile once they complete tasks; users who don't engage with tasks remain just an on-chain address, with no forced binding to a real social identity. The privacy boundaries are governed by the [privacy policy](https://hongbao.digital/#/privacy).

> The task system and data dashboard are still being built out; capabilities will roll out incrementally.

## App and Relayer

**Q: Do cardholders have to use the Hongbao App?**
Yes. The official Hongbao App / Web is the only standard cardholder entry point. The hardware, client, and contract are tightly coupled, with unified firmware auditing, Bluetooth protocol, and UX — this is the foundation of the product's security and experience, and it is also the gateway for Hongbao's partnerships across the ecosystem (wallets, exchanges, Dapps). Issuers who want branded presentation go through co-branded card customization (the Hongbao logo stays, the rest of the surface is open — see [customization.md](customization.md)); customization is not done on the App side.

**Q: Do I have to use your Relayer?**
No. `withdraw(unlockAddress, to, v, r, s)` has no `msg.sender` restriction, so any EOA can submit it. You can use ours (the default), run your own, or have the user's App submit directly through another wallet (as long as the user or you covers the gas).

**Q: Does collecting funds through your Relayer cost anything?**
By default we cover the gas for you, currently free of charge — this is early-stage promotion, and a fair-use policy may be added later. If your distribution volume is large or you have SLA requirements, we recommend self-hosting the Relayer. See the [open-source repo](https://github.com/hongbao-labs/contracts) for details.

**Q: Can I let users pay their own gas?**
The contract layer places no restriction on who submits (there is no `msg.sender` check on `withdraw`). The official Hongbao App goes through the Relayer to sponsor gas by default — that is the standard cardholder experience. If your team builds a client on top of the contract ABI, you can have users connect their own wallet and pay gas (see the [open-source repo](https://github.com/hongbao-labs/contracts)), but the experience is noticeably worse and it requires users to hold native tokens in their wallet.

## Loss and After-Sales

**Q: What if cards arrive damaged?**
Handled per the DOA policy in your partnership contract (case by case). Please spot-check a sample on receipt.

**Q: A user lost their card. Can the funds inside be recovered?**
Not before expiry. The card is the private key, so losing the card means losing the private key, and the assets can no longer be moved. But after expiry you can `withdrawExpired` to reclaim the assets and issue the user a new card. This is our recommended lost-card SOP: the user reports the loss → you log it → wait for the expiry reclaim → reissue a new card and deposit again.

**Q: Can you provide device serial numbers or card anti-counterfeiting traceability?**
The device's ETH address is its unique serial number (one per card). We don't provide a separate anti-counterfeiting or tracking service — if you need one, you can build a SKU system on top of the ETH addresses. For custom solutions, reach out through business contact ([contact.md](../contact.md)).

**Q: What is the card's battery life?**
Roughly 3 years by design (essentially no drain in deep sleep; very low consumption in active use). The battery is not replaceable.

## Legal and Compliance

**Q: Whose responsibility is compliance?**
Yours. What we provide is a trustless hardware-and-contract toolkit; the act of distribution (who you sent how much to) is carried out by you, and the related tax, KYC, AML, and regional compliance obligations fall to you. The contract charges no fees and keeps no admin key: Hongbao never custodies or touches your funds — the whole flow is on-chain, and the funds stay under your control from start to finish.

**Q: Do you retain records of users' claims?**
Our Relayer keeps minimal operational logs (for abuse prevention and troubleshooting), but it retains no user information beyond what is necessary. If these logs concern you, self-host the Relayer.

**Q: If Hongbao's service has problems (temporary server downtime / Relayer outage), can the cards I've already distributed still be claimed?**
At the asset level, 100% safe. The contract is deployed on a public chain, has no owner, and depends on no centralized service; the assets are guaranteed by the protocol itself and are completely decoupled from our operational status.

At the claim level: claims normally go through the official Hongbao Web / App, and short outages recover automatically. In an extreme case, the contract ABI is public, the BLE interface spec is public, and the CLI tool is open-source, so anyone can submit a claim transaction through the public interfaces. Those with the technical skills can build their own client; those who can't can rely on our technical support team to step in at any time. Under no circumstances will the assets be permanently stuck in the contract.

## Product Positioning

**Q: How does this compare to hardware wallets (like the common multi-use signing hardware wallets on the market)?**
Completely different products. A hardware wallet is a multi-use signing device sold to end users for long-term private key management, with an ongoing relationship to the user. Hongbao is a one-time signing device plus an on-chain distribution protocol, sold to asset distributors (project teams, exchanges, enterprises); the card is spent once it reaches the recipient and ownership transfers — it is not the user's "wallet."

If you want to buy an employee a long-term wallet as a gift, buy a hardware wallet. If you want to precisely distribute an asset to 1,000 users and complete their onboarding, use Hongbao.

**Q: How does this compare to the crypto gift card products on the market?**
They are custodial: the platform collects the user's money first, and the user redeems the card against a platform balance. Hongbao is a protocol with a completely decoupled fund flow — the project team locks the assets into the contract itself, and we never collect a cent, never disburse a cent, and never hold any balance. Architecturally, they are simply not the same kind of product.

## More Questions?

Business partnerships and purchasing: hello@hongbao.digital
Technical questions: dev@hongbao.digital
