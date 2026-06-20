---
title: Cardholder FAQ
description: Frequently asked questions for Hongbao cardholders
draft: false
---

## Security

**Q: Can the private key on my card be stolen?**
The private key is generated randomly inside the chip at the time of manufacture and never leaves it. The card manufacturer, the card issuer, Hongbao, and you yourself have no way to read it out. The chip is designed with protections against side-channel attacks and physical disassembly.

**Q: Could someone secretly connect to my card via Bluetooth nearby and transfer my funds?**
No. It takes two physical button presses: hold for 3 seconds to confirm the connection, then hold again for 10 seconds to authorize the signature. Nobody can press the button for you over the air.

**Q: Can the card issuer or anyone in the middle change my receiving address?**
No. The receiving address you enter is **written into the signed data itself** — if the address is changed, the signature becomes invalid and the smart contract will reject it. Nobody (including Hongbao, the card issuer, or the relay that submits the transaction) can redirect your assets.

**Q: Can the assets on my card be double-spent?**
No. The card's firmware is hard-coded to allow signing only once. The smart contract also records a "claimed" status, and any second submission will be rejected. These two layers are completely independent of each other.

**Q: What if Hongbao's service is temporarily unavailable — can I still claim my card?**
**Your assets are 100% safe.** The assets are locked in a public smart contract that has **no owner, no pause switch, and no upgrade mechanism**. As long as the blockchain is running and you have your card, the assets are yours.

**For claiming:** under normal conditions you use the Hongbao website or App, and brief outages will recover automatically. There is always a fallback path — the contract ABI, BLE interface, and CLI tools are fully open-source, so anyone technical can claim directly using the public interfaces. If you're not technical, our support team is always here to help. **In any situation, your assets will never be permanently stuck in the contract.**

## Task cards

**Q: What is a task card, and how is it different from a plain card?**
With a plain card, you scan, press the button once, and the full amount goes directly to your address. A task card splits the amount into two parts: scanning and pressing the button gives you the **basic amount** right away, and the rest is unlocked by **completing tasks** (such as following an account, sharing a post, joining a group, on-chain activity verification, checking in at a location, etc.). Once you connect the App to the card, it will tell you which type you have and what tasks are available.

**Q: Do I need to use the card again to unlock each task?**
No. When you pressed the button the first time, your receiving address was locked to the card. From then on, each time you complete a task, the corresponding amount is sent automatically to that address — everything happens in the App, and you don't need to touch the card again.

**Q: Is the task amount safe? Could someone else claim it on my behalf?**
No. The funds unlocked by tasks **can only be sent to the address you locked in with your first signature**. Even if someone else gets hold of your task preimage and submits it, the funds will still go to your address — no one else can take them.

**Q: What happens if I don't finish all the tasks?**
Any task amounts you haven't claimed by the expiry date will be reclaimed by the card issuer — **this does not affect what you've already received**. We recommend completing your tasks before the expiry date.

**Q: Do I have to link my social accounts to do tasks?**
Completing tasks requires you to link the relevant accounts through the App (for example, to verify that you followed a particular account on X). If you only want to claim the basic amount and skip the tasks, you don't need to link any real social identity. See the user agreement for details on what data is used.

## Using your card

**Q: Do I need to pay gas to claim?**
No, you don't pay anything. The card issuer covers gas by default through Hongbao's or their own relay. Even if no relay is available, anyone who has gas (including yourself using another wallet) can submit your signed transaction on-chain.

**Q: I don't have a crypto wallet — can I still claim?**
Yes. The App will guide you through setting up an account with a mainstream crypto wallet or exchange to get a receiving address, then bring you back to Hongbao to complete the claim.

Your wallet private key or exchange account is always managed by the respective service provider — Hongbao **does not create, custody, or access** your private key. We only guide you through the onboarding.

**Q: Can I claim assets directly to a centralized exchange deposit address?**
It depends on the asset type:

