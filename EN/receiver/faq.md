# FAQ

## Security & private keys

**Q: Can the private key on my card be stolen?**
The private key is generated randomly inside the chip during manufacture and never leaves it. Nobody can read it — not the card manufacturer, the issuer, Hongbao, or even you. The secure element is also designed to resist side-channel attacks and physical tampering.

**Q: Could someone secretly connect to my card over Bluetooth nearby and move my funds?**
No. The card has two physical button defenses: connecting takes a 3-second press to confirm, and signing takes a further 10-second press to authorize. An attacker can't make those button presses for you over the air.

**Q: Can the issuer or someone in the middle change my recipient address?**
No. The recipient address you enter is baked into the signed data itself. The moment that address is changed, the signature becomes invalid and the contract rejects it outright. Nobody — not us, not the issuer, not the relayer that helps submit the transaction — can redirect your assets to a different address.

**Q: Can the assets on my card be double-spent?**
No. The card's firmware is hard-coded to sign only once, and the contract also records a "claimed" status, so any second submission is rejected outright. These two safeguards are independent of each other, and you need both.

**Q: If Hongbao's service is temporarily unavailable, can I still claim my card?**
At the asset level, you're 100% safe. The assets are locked in a public smart contract with no owner, no pause switch, and no upgrade authority. As long as the chain is running and you have your card, the assets are yours.

At the claiming level: the flow normally goes through Hongbao's official website or App, and short-term glitches usually clear up on their own. Even in an extreme case, there's still a fallback — the contract ABI, BLE interface, and CLI tools are all open-source, so anyone technical can work through the public interfaces directly. If that's not you, you can reach out to our technical support team any time. Your assets won't get stuck in the contract.

## Task cards

**Q: What is a task card, and how is it different from a plain card?**
With a plain card, you scan, press the button once, and the full amount lands in your account. A task card splits the amount in two: scanning gives you the basic amount first, and the rest unlocks only as you complete tasks — for example following an account, reposting, joining a group, verifying on-chain activity, or checking in at a location. Once the App connects to the card, it tells you clearly which type of card it is and which tasks you can unlock.

**Q: Do I need to use the card again to unlock tasks?**
No. When you first pressed the button to sign, your recipient address was already locked onto the card. From then on, each time you complete a task the matching amount is sent to that address automatically. It all happens in the App — you never need to touch the card again.

**Q: Is the task amount safe? Could someone else claim it in my place?**
No. Funds unlocked by tasks only ever go to the address you locked in with your first signature. Even if someone else gets hold of your task preimage, submitting it just sends the funds to your address — they can't take them.

**Q: What happens if I don't finish the tasks?**
Once the expiry date passes, the issuer reclaims any unclaimed task amount, but this doesn't affect the part you've already claimed. We recommend finishing your tasks before then.

**Q: Do I have to link my social accounts to do tasks?**
To do tasks, you'll need to follow the App's prompts and link the relevant accounts — for example, to check whether you follow a particular X account. If you just want the basic amount and skip the tasks, there's no need to link any social identity. For the specific data involved, see the [privacy policy](https://hongbao.digital/#/privacy).

## Using your card

**Q: Do I need to pay gas to claim?**
You don't pay a thing. The issuer usually covers gas for you, through our relayer or their own. And even if the relayer is down, anyone with gas — including you, from another wallet — can take your signature and submit it on-chain.

**Q: I don't have a crypto wallet — can I still claim?**
Yes. The App will first walk you through signing up for a mainstream crypto wallet or exchange to get a recipient address, then bring you back to Hongbao to finish claiming.

Your wallet's private key and your exchange account always stay with that provider. Hongbao never creates, custodies, or touches your private key — it only guides you through the signup.

**Q: Can I claim assets to a centralized exchange deposit address?**
It depends on the asset type.

- Tokens (USDT, USDC, etc.): usually yes — most exchanges can receive them.
- NFTs: not recommended. Many exchange deposit addresses can't receive NFTs, so even after the signature is spent the NFT has nowhere to land — the card is used up and you get nothing.

If you came in through the Hongbao App's signup flow, the App checks address compatibility for you based on the card's asset type — just follow the prompts. If you're pasting an exchange address by hand, we recommend a self-custody wallet first, and only consider an exchange address for standard tokens (not NFTs).

**Q: Can I split the assets on one card across multiple addresses?**
No. The card can be signed only once, and you can name only a single recipient address when you sign.

**Q: I've claimed the card — can I top it up with more funds?**
No. The card is single-use by design: once it has signed, the firmware won't sign again, and physically it can't be used a second time either.

**Q: How long until the card expires?**
The issuer sets this, with a minimum of 30 days. You can claim any time before expiry; after that, the issuer can reclaim the assets on the card (depending on the asset type — see below). Connect the card in the App to see the exact expiry timestamp.

**Q: Can I still claim after it has expired?**
It depends on whether the issuer has already reclaimed it.
- If it hasn't been reclaimed yet, you can still claim normally. The contract doesn't move expired assets on its own; it only lets the issuer reclaim them.
- If it has already been reclaimed, there's nothing left on the card to claim.

We recommend claiming as soon as you can, before expiry.

## Lost or damaged

**Q: What if I lose my card?**
The card is essentially the private key itself, so losing it is like losing the cash inside. That said, whoever finds it may not manage to claim it: they'd have to know it's a Hongbao card, install the right App, connect to the card, and then hold the button for 13 seconds. If they're determined enough, though, claiming the assets is in theory still possible.

If you notice early, contact the issuer as soon as you can. The issuer can reclaim the assets after expiry — so the finder can't claim them — and then send you a replacement. Before expiry, though, there's nothing they can do.

**Q: My card got wet or was crushed — are the assets locked forever?**
Yes. A damaged card means the private key is unusable, so the on-chain assets can no longer be signed out. But the issuer can reclaim them after expiry, so they won't be stuck in the contract forever. Please contact the issuer to request a replacement.

**Q: What if the battery dies?**
A new card has a shelf life of about 3 years. If the battery fails before expiry, it's handled the same way as above: contact the issuer, and once they reclaim at expiry they'll send a replacement. The card's battery can't be replaced.

## Supported chains & assets

**Q: Which chains are supported?**
At the protocol level, any chain that uses the secp256k1 elliptic curve for signature verification. It's the de facto universal curve in crypto, so this covers almost all major public chains, including Bitcoin, Ethereum and all EVM chains, Solana, Sui, Aptos, Tron, the Cosmos ecosystem, Litecoin, Dogecoin, and BCH.

EVM is our first live example:

- Already developed and live: Ethereum and all EVM-derived chains, including BSC, Polygon, Arbitrum, Base, and Optimism.
- Expanded per order, based on issuer demand: Bitcoin, Solana, Sui, Aptos, Cosmos, and more.

The issuer decides which chain a given card uses, and the App shows it once you connect the card.

**Q: Which assets are supported?**
At the protocol level, a card can carry any asset that supports a "standard transfer" — including fungible tokens, non-fungible tokens, and a project's own custom contracts.

The EVM contracts developed so far cover:

- ERC20 tokens (such as stablecoins USDT / USDC, major tokens, a project's own ERC20, etc.): ✅
- ERC721 NFTs: ✅
- Native coins (such as ETH, BNB, etc.): not supported by the current standard contract; issuers usually wrap them into a wrapped token (such as WETH) first.
- ERC1155, non-standard tokens, and a project's own contracts: custom-built per order.

## Still have questions?

Reach out to the issuer — they know their own campaign best. For product or technical questions, check the [open-source repo](https://github.com/hongbao-labs/contracts) or email dev@hongbao.digital.
