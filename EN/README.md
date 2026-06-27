# Hongbao Overview

> **English** · [中文](../CN/README.md)

**Hongbao** (红包) is the Mandarin word for "red packet."

In Chinese tradition, a hongbao is the red envelope an elder hands a child at New Year, that guests give at weddings, that friends pass to one another on birthdays — an envelope with money inside that means far more than money. The red wards off bad luck and the envelope carries a blessing. **The moment it leaves your hand, the money belongs to whoever holds it — no third party's approval required.** It is the simplest, most elegant design humans ever built for "giving money": a single physical gesture transfers ownership, and the social meaning arrives together with the value.

The Hongbao protocol brings this paradigm on-chain. A physical card *is* a red packet — the secure element inside generates a secp256k1 private key at the factory and seals it permanently, and the corresponding on-chain address holds the assets you deposit. Hand the card to someone, and control of those assets transfers to them completely and irreversibly. **Hold the card, own the assets. Sign, and it's claimed.** No issuer account, no activation code, no freeze risk — every trust assumption collapses into cryptography and public contracts. **The protocol runs self-sufficiently on public chains, independent of any centralized service's status.**

That's why it's called Hongbao: **using cryptography to recreate the simplicity and certainty of the moment you hand someone a red packet.**

---

## What we are, and what we're not

Hongbao is an **on-chain asset distribution protocol** — it looks like a gift card, looks like a hardware wallet, but underneath it's **a new distribution paradigm**.

| | We are not | We are |
|---|---|---|
| vs. hardware wallets | a multi-sign device sold to end users to manage their own keys long-term | a **one-time signing device** sold to asset distributors — the card transfers ownership the moment it changes hands, then retires |
| vs. crypto gift cards | platform-custodied funds that can be frozen or voided | **assets locked in a public contract** — no owner, no admin, no pause |
| vs. traditional airdrops | most of the allocation farmed by sybils, dumped on-chain, unrecoverable | physical bot-filtering, forced wallet registration, unclaimed funds reclaimable |

**Three core promises:**

- **Hold the card, own the assets** — the private key is generated in-chip by a hardware TRNG and physically sealed; no one can read it out. Whoever holds the card owns the assets.
- **Sign, and it's claimed** — the recipient address is part of the signed content, so no intermediary can redirect it. The card signs exactly once, then physically retires — this is a design commitment, not a technical limitation: each card guarantees one definite transfer of ownership, unassignable like cash.
- **Zero-trust by design** — the contract has no owner, no admin, no upgrade path. Hongbao the company **touches no assets and holds no private keys**. Once the contract is deployed, we step out of the funds path entirely.

> **Self-sufficient protocol**: contracts are deployed on public chains, and the BLE interface and CLI tools are open-source — a card's claimability is **guaranteed by the protocol itself**, independent of any centralized service's operational status. For everyday use, our official Web/App handles everything; if anything goes wrong, our support team is on call.

---

## Not just distribution — incentivized tasks

Beyond "hand it over and it lands," a Hongbao card can also be a **task card**: the value is split into a *basic amount* + *task amounts*. The user scans to claim the basic amount and locks in their recipient address; then each completed task (follow on X, retweet, join a group, prove on-chain activity, etc.) unlocks one more task amount.

**A physical card is, by its nature, an anti-sybil identity credential** — bots can register ten thousand wallets, but they can't hold ten thousand physical cards, and they certainly can't show up in person to complete your tasks. That makes Hongbao an **offline growth tool**: real people + real engagement + user data you can actually keep. Full issuer-side details in [issuer/](issuer/).

---

## Protocol components

Hongbao is built from four components working together:

| Component | Role | Form |
|---|---|---|
| **Hardware signing device** (the card) | One-time secp256k1 signing device. The private key is generated in-chip and physically sealed | Designed, manufactured, and sold by Hongbao |
| **Client** (Android live; Web & iOS 🚧 coming soon) | Guides the cardholder through scanning, Bluetooth pairing, entering the recipient address, and authorizing the signature | Provided by Hongbao |
| **Standard contract** | The on-chain custody layer. Binds the card address and releases funds after verifying the signature; the issuer reclaims after expiry | Open-source; anyone can deploy / fork / extend |
| **Relayer** | Pays gas to submit the withdraw transaction | A non-trusted role — any EOA can serve |

