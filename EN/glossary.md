# Glossary

Plain-language definitions of the terms you'll come across in these docs, to help you get up to speed on Hongbao's product and mechanics.

## Core concepts

- **Hongbao card** — a physical card with a secure chip inside, holding a single on-chain address. Whoever holds the card controls the assets at that address. The card signs exactly once, then retires.
- **Bearer object** — like cash, whoever holds it owns it. A Hongbao card is exactly this kind of instrument: to hold it is to control it.
- **Plain card** — a card that claims its full amount with a single scan and one press of the button.
- **Task card** — a card whose value is split into a *basic amount* and *task amounts*. You claim the basic amount first, then unlock more by completing tasks.
- **Basic amount** — the portion of a task card claimed with its first signature; that same signature locks the recipient address.
- **Task amount** — the portion released after a given task is completed; it can only be paid to the already-locked recipient address.
- **Issuer** — the party that loads assets onto cards and hands them out (a project, exchange, company, or retailer).
- **Cardholder / recipient** — the person who holds a card and claims the assets on it.
- **Claim** — the act of scanning, pressing, and signing to move a card's assets into a wallet you control.
- **Expiry / reclaim** — every deposit carries a lock period (30 days minimum). Once it passes, the issuer can reclaim any unclaimed funds.

## Hardware & security

- **Secure element** — a tamper-resistant chip where the private key is generated and sealed for good, never to be exported.
- **TRNG (True Random Number Generator)** — the in-chip hardware source of randomness used to generate the private key.
- **BLE (Bluetooth Low Energy)** — the wireless link between the app and the card.
- **MCU** — the card's microcontroller, cryptographically bound to the secure element to prevent chip-swap attacks.

## On-chain & contracts

- **secp256k1** — the elliptic curve used for signatures. It is the de facto universal curve in crypto, which is why a single card can target almost any major chain.
- **EVM (Ethereum Virtual Machine)** — the execution environment shared by Ethereum and chains like BSC, Polygon, Arbitrum, Base, and Optimism; Hongbao's first production integration.
- **ERC20** — the standard for fungible tokens (e.g. USDT, USDC, project tokens).
- **ERC721** — the standard for non-fungible tokens (NFTs).
- **EOA (Externally Owned Account)** — an ordinary wallet address (as opposed to a contract). Any EOA can submit a claim transaction.
- **Standard contract** — the open-source on-chain custody layer that holds locked assets, verifies the card's signature, and releases funds.
- **Factory** — the contract that deploys Pools. Deployed once per chain + asset.
- **Pool** — an immutable contract instance bound to a single asset that custodies deposits and handles claims for a batch of cards.
- **Relayer** — an untrusted role that pays gas and submits the claim transaction on the cardholder's behalf. Any EOA can play it; it cannot alter the recipient address or seize the funds.
- **Preimage** — the secret value that unlocks one task amount. Bound to a specific (chain, Pool, card, task slot); even if it leaks, the money still pays only the locked address.

## Growth & risk

- **Sybil / sybil farm** — one actor controlling a swarm of wallets to grab rewards meant for distinct, real people. A physical card defeats this: no one can batch-hold tens of thousands of cards.
- **Airdrop** — distributing tokens to many wallets, traditionally easy prey for sybil farms.
- **Read/write separation** — being able to *verify* a card's balance (read) but unable to *claim* it (write) until a condition is met (e.g. payment, or removing the packaging).

## Operations & partnerships

- **DOA (Dead on Arrival)** — a card that's unusable the moment it arrives, handled per the DOA policy in the commercial contract.
- **Onboarding** — guiding a new user through setting up a wallet or exchange account so they have an address to receive into.

> Don't see a term? Check the [security model](security.md) or the [open-source repo](https://github.com/hongbao-labs/contracts), or email dev@hongbao.digital.
