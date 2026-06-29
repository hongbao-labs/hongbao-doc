# Issuer Overview

Hongbao is asset-distribution infrastructure built on "physical cards + public-chain contracts." It lets you hand value to a cardholder in a way that is secure, unambiguous, and verifiable.

Think of it as the on-chain version of the real-world red packet. It's not a traditional gift card, nor just an airdrop tool — it's a verifiable, traceable, composable asset-transfer protocol: the issuer locks assets into a card, and the cardholder claims them with a signature once the card is in hand. The physical card decides "who claims, when, and whether it can be claimed again"; the on-chain contract governs "whether a claim is valid, whether it can be replayed, and whether the funds are safe."

The mechanism fits two kinds of scenarios:

- **One-to-one gifting**: send assets as a gift to customers, friends and family, KOLs, or event attendees.
- **Task-driven growth**: split assets into a basic amount and task amounts, so users keep unlocking rewards as they complete tasks.

If you've ever run an airdrop, a gift-card program, an offline event, or private-community growth, Hongbao is a natural fit — thanks to two built-in advantages:

1. **Stronger sybil resistance**: a bot can register countless wallets, but it can't get its hands on a pile of physical cards, and it can't complete your offline tasks for you.
2. **Stronger retention and traceability**: behind every card is a real person and a verifiable path of asset flow.

---

## Why Hongbao

### For the issuer

- **Simple and efficient**: you don't have to maintain your own key-management setup, transfer scripts, or task system. The cards and the client app handle all of that for you.
- **Secure and controllable**: assets are locked in public-chain contracts, the private key lives in hardware, and each card can sign only once. There's no need to whitelist users, and you never have to worry about your own private key being abused.
- **Configurable**: lock period, expiry rules, task thresholds, card-face content, asset types — all are negotiable business and product parameters.
- **Extensible**: beyond plain tokens, it supports NFTs, and new public chains can be integrated to fit your needs.

### For the cardholder

- **Low barrier**: once they have the card, they just connect the app and tap a button to claim.
- **Smooth experience**: any Bluetooth-capable device can complete a claim — no manual transaction signing, no need to understand complex on-chain operations.
- **Lower risk**: layered security means that even if an attacker takes the card, moving the assets away is extremely difficult — and once a card has signed, it's spent.

## How it works

A typical flow looks like this:

1. You deposit assets into a Pool on a public chain;
2. You hand the cards to your target users;
3. In the app, a user scans the code, connects the card, enters their own recipient address, and authorizes the signature;
4. The contract verifies the signature and transfers the assets to the user;
5. For a task card, the user keeps unlocking task amounts as they complete tasks.

See [flow.md](flow.md) for the full flow.

## What businesses it suits

Hongbao fits scenarios like these:

- **Community airdrops**: let real users claim, instead of letting sybil bots drain the pool.
- **Offline events**: load rewards onto physical cards and hand them to attendees on-site, boosting engagement.
- **KOL / community incentives**: reward those who drive social reach directly, without complex airdrop-distribution logic.
- **Brand gifts / customer rewards**: turn coupons, tokens, NFTs, or other assets into a physical card with a personal touch.

## What you can customize

- Card-face customization: the Hongbao logo stays; the rest is yours to design;
- Asset types: ERC20 / ERC721 / native coin supported (as needed);
- Task design: the rules for basic amount + task amounts are yours to define;
- Distribution: single cards, batches, or enterprise-scale procurement, all handled per order.

See [customization.md](customization.md) for details.

## Read on

- [flow.md](flow.md) — the full flow from order to payout
- [customization.md](customization.md) — customization of the card face, assets, and tasks
- [faq.md](faq.md) — common questions, covering contracts, legal, and operations
- [security.md](../security.md) — the security model and contract-level guarantees
