# What is Hongbao

> **English** · [中文](../CN/README.md)

**Hongbao** is the pinyin for "红包" — a red packet.

In Chinese tradition, a hongbao is the red envelope that elders, family, and friends exchange at New Year, weddings, birthdays, and other occasions. It carries more than money — it carries affection and trust. **The moment it leaves your hand, the money belongs to whoever receives it, with no third party's approval required.** This is the simplest and most elegant way to give: a single gesture completes the transfer of ownership.

Hongbao brings this experience on-chain. The physical card is a "digital red packet": at the factory, the secure element inside generates a secp256k1 private key at random and then seals it permanently. The corresponding on-chain address holds the assets you deposit; once you hand the card to someone, control of those assets passes to the cardholder completely and irreversibly. **Hold the card, own the assets. Sign, and it's claimed.** This mechanism relies on no centralized account, activation code, or freeze authority — it runs on cryptography and public contracts.

---

## What Hongbao is

Hongbao is an **on-chain asset distribution protocol**. On the surface it looks like a physical gift card; underneath, it is a new paradigm for distributing assets.

It is built to hand assets to real users, KOLs, community members, and in-person participants through a "physical card + physical handover" model.

| Comparison | We are not | We are |
|---|---|---|
| Hardware wallets | a multi-signature device for end users to manage their own keys long-term | a one-time signing device for asset distributors — the card retires once it reaches the recipient and ownership has transferred |
| Crypto gift cards | a platform that custodies funds first, and can freeze or void them | **assets locked in a public contract** — no owner, no admin, no pause |
| Traditional airdrops | most of the allocation farmed by sybils — creating sell pressure and hard to claw back | physical filtering through a real card, enforced wallet registration, and unclaimed assets that stay reclaimable |

---

## Why it's different

Hongbao's core promise is simple:

- **Hold the card, own the assets**: the private key is generated at random inside the chip by a hardware TRNG and sealed permanently. Whoever holds the card owns the assets.
- **Sign, and it's claimed**: the recipient address is written into the signed content, so no intermediary can redirect it. The card signs exactly once, then physically retires.
- **Zero-trust by design**: the contract has no owner, no admin, and no upgrade path. Hongbao touches no assets and holds no private keys.

> The protocol runs self-sufficiently on public chains; the BLE interface, CLI tools, and contracts are all open, while the everyday experience is delivered through the official Web / App.

---

## Not just distribution — task incentives too

Beyond "hand it over and it lands," a Hongbao card can also be a task card: the assets are split into a basic amount and task amounts. After scanning, the user first claims the basic amount and locks in their recipient address; from there, each completed task unlocks its corresponding task amount.

That makes it a fit not just for airdrops, but for in-person events, conference giveaways, KOL gifts, community tasks, and user growth.

---

## What it's made of

Hongbao is built from four parts working together:

| Component | Role | Form |
|---|---|---|
| **Hardware signing device** (the Hongbao card) | a one-time secp256k1 signing device | designed, manufactured, and sold by Hongbao |
| **Client** (Android live; Web and iOS coming soon) | guides the cardholder through scanning, Bluetooth pairing, entering the address, and authorizing the signature | provided by Hongbao |
| **Standard contract** | the on-chain custody layer — releases funds after verifying the signature, and allows reclaim after expiry | open-source; deploy / fork / extend at will |
| **Relayer** | pays gas and submits the claim transaction | a non-trusted role — any EOA can serve |

**The on-chain layer is fully open** — wallets, exchanges, dapps, and projects can all integrate or extend against this spec.

---

## How it works

Each card contains a secure element that, at the factory, generates a secp256k1 private key at random inside the chip itself and seals it permanently. The on-chain address derived from that private key is printed as a QR code on the card face.

The issuer locks assets to this address, then sends the physical card to the recipient. The recipient scans the code, connects over Bluetooth, enters a recipient address, and presses the button on the card to authorize the signature — and the assets move to the chosen wallet. The card signs exactly once, then physically retires.

Task cards add one more layer of logic: that single signature both claims the basic amount and locks the recipient address onto the card. From then on, each time the user completes a task they unlock the corresponding amount, and the funds flow automatically to the locked address.

---

## Many chains, many assets

Hongbao's hardware layer is built on secp256k1 — crypto's de facto universal curve, covering nearly every major public chain:

| Chain | How it's compatible |
|---|---|
| **Bitcoin**, **Ethereum and all EVM chains**, **Tron**, the **Cosmos / Tendermint** family, **Litecoin / Dogecoin / BCH** | native secp256k1 account curve |
| **Solana** | native `secp256k1 program` precompile + `secp256k1_recover` syscall |
| **Sui** | native secp256k1 account curve support |
| **Aptos** | native secp256k1 ECDSA transaction authenticator |

Live today: the full EVM family (ERC20 + ERC721 standard contracts). Enabled on demand: Bitcoin, Solana, Sui, Aptos, Cosmos, and other ecosystems.

---

## Documentation map

| You are | Read |
|---|---|
| Someone who received a card | [receiver/](receiver/) — how to claim, why it's safe, what to do if you lose it |
| A project / company / retail user who wants to distribute assets with Hongbao | [issuer/](issuer/) — how it differs from gift cards, the workflow, and room for customization |
| Looking to understand the security model | [security.md](security.md) — safeguards, contract guarantees, audit status, and vulnerability disclosure |
| Hitting an unfamiliar term | [glossary.md](glossary.md) — plain-language definitions |

## Contact

See [contact.md](contact.md).
