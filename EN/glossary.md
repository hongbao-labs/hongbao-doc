# Glossary

Plain-language definitions of the terms used across these docs.

## Core concepts

- **Hongbao card** — a physical card with a secure chip inside that holds a single on-chain address. Whoever holds the card controls the assets at that address. It signs exactly once, then retires.
- **Bearer object** — something whose holder is its owner, like cash. A Hongbao card is a bearer object: possession is control.
- **Plain card** — a card whose single scan-and-press claims the full amount.
- **Task card** — a card whose value is split into a *basic amount* (claimed on the first press) and *task amounts* (unlocked one by one as the cardholder completes tasks).
- **Basic amount** — the portion of a task card claimed immediately with the first signature, which also locks the recipient address.
- **Task amount** — a portion of a task card released when a specific task is completed; it can only go to the already-locked recipient address.
- **Issuer** — the party that loads assets onto cards and distributes them (a project, exchange, company, or retailer).
- **Cardholder / recipient** — the person who holds a card and claims its assets.
- **Claim** — the act of scanning, pressing the button, and signing to move a card's assets into a wallet you control.
- **Expiry / reclaim** — every deposit has a lock period (minimum 30 days). After it passes, the issuer can reclaim any unclaimed funds.

## Hardware

- **Secure element** — a tamper-resistant chip that generates and seals the private key so it can never be exported.
- **TRNG (True Random Number Generator)** — the in-chip hardware source of randomness used to generate the private key.
- **BLE (Bluetooth Low Energy)** — the wireless link between the app and the card.
- **MCU** — the card's microcontroller, cryptographically bound to the secure element to prevent chip-swap attacks.

## On-chain

- **secp256k1** — the elliptic curve used for signatures. It is the de facto universal curve in crypto, which is why one card can target almost any major chain.
- **EVM (Ethereum Virtual Machine)** — the execution environment shared by Ethereum and chains like BSC, Polygon, Arbitrum, Base, and Optimism. Hongbao's first production integration.
- **ERC20** — the standard for fungible tokens (e.g. USDT, USDC, project tokens).
- **ERC721** — the standard for non-fungible tokens (NFTs).
- **EOA (Externally Owned Account)** — an ordinary wallet address (as opposed to a contract). Any EOA can submit a claim transaction.
- **Standard contract** — the open-source on-chain custody layer that holds locked assets, verifies the card's signature, and releases funds.
- **Factory** — the contract that deploys Pools. Deployed once per chain + asset.
- **Pool** — an immutable contract instance bound to a single asset that custodies deposits and handles claims for a set of cards.
- **Relayer** — a non-trusted role that pays gas to submit a claim transaction on the cardholder's behalf. Any EOA can serve; it cannot alter the recipient or seize funds.
- **Preimage** — the secret value that unlocks one task amount. Bound to a specific (chain, Pool, card, task slot); a leaked preimage still pays only the locked address.

## Growth & risk

- **Sybil / sybil farming** — one actor controlling many wallets to capture rewards meant for distinct people. A physical card defeats this: you can't batch-hold thousands of cards.
- **Airdrop** — distributing tokens to many wallets, traditionally vulnerable to sybil farming.
- **Read/write separation** — being able to *verify* a card's balance (read) without being able to *claim* it (write) until a condition is met (e.g. payment, or removing packaging).

## Operations

- **DOA (Dead on Arrival)** — a card that arrives non-functional; handled per the commercial contract's DOA policy.
- **Onboarding** — guiding a new user to set up a wallet/exchange account so they have an address to receive into.

> Don't see a term? Check the [security model](security.md), the [developer page](developers.md), or email dev@hongbao.digital.
