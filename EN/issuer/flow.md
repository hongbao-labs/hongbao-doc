# Issuance Flow

From "I want to distribute assets" to "users successfully claim them," an issuer goes through roughly the following steps.

## Flow Overview

```text
1. Place order
2. (Task cards) Design the campaign: basic amount + task list
3. We ship cards + JSON
4. Issuer receives and verifies shipment
5. Lock assets in one click via Web Dapp (+ write task commitments)
6. Distribute physical cards offline
7. Cardholder scans to claim the basic amount → completes tasks to unlock task amounts
8. (Optional) Reclaim unclaimed amounts after expiry in one click
```

Plain cards simply follow 1→3→4→5→6→7. Task cards add step 2 for campaign design and step 7 for task unlocking. If you'd rather bypass the Web Dapp and work directly at the contract layer or build your own client, your developer team can refer to the [open-source repo](https://github.com/hongbao-labs/contracts).

---

## 1. Place Order

Delivery is per order. Confirm the following when you order:

- Quantity
- Target chain: the protocol layer supports any chain with secp256k1 signature verification. The full EVM contract suite is available today; other chains are expanded per order.
- Asset type: current EVM contracts cover ERC20 + ERC721. ERC1155, native currency, and non-standard tokens are available as custom orders.
- Card-face customization: see [customization.md](customization.md)

Cards arrive with all factory operations already complete:

- secp256k1 private key generated randomly inside the chip (permanently sealed — unreadable by anyone)
- HMAC binding between MCU and secure element (prevents chip-swap attacks)
- SWD write-lock applied (prevents firmware extraction)
- Factory lock applied (prevents malicious instructions post-shipment)
- Signature / verification / authentication tests passed
- Deep sleep mode (zero power draw)

You do not need to perform any firmware-level operations.

## 2. We Ship Cards + JSON

Each batch ships with a JSON card list: an array with one entry per card, containing just two fields.

```json
[
  { "card_address": "0xAbc...", "nickname": "Card #1" },
  { "card_address": "0xDef...", "nickname": "Card #2" }
]
```

| Field | Required | Description |
|---|---|---|
| `card_address` | Yes | The card's on-chain address (`0x`-prefixed, 40-hex Ethereum address) — the secp256k1 address of the private key sealed in the chip |
| `nickname` | No | A card label, used only for display and search within the Web Dapp |

> Chain, asset contract, locked amount, expiry, and similar parameters are not part of this list — they are set in the Web Dapp at step 4 ("Lock"). Each card's claim QR code is derived from its `card_address` (`https://hongbao.digital/_c?ea=<first 6 chars of the address>`).

## 3. Verify Shipment

Once you receive the cards and JSON, we recommend running a card verification pass:

- Spot check (recommended): randomly pick a few cards, use the Hongbao-provided tool to read each card's on-chain address, and compare against the `card_address` in the JSON.
- Full verification: for batches with especially large asset values, you can run a full sweep.

> The verification tool is not yet publicly available. For verification needs, contact hello@hongbao.digital.

Once everything checks out, proceed to the next step.

## 4. Lock Assets in One Click via Web Dapp

Log in at hongbao.digital and connect your deposit wallet:

- Upload / select the batch JSON
- Select the asset contract (automatically validated against the JSON)
- Set the locked amount per card (ERC20) / select the tokenId list (ERC721)
- Set the expiry time (minimum 30 days)
- Click "Lock"

Everything below happens in a single background pass — you don't need to worry about any of it:

- (First time for this chain and asset) Deploy Factory
- Create Pool (once per asset + deposit wallet; reused if it already exists)
- ERC20 contract approve
- Automatically split into batches by the on-chain gas limit via batchDeposit
- Real-time status display for each transaction; failures can be retried

Once the process completes, all cards enter the "claimable" state.

### Task Cards: Lock + Write Task Commitments

If this batch is task cards, the lock UI adds two steps:

- Set the basic amount + task list: each task maps to an amount and a completion condition (follow / retweet / join group / on-chain activity verification, etc., up to 255 tasks)
- Generate task commitments: the Web Dapp generates a preimage `n` for each task on each card and writes the corresponding hash into the contract (`batchDepositWithTasks`). You control the preimages — they can be hosted on Hongbao Web or exported to your own backend.

