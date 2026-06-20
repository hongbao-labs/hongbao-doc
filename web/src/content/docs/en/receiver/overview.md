---
title: You've Got a Hongbao Card
description: Introduction for cardholders — what a Hongbao card is and why it is safe
draft: false
---

### Scan, press, done — assets arrive in seconds.

The card holds on-chain assets — these could be stablecoins (USDT / USDC), popular tokens (ETH / BNB / SOL), NFTs, or any ERC20 / ERC721 or other tokens issued by the distributor. **What's inside and how much is decided by the issuer — the App will show you the details once it connects to your card.**

It is **not a voucher, not points, not a coupon** — the card represents the actual on-chain assets themselves. Scan the QR code, press the button on the card, and the assets land in your wallet in seconds. You don't need to pay any gas, and you don't need to know anything about blockchain — see the [Claim Guide](guide).

---

## What it is

Physically, it's about the size of a bank card, a little thicker than a credit card. Inside there's:

- An encrypted chip (where the private key lives)
- A button
- Two indicator lights (red and green)
- A one-time battery
- A QR code (printed on the front)

Conceptually, it's a **one-time on-chain asset credential** — like cash: **whoever holds it, owns what's inside**:

- **A private key lives inside the chip**, generated randomly by the chip itself at the factory and permanently sealed in hardware. We, the issuer, the manufacturer — nobody, including you — can ever export it.
- **That private key corresponds to assets locked on-chain** — the issuer locked the funds before the card ever reached you.
- **The card can only sign once.** When you press the button to authorize, the assets transfer to the wallet address you specify. This is a design choice, not just a technical limit: each card makes exactly one final transfer of ownership, so it **cannot be redirected, misused, or double-spent**.

## Plain card vs. task card

You'll receive one of two card types — the App will tell you which once it connects:

- **Plain card**: Scan, press once, the full amount arrives. Done.
- **Task card**: Scan, press once to claim the **basic amount** (which also locks in your receiving address); the remaining **task amount** unlocks as you **complete tasks** — such as following the project, sharing a post, joining a community, or verifying on-chain activity. Each completed task automatically sends the corresponding amount to your locked address. **You don't need the card again to complete tasks** — just follow the steps in the App. Any unclaimed portion is reclaimed by the issuer after the card expires.

## What you need

Nothing. Download the Hongbao App ([Android APK](https://github.com/hongbao-labs/HB_Android/releases/download/v1.0.4/hongbao-v1.0.4-release.apk)) and follow the steps.

**No crypto wallet or exchange account? No problem.** The App will walk you through setting one up with a mainstream crypto wallet or exchange so you get a receiving address, then bring you right back to finish claiming.

> Your wallet private key / account is always managed by the respective wallet or exchange — **Hongbao does not create, hold, or touch your private key**. We only guide you through registration and handle the distribution process.

## Why it's safe

Four independent safeguards. Any one of them is enough on its own to keep your assets from being lost:

1. **The private key never leaves the chip** — it has been sealed in hardware since the day it was manufactured. We have no backup and no way to recover it — that's an intentional design trade-off.
2. **You must press the physical button** — a wireless intercept goes nowhere: no button press, no signature.
3. **Your receiving address is baked into the signature** — the address you enter is part of what gets signed. Any attempt by a third party to change it invalidates the signature, and the on-chain contract will reject it outright.
4. **The card can only sign once** — a card that's been claimed becomes a keepsake. Even if someone got hold of it afterward, there's nothing left to take.

The smart contract holding your assets has no owner, no pause switch, and no upgrade mechanism — the issuer cannot take the funds back (unless the expiry time has passed). Even if a centralized service is temporarily unavailable, **your assets are always yours at the contract level**. The code is fully public and can be independently audited.

> Whatever questions or issues come up, our support team is always here to help. See [FAQ](faq.md).

## What's Next

→ [Claim Guide](guide) (three steps, about 1 minute)
→ [FAQ](faq.md) (lost card, expiry, security, supported chains, and more)