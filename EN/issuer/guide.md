# Issuer End-to-End Flow

From order to cardholder claim, the flow looks like this. **All contract interactions are integrated into the Hongbao Web Dapp — issuers do not need to write scripts, call contracts directly, or deploy a Factory / Pool**. Every on-chain action is triggered through the frontend UI.

```
1. Place order
2. (Task cards) Design the campaign: basic amount + task list
3. We ship cards + JSON
4. Issuer receives and verifies shipment
5. Lock assets in one click via Web Dapp (+ write task commitments)
6. Distribute physical cards
7. Cardholder scans to claim basic amount → completes tasks to unlock task amounts
8. (Optional) Reclaim unclaimed amounts after expiry in one click
```

> Plain cards follow steps 1→3→4→5→6→7 (full amount claimed in one action). Task cards add step 2 for campaign design and step 7 for task unlocking. Developer teams who want to bypass the Web Dapp and interact directly at the contract layer or build a custom client can refer to the open-source contract repo ([github.com/hongbao-labs/contracts](https://github.com/hongbao-labs/contracts)). This guide is written for issuer operations and BD teams, and describes the Web Dapp flow.

---

## 1. Place Order

Delivery is per order. Confirm at time of order:

- **Quantity**
- **Target chain**: The protocol layer supports any chain with secp256k1 signature verification. Full EVM contracts are available today; other chains are expanded per order.
- **Asset type**: Current EVM contracts cover ERC20 + ERC721. ERC1155, native currency, and non-standard tokens are available as custom orders.
- **Card customization**: See [customization.md](customization.md)

Cards arrive with all factory operations already complete:

- secp256k1 private key generated randomly inside the chip (permanently sealed — unreadable by anyone)
- HMAC binding between MCU and secure element (prevents chip-swap attacks)
- SWD write-lock applied (prevents firmware extraction)
- Factory lock applied (prevents malicious instructions post-shipment)
- Signature / verification / authentication tests passed
- Deep sleep mode (zero power draw)

You **do not** need to perform any firmware-level operations.

## 2. We Ship Cards + JSON

Each card batch ships with a JSON card list: an array with one entry per card, containing just two fields.

```json
[
  { "card_address": "0xAbc...", "nickname": "Card #1" },
  { "card_address": "0xDef...", "nickname": "Card #2" }
]
```

| Field | Required | Description |
|---|---|---|
| `card_address` | Yes | The card's on-chain address (`0x`-prefixed, 40-hex Ethereum address) — the secp256k1 address of the private key sealed in the chip |
| `nickname` | No | A display label, used only for presentation and search within the Web Dapp |

> Chain, asset contract, locked amount, and expiry are **not** part of this list — they are set in the Web Dapp at step 4 ("Lock"). Each card's claim QR code is derived from its `card_address` (`https://hongbao.digital/_c?ea=<first 6 chars of the address>`).

## 3. Verify Shipment

Upon receiving cards and JSON, run a verification pass:

- **Spot check** (recommended): Randomly select a few cards, use the Hongbao-provided tool to read each card's on-chain address, and compare against the `card_address` in the JSON.
- **Full verification**: For batches with especially large asset values, run a full sweep.

The read tool is the Hongbao CLI (the `hongbao` command-line tool). Connect a card to your computer with a USB-to-serial cable and run `hongbao pubkey` to read that card's Ethereum address, then compare it against the `card_address` in the list:

```bash
hongbao pubkey
# the "Ethereum address" in the output is the card's on-chain address
```

> The CLI talks to the card over USB serial (115200 baud; on macOS, install the CH34x serial driver first). To obtain the tool, contact Hongbao (see [contact.md](../contact.md)).

Once confirmed, proceed to the next step.

## 4. Lock Assets in One Click via Web Dapp

Log in to the Hongbao Web Dapp ([hongbao.digital](https://hongbao.digital), sign in with the Issuer role) and connect your deposit wallet:

[TBD: Screenshots + step-by-step instructions]
- Upload / select the batch JSON
- Select the asset contract (automatically validated against the JSON)
- Set the locked amount per card (ERC20) / select the tokenId list (ERC721)
- Set the expiry time (minimum 30 days)
- Click "Lock"

Everything below happens automatically in the background (no action required on your part):

- (First time for this chain and asset) Deploy Factory
- Create Pool (once per asset + deposit wallet combination; reused if already exists)
- ERC20 contract approve
- Automatically split into batches based on the target chain's gas limit via batchDeposit
- Real-time transaction status display; failures can be retried

Once the process completes, all cards enter the "claimable" state.

### Task Cards: Lock + Write Task Commitments

If this batch is task cards, the lock UI includes two additional steps:

- **Set basic amount + task list**: Each task has an amount and a completion condition (follow / retweet / join group / on-chain activity verification, etc., up to 255 tasks)
- **Generate task commitments**: The Web Dapp generates a preimage `n` for each task on each card and writes the corresponding hash into the contract (`batchDepositWithTasks`). You control the preimages — they can be hosted on Hongbao Web or exported to your own backend.

> Total task card amount = basic amount + Σ task amounts. Task slots are immutable after creation; top-ups go to the basic amount only. See the open-source contract repo ([github.com/hongbao-labs/contracts](https://github.com/hongbao-labs/contracts)) for full mechanism details.

## 5. Distribute

Ship or hand-deliver the physical cards to users. The logistics are entirely up to you — gift packaging, event distribution, postal mail, all work fine.

When distributing, we recommend also informing users:

- This is a Hongbao card; scan the QR code to claim
- The expiry date (so users don't miss the window)

The QR code points by default to `https://hongbao.digital/...` — scanning it goes directly to the Hongbao official claim page (responsive web UI; opens the Hongbao App first if installed). No additional user guidance is needed. The standardized cardholder claim entry point is a product guarantee — issuers do not separately host or replace the frontend.

## 6. Cardholder Claim

See the [Cardholder Claim Guide](../receiver/guide.md).

On-chain transactions are submitted via the Hongbao official Relayer (default) or a self-hosted Relayer. You do not need to do anything during the claim flow.

**Task card claims happen in two stages**: the user scans and taps to claim the basic amount (this simultaneously binds the recipient address to the card); then for each task completed, the user submits the preimage `n` to unlock the corresponding amount, which flows automatically to the bound address. Task completion verification is controlled by you (hosted on Hongbao Web or your own backend).

On-chain events can be monitored to update your backend state and dashboard:

| Asset / Action | Event |
|---|---|
| ERC20 claim | `Withdrawn(unlockAddress, to, amount)` (task cards: amount = released basic amount) |
| Task unlock | `TaskClaimed(unlockAddress, taskIdx, to, amount)` |
| ERC721 claim | `WithdrawNFT(unlockAddress, to, tokenId)` |

## 7. Reclaim Expired Funds (Optional)

Can be initiated as early as `lockTime` seconds after deposit. In the same Web Dapp interface:

[TBD: Screenshots + steps]
- Select the batch
- Click "Withdraw Expired"

Behavior:

- Plain cards: Already-claimed entries and entries with no deposit record are automatically skipped; unclaimed assets return to your deposit wallet.
- **Task cards**: The initiator reclaims all remaining funds in one click (unclaimed basic amounts + unlocked task amounts), and closes the cards. Once closed, both claims and task unlocks for those cards stop.

---

## End-to-End Example

A DeFi project airdropping 100 USDT to each of 1,000 KOLs, with assets held on Polygon:

```
1. Order 1,000 cards (Polygon / USDT / co-branded customization)
2. We ship cards + batch JSON
3. Issuer spot-checks 50 cards against addresses, confirms match
4. Log in to Web Dapp → upload JSON → 100 USDT/card → 60-day expiry → Lock
5. Ship cards to KOLs
6. KOLs scan to claim (Hongbao official claim page; gas covered by the default Relayer)
7. After 60 days, return to Web Dapp and Withdraw Expired to reclaim unclaimed amounts
```

The issuer's visible on-chain interactions: approve + several batchDeposit transactions + optional withdrawExpired afterward — **all triggered through the Web Dapp, no scripting required**.

### Task Card Example

A project distributing 500 cards to attendees at an in-person conference, 50 USDT per card, structured as "claim 10 on arrival + unlock 10 each for 4 tasks":

```
1. Order 500 cards (Polygon / USDT / co-branded card design)
2. Design campaign: basic amount 10 USDT + 4 tasks (follow on X / retweet / join TG group / on-chain interaction — 10 USDT each)
3. We ship cards + batch JSON
4. Spot-check cards
5. Web Dapp → upload JSON → basic 10 + 4×10 tasks → 60-day expiry → Lock (write task commitments)
6. Distribute cards at the conference
7. Users scan to claim 10 USDT (recipient address bound) → complete tasks later, unlock each task amount one by one for +10 each
8. After 60 days, Withdraw Expired in one click to reclaim amounts from uncompleted tasks
```

The dashboard shows in real time: who claimed the basic amount, which tasks each user completed, and their on-chain profile.

## Notes

- **Batch size**: The Web Dapp automatically splits batches based on the target chain's gas limit — no manual batch size calculation needed.
- **NFT recipient address validation**: The contract layer does not restrict recipient address type, but the Hongbao official App validates that the cardholder's address can receive ERC721 before signing (prevents NFTs from being sent to addresses that do not implement `onERC721Received` and becoming permanently inaccessible).
- **Minimum expiry of 30 days**: Hardcoded constant in the contract.
- **Asset scope**: Each Pool is bound to a single asset type. Multiple asset types = multiple Pools (managed separately within the Web Dapp).
- **Cross-chain deposits**: Each chain is fully independent. Cards are in secp256k1 address format — the same address exists across EVM chains — but **a card can only sign once**, meaning a single card can only be locked on one chain and claimed on one chain. **Do not lock assets to the same card address on multiple chains simultaneously.** Whichever chain the user claims on, the assets on all other chains become permanently unrecoverable (only recourse is waiting for expiry to reclaim).