> Total task card amount = basic amount + Σ task amounts. Task slots are immutable after creation; top-ups go to the basic amount only. See the [open-source repo](https://github.com/hongbao-labs/contracts) for the full mechanism.

## 5. Distribute

Ship or hand the physical cards to your users. How you deliver them is up to you — tuck one into a greeting card, hand them out at an event, or send them by mail.

When you distribute the cards, we recommend also telling users:

- This is a Hongbao card; just scan to claim
- The expiry date (so they don't miss the window)

The QR code points by default to `https://hongbao.digital/...` — scanning it takes users straight to the official Hongbao claim entry point (the web UI adapts automatically, and opens the Hongbao App first if installed), with no extra guidance needed. The cardholder entry point is maintained entirely by Hongbao; issuers do not separately host or replace the frontend.

## 6. Cardholder Claim

See the [Cardholder Claim Guide](../receiver/claim.md).

On-chain transactions are submitted via the Hongbao official Relayer (default) or a self-hosted Relayer. You do not need to do anything during the claim flow.

Task card claims happen in two stages: the user first scans to claim the basic amount, which simultaneously binds the recipient address to the card; then, for each task they complete, they present the task credential `n` to unlock the corresponding amount, and the funds flow automatically to the bound address. You judge task completion (hosted on Hongbao or your own backend).

On-chain events can be monitored to update your own backend state and dashboard:

| Asset / Action | Event |
|---|---|
| ERC20 claim | `Withdrawn(unlockAddress, to, amount)` (task cards: amount = released basic amount) |
| Task unlock | `TaskClaimed(unlockAddress, taskIdx, to, amount)` |
| ERC721 claim | `WithdrawNFT(unlockAddress, to, tokenId)` |

## 7. Reclaim After Expiry (Optional)

Can be initiated as early as `lockTime` seconds after deposit. In the same Web Dapp interface:

- Select the batch
- Click "Withdraw Expired"

Behavior:

- Plain cards: already-claimed entries and entries with no deposit record are automatically skipped; unclaimed assets return to your deposit wallet.
- Task cards: the initiator reclaims all remaining funds in one click (unclaimed basic amounts + unlocked task amounts) and closes the cards; once closed, both claims and task unlocks for those cards stop.

---

## End-to-End Example

A DeFi project airdrops 100 USDT to each of 1,000 KOLs, with the assets held on Polygon:

```text
1. Order 1,000 cards (Polygon / USDT / co-branded card-face customization)
2. We ship cards + batch JSON
3. Issuer spot-reads 50 cards against their addresses, confirms a match
4. Log in to Web Dapp → upload JSON → 100 USDT/card → 60-day expiry → Lock
5. Ship cards to KOLs
6. KOLs scan to claim (Hongbao official entry point; gas covered by the default Relayer)
7. After 60 days, return to Web Dapp and Withdraw Expired in one click to reclaim the unclaimed portion
```

The on-chain interactions visible to the issuer: approve + several batchDeposit transactions + optional withdrawExpired afterward — all triggered through the Web Dapp, no scripting required.

### Task Card Example

A project distributes cards to 500 attendees at an in-person conference, 50 USDT per card, structured as "claim 10 on arrival + 10 each for 4 completed tasks":

```text
1. Order 500 cards (Polygon / USDT / co-branded card face)
2. Design the campaign: basic amount 10 USDT + 4 tasks (follow on X / retweet / join TG group / on-chain interaction — 10 USDT each)
3. We ship cards + batch JSON
4. Spot-check the cards
5. Web Dapp → upload JSON → basic 10 + 4×10 tasks → 60-day expiry → Lock (write task commitments)
6. Hand out cards at the conference
7. Users scan to claim 10 USDT (recipient address bound) → complete tasks back at the hotel, unlocking each for +10
8. After 60 days, Withdraw Expired in one click to reclaim amounts from uncompleted tasks
```

The dashboard shows in real time: who claimed the basic amount, which tasks each user completed, and their on-chain profile.

## Notes

- Batch size: the Web Dapp automatically splits batches by the target chain's gas limit — no manual batch size calculation needed.
- NFT recipient address validation: the contract layer does not restrict recipient address type, but the Hongbao official App validates that the address can receive ERC721 before the cardholder signs, to prevent NFTs from being ruined by transfer to an address that does not implement `onERC721Received`.
- Minimum expiry of 30 days: a hardcoded constant in the contract.
- Asset scope: each Pool is bound to a single asset; multiple assets mean multiple Pools, managed separately within the Web Dapp.
- **Cross-chain deposits**: each chain is fully independent. Cards are in secp256k1 address format, so the same address exists across EVM chains, but a card can only sign once — a single card can only be locked on one chain and claimed on one chain. Do not lock assets to the same card address on multiple chains simultaneously; otherwise, whichever chain the user claims on, the assets on the other chains become permanently unrecoverable (the only recourse is waiting for expiry to reclaim).