- **ERC20 tokens** (USDT, USDC, etc.): Usually yes — the contract's withdraw call uses `token.transfer`, which most exchanges can recognize.
- **ERC721 NFTs**: **Do not do this** — most exchange deposit addresses do not implement `onERC721Received`, so the signature will be consumed but the NFT will not transfer, and the card will become unusable.

If you came through the Hongbao App's onboarding flow, the App will automatically check address compatibility based on the asset type on your card — just follow the prompts. If you're pasting an exchange address manually, we recommend using a self-custody wallet instead; only use an exchange address if you're sure the asset is ERC20 and the exchange supports contract-initiated transfers.

**Q: Can I split the assets on one card across multiple addresses?**
No. The card can only be signed once, and you must specify a single receiving address at that time.

**Q: Once I've claimed the card, can I add more funds to it?**
No. Cards are **single-use by design** — once signed, the firmware rejects any further signing, and the card cannot be used again physically.

**Q: How long before the card expires?**
The expiry date is set by the card issuer, with a minimum of 30 days. You can claim any time before expiry. After expiry, the card issuer may reclaim the remaining assets (depending on asset type — see below). Connect the card in the App to see the exact expiry timestamp.

**Q: Can I still claim after the card has expired?**
It depends on whether the card issuer has already reclaimed the assets.
- Issuer has not reclaimed → you can still claim normally (the contract does not automatically move expired assets; it only allows the issuer to reclaim).
- Issuer has already reclaimed → there is nothing left to claim.

We recommend claiming well before the expiry date.

## Lost or damaged

**Q: What if I lose my card?**
The card is effectively the private key itself — losing the card means losing access to the funds inside. That said, **whoever finds the card may not be able to claim immediately** — they would need to know it's a Hongbao card, install the App, connect to it, and hold the button for 13 seconds. But if they're willing to put in the effort, it is technically possible for them to claim.

If you notice early, contact the card issuer — they can wait for the expiry date and then reclaim the assets (so the funds won't end up with whoever found the card), and issue you a replacement card. They cannot intervene before the expiry.

**Q: My card got wet or physically damaged — are the assets locked forever?**
If the card is damaged, the private key is inaccessible and the on-chain assets cannot be signed out. However, the card issuer can reclaim the assets after expiry, so they won't be stuck in the contract permanently. Please contact the card issuer to request a replacement card.

**Q: What if the battery runs out?**
New cards have a shelf life of approximately 3 years. If the battery fails before the expiry date, the process is the same as above — contact the card issuer, wait for expiry, and they can reclaim and reissue. The card battery **is not replaceable**.

## Supported chains & assets

**Q: Which blockchains are supported?**
**At the protocol level:** any chain that uses the secp256k1 elliptic curve for signature verification. This is the de facto universal curve in the crypto world, covering virtually all major public blockchains (Bitcoin, Ethereum and all EVM chains, Solana, Sui, Aptos, Tron, Cosmos ecosystem, Litecoin / Dogecoin / BCH, and more).

EVM is simply our first production integration:

- **Currently developed and live:** Ethereum and all EVM-compatible chains (BSC, Polygon, Arbitrum, Base, Optimism, etc.).
- **Available on request by card issuers:** Bitcoin, Solana, Sui, Aptos, Cosmos, and others.

Which chain a specific card uses is determined by the card issuer; the App will display this when connected.

**Q: Which assets are supported?**
**At the protocol level:** any asset type that supports a "standard transfer" — fungible tokens, non-fungible tokens, and custom project contracts are all supported.

**Currently developed EVM contracts cover:**

- ERC20 tokens (stablecoins like USDT / USDC, major tokens, project-specific ERC20s, etc.): ✅
- ERC721 NFTs: ✅
- Native coins (ETH, BNB, etc.): not supported in the current standard contract; card issuers typically wrap them as wrapped tokens (e.g., WETH) before use.
- ERC1155 / non-standard tokens / custom project contracts: available as custom orders.

## Still have questions?

Reach out to the card issuer — they know their campaign best. For product or technical questions, see the [open-source repo](https://github.com/hongbao-labs/contracts) or email zwx@hongbao.digital.