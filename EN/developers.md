# Developers

Hongbao's on-chain layer is **fully open**. The standard contract and signature spec are the foundation of Hongbao as an ecosystem protocol — wallets, exchanges, and dapps can integrate or extend against them, and anyone can deploy, fork, or audit the contracts.

> **Source code:** [github.com/hongbao-labs/contracts](https://github.com/hongbao-labs/contracts) — interfaces, contracts, security model, and design rationale.

---

## What's open vs. provided

| Layer | Open source | Provided by Hongbao |
|---|---|---|
| Standard contract + signature spec | ✅ deploy / fork / extend | — |
| BLE interface spec | ✅ | — |
| CLI tools | ✅ | — |
| Hardware (the card) | — | Designed, manufactured, and sold by Hongbao |
| Official client (Web / Android / iOS) | — | Provided by Hongbao |

Hardware and the official client are unified so the secure-element supply chain stays trusted, firmware audits stay consistent, and the cardholder experience stays standard. The on-chain layer is where you build.

## Architecture in one minute

1. **Factory** deploys a **Pool** (once per chain + asset).
2. The issuer locks assets into the Pool against each card's on-chain address (`deposit` / `batchDeposit`, or `batchDepositWithTasks` for task cards).
3. The cardholder signs a payload — containing their chosen recipient address — with the card's sealed key.
4. Anyone (a **Relayer**, the user, or you) submits `withdraw(unlockAddress, to, v, r, s)`. The Pool verifies the signature and releases funds to `to`. There is **no `msg.sender` restriction** — any EOA can submit.
5. After the lock period, the issuer can `withdrawExpired` to reclaim unclaimed funds.

The card itself is chain-agnostic — it does ECDSA over a 32-byte digest and doesn't care which chain that digest belongs to. **To support a new chain, deploy a corresponding "lock → verify signature → release" contract there; the card works as-is.**

## Task cards

The value splits into a basic amount plus up to 255 task amounts. The first signature claims the basic amount and binds the recipient address; each task amount is released by submitting its **preimage**. A preimage is bound to a specific (chain, Pool, card, task slot) and funds are forced to the bound address — a leaked preimage cannot be hijacked or replayed. Mechanics: `batchDepositWithTasks`, `claimTask`. See the repo for the full spec.

## Events to monitor

| Action | Event |
|---|---|
| ERC20 claim | `Withdrawn(unlockAddress, to, amount)` |
| Task unlock | `TaskClaimed(unlockAddress, taskIdx, to, amount)` |
| ERC721 claim | `WithdrawNFT(unlockAddress, to, tokenId)` |

## Building a custom client

You don't have to use the official Web Dapp or Relayer. Teams can interact directly at the contract layer — deploy your own Factory/Pool, run your own Relayer (or let users pay their own gas, since `withdraw` has no sender restriction), and build a custom issuer or cardholder client against the contract ABI and BLE spec. Start from the [open-source repo](https://github.com/hongbao-labs/contracts).

## Supported chains & assets

- **Live today:** Ethereum and all EVM chains (ERC20 + ERC721 standard contracts).
- **Opened on request:** Bitcoin, Solana, Sui, Aptos, Cosmos, and other secp256k1 ecosystems.
- Native coins (ETH, BNB, …) aren't supported by the current standard contract; wrap them (e.g. WETH) first. ERC1155 / non-standard / custom contracts are available as custom orders.

Per-network deployed contract addresses are published in the repo and available via dev@hongbao.digital.

## Security & disclosure

The contracts have no owner, admin, pause, or upgrade path — see the [security model](security.md) for the full picture. Found an issue? Email **security@hongbao.digital** and allow a reasonable disclosure window.

## Contact

Technical questions and integration support: **dev@hongbao.digital** (see [contact.md](contact.md)).