**The on-chain layer (standard contract + signature spec) is fully open** — this is the foundation of Hongbao as an ecosystem protocol. Wallets, exchanges, and dapps can all integrate or extend against this spec.

**Hardware and the official client are provided by Hongbao** — unified hardware guarantees a trusted secure-element supply chain and consistent firmware audits; a unified client standardizes the cardholder experience and serves as Hongbao's integration point with ecosystem partners (wallets / exchanges / projects). Card-face customization (Hongbao logo retained, the rest open to the issuer) runs through a commercial process — see [issuer/](issuer/).

## How it works

Each card contains a tamper-resistant secure element that, at the factory, generates a secp256k1 private key in-chip and seals it permanently. **No party — including us — can read this key out.** The corresponding on-chain address is printed as a QR code on the card face.

The issuer locks assets to this address (held in escrow by the protocol contract) and mails the physical card to the recipient. The recipient scans, connects over Bluetooth, enters a recipient address, and presses the button on the card to authorize the signature — and the assets move to the recipient's chosen wallet. The card signs exactly once, then physically retires.

**Task cards add one layer**: that single signature claims the basic amount and locks the recipient address onto the card; thereafter, each time the user completes a task, they unlock the corresponding amount with a task preimage, and the funds flow automatically to the already-locked address. Even a leaked preimage can't be hijacked — the funds can only go to that locked address. Contract mechanics are in the open-source repo (https://github.com/hongbao-labs/contracts).

No link in the chain — the Bluetooth channel, the network path, the gas-paying relayer — **can** alter the recipient address, double-spend the assets, or seize them before expiry. These constraints are written into cryptography and public contracts, not anyone's verbal promise.

## One card, every chain

Hongbao's hardware layer is built on secp256k1 — crypto's de facto universal curve. That brings essentially every major chain into scope:

| Chain | Compatibility |
|---|---|
| **Bitcoin** (incl. Taproot), **Ethereum and all EVM chains**, **Tron**, **Cosmos / Tendermint** family, **Litecoin / Dogecoin / BCH** | Native secp256k1 account curve |
| **Solana** | Native `secp256k1 program` precompile + `secp256k1_recover` syscall |
| **Sui** | Native secp256k1 account curve support (alongside Ed25519) |
| **Aptos** | Native secp256k1 ECDSA transaction authenticator since AIP-49 + stdlib verification module |

The card itself is chain-agnostic — it does ECDSA over a 32-byte digest and doesn't care which chain's transaction that digest represents. To support a new chain, you only deploy a corresponding "lock → verify signature → release" contract there. The card works as-is.

**Live today**: the full EVM family (ERC20 + ERC721 standard contracts).
**Opened on demand**: Bitcoin, Solana, Sui, Aptos, Cosmos, and other ecosystems.

## Roadmap

Hongbao rolls out in two phases:

- **Phase 1 — Business** *(current focus)*. Selling to asset distributors — Web3 projects, L1/L2 foundations, exchanges, and wallets. The growth-and-acquisition scenarios come first: sybil-proof airdrops, conferences and IRL events, quests, ambassador kits.
- **Phase 2 — Consumer**. Bringing Hongbao to everyday people: retail crypto gift cards on the shelf at the grocery and convenience store, digital red packets for holidays and occasions, and individual gifting. Retail is not open yet — [join the waitlist](contact.md).

See the full [use-case library](use-cases.md) for where each scenario fits.

## Documentation map

| You are | Read |
|---|---|
| Wondering where Hongbao fits | [use-cases.md](use-cases.md) — 24 scenarios where a physical card beats a bare wallet address |
| Someone who received a card | [receiver/](receiver/) — how to claim, why it's safe, what to do if you lose it |
| A project / company / retail user who wants to distribute assets with Hongbao | [issuer/](issuer/) — how it differs from gift cards, the workflow, customization options |
| Wanting to understand the security model | [security.md](security.md) — safeguards, contract guarantees, audit status, disclosure |
| A developer building on the protocol | [developers.md](developers.md) — architecture, interfaces, events, and the open-source repo |
| Hitting an unfamiliar term | [glossary.md](glossary.md) — plain-language definitions |

## Contact

See [contact.md](contact.md).
