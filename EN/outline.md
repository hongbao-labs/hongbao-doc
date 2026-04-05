# Documentation Outline (Draft)

Working document for planning doc content. Delete after all docs are written.

Items marked `[TBD]` need team input before writing.

---

## User Docs

### user/overview.md — What is Hongbao

- One sentence: a crypto gift card in hardware form
- The problem: sending crypto to someone who doesn't have a wallet
- The solution: a physical device that holds a private key, claim with one button press
- Key properties (no jargon):
  - Nobody knows the private key — not even us
  - One-time use: once claimed, the device is spent
  - No crypto knowledge needed to receive: App + button press + done
  - No gas fees for the receiver
- How it works (high-level, with illustrations):
  - Sender: buy device → lock tokens to its address → gift the device
  - Receiver: scan QR → connect App → press button → tokens arrive in your wallet
- What's inside the device (simple version): secure chip, BLE radio, button, LEDs
- LED meaning for users (green blink = ready, alternating = confirm, green solid = connected, etc.)

### user/sender-guide.md — Sending a Hongbao

- Where to buy [TBD]
- Understanding the QR code: device address + identity
- Locking tokens:
  - Via website: connect wallet → enter device address (scan QR) → choose token + amount → confirm [TBD]
  - Via App [TBD]
- Optional: set expiry for automatic refund [TBD]
- Gifting: just hand over the physical device
- Checking status: see if your Hongbao has been claimed [TBD]

### user/receiver-guide.md — Claiming a Hongbao

- Step-by-step with screenshots [TBD]:
  1. Download the Hongbao App [TBD: links]
  2. Open the Hongbao packaging, device powers on (green LED blinks)
  3. Scan the QR code on the device
  4. App connects via Bluetooth — LEDs alternate red/green
  5. Press and hold the button for 3 seconds to confirm connection
  6. Enter your wallet address (or create one in-app)
  7. Press and hold the button for 10 seconds to sign the claim
  8. Wait for confirmation — tokens arrive in your wallet
- What if something goes wrong:
  - "LEDs not blinking" → device might be asleep, hold button 3s to wake
  - "Can't connect" → make sure Bluetooth is on, stay close to device
  - "Button timeout" → try again, hold firmly for full duration
  - "Already claimed" → red LED stays on, device is spent

### user/faq.md — Frequently Asked Questions

- Is this safe? (Private key never leaves the device, etc.)
- Can someone steal my tokens over Bluetooth? (No — physical button required)
- What if I lose the device before claiming? (Sender can reclaim after expiry [TBD])
- Can I re-use a Hongbao? (No — one-time use by design)
- What tokens are supported? [TBD]
- What chains are supported? [TBD]
- Do I need a crypto wallet to receive? (App can create one for you [TBD])
- Who pays the transaction fee? (Relayer sponsors gas, free for receiver)
- How long do locked tokens last? (Until claimed or expiry [TBD])
- Can the sender cancel? [TBD]

---

## Developer Docs

### dev/architecture.md — System Architecture

- Component diagram:
  ```
  ┌──────────┐  BLE   ┌──────────┐  HTTPS  ┌──────────┐  on-chain  ┌──────────┐
  │  Device   │◄─────►│   App    │◄──────►│  Relayer  │◄─────────►│ Contract │
  └──────────┘        └──────────┘         └──────────┘           └──────────┘
  ```
- Data flow: lock → gift → claim (sequence diagram)
- What each component knows / can do:
  | Component | Knows private key? | Knows recipient? | Submits tx? |
  |-----------|-------------------|-----------------|-------------|
  | Device | Yes (never exports) | No | No |
  | App | No | Yes (user input) | No |
  | Relayer | No | Yes (from signed msg) | Yes |
  | Contract | No | Yes (from ecrecover) | N/A |
- Trust model: the claim is valid if and only if the device signed it — no other party can forge, modify, or redirect
- End-to-end claim sequence diagram:
  ```
  Sender           Website/App       Contract        Device          App           Relayer
    │  lock tokens ──►│──── lock() ──►│               │               │               │
    │  gift device    │               │               │               │               │
    │                 │               │               │◄── BLE ──────►│               │
    │                 │               │               │  sign claim   │               │
    │                 │               │               │──► signature ─►│── POST /claim►│
    │                 │               │               │               │               │── claim() ──►│
    │                 │               │               │               │◄── txHash ────│              │
  ```

### dev/device.md — Hardware Device

- Hardware summary (MCU, secure element, BLE) — reference firmware README for full detail
- BLE protocol quick reference:
  - Service UUID, characteristic UUIDs
  - Command table (subset relevant to claim flow): IDENTITY_CHALLENGE, SIGN, GET_PUBKEY, GET_ETH_ADDRESS
  - Binary frame format
- Device state machine (FSM): ADVERTISING → PENDING → CONFIRMED → IDENTIFIED
- What the device signs:
  - The App constructs an EIP-712-like typed data hash (32 bytes)
  - The device signs this hash with its main signing key (Slot 2)
  - The device does NOT know what the hash represents — it just signs 32 bytes
- Security layers (summary, reference security.md for detail):
  - Key never exported, HMAC binding, identity verification, physical button, single-sign
- Firmware build modes: test (multi-sign) vs release (single-sign)
- Full firmware documentation: `../../README.md`

### dev/contract.md — Smart Contract

- Purpose: escrow for token gifts, claimable only by device signature
- Lock interface:
  ```solidity
  function lock(address deviceAddress, address token, uint256 amount, uint256 expiry) external payable
  ```
  - [TBD] exact interface, events, access control
- Claim interface:
  ```solidity
  function claim(address deviceAddress, address recipient, uint8 v, bytes32 r, bytes32 s) external
  ```
  - [TBD] exact interface
- EIP-712-like typed data for claim:
  ```
  Domain: { name: "Hongbao", version: "1", chainId, verifyingContract }
  Types:  Claim { address device, address recipient, uint256 nonce }
  ```
  - [TBD] exact fields — this is the most critical design decision
  - Device signs: `keccak256(abi.encodePacked("\x19\x01", domainSeparator, structHash))`
  - Contract verifies: `ecrecover(digest, v, r, s) == deviceAddress`
- Storage:
  - Mapping: deviceAddress → { sender, token, amount, expiry, claimed }
  - [TBD] multi-lock support? Multiple tokens to same device?
- Refund mechanism:
  - After expiry, sender can call `refund(deviceAddress)` to reclaim tokens [TBD]
- Token support:
  - ERC-20 [TBD]
  - Native ETH [TBD]
  - ERC-721 / ERC-1155? [TBD]
- Multi-chain:
  - Same contract on multiple chains? Chain-specific domain separator handles replay [TBD]
  - Deployment addresses [TBD]
- Security considerations:
  - Reentrancy protection
  - ecrecover returns address(0) on invalid sig → must check
  - Front-running: relayer submits, MEV bot replaces recipient? → recipient is inside signed message
- Audit plan [TBD]

### dev/relayer.md — Relayer Service

- Purpose: gasless claims — receiver doesn't need ETH to claim
- API spec:
  ```
  POST /api/v1/claim
  {
    "deviceAddress": "0x...",
    "recipientAddress": "0x...",
    "signature": "0x...",     // 65 bytes: r(32) + s(32) + v(1)
    "chainId": 1
  }
  → { "txHash": "0x...", "status": "pending" }
  ```
  - [TBD] exact API, authentication, rate limits
  ```
  GET /api/v1/status/{txHash}
  → { "status": "confirmed", "blockNumber": 12345 }
  ```
- Why the Relayer cannot cheat:
  - Signature is over (device, recipient, nonce) — cannot change recipient
  - Contract verifies ecrecover — cannot forge signature
  - One-time claim — cannot replay
  - Relayer only role: pay gas and submit the already-signed transaction
- Gas sponsorship model [TBD]:
  - Project-funded? Sender-funded (included in lock amount)? Ad-supported?
  - Per-claim gas budget, max gas price
- Abuse prevention [TBD]:
  - Rate limiting per device address, per IP
  - Invalid signature rejection (verify locally before submitting)
  - Duplicate claim detection
- Infrastructure [TBD]:
  - Hosting, RPC providers, key management for relayer EOA
  - Monitoring: claim success rate, gas spend, queue depth
  - Failover: what if relayer is down? App can submit directly if user has gas

### dev/app.md — App Client

- Platforms [TBD]: iOS, Android, web?
- Tech stack [TBD]
- Core user flow (maps to receiver-guide.md):
  1. Scan QR code → parse device ETH address + identity pubkey
  2. BLE scan + connect to device by name (`hongbao_XXXX`)
  3. Wait for connection confirmation (CONN_CONFIRM notifications, 3s button hold)
  4. Auto identity challenge → verify returned pubkey matches QR code
  5. User inputs recipient address (or App creates/imports wallet)
  6. App constructs EIP-712-like claim digest (32 bytes):
     - Query contract for lock info (token, amount, nonce)
     - Build typed data struct → hash → 32-byte digest
  7. Send SIGN command with digest → device prompts button hold
  8. Receive 64-byte signature (r, s) → determine v by trying both recovery IDs
  9. POST to Relayer `/api/v1/claim`
  10. Poll transaction status → show confirmation
- BLE integration details:
  - Binary protocol: frame format, commands used
  - Connection flow: scan → connect → service discovery → subscribe notifications
  - Error handling: timeout, disconnect, retry
- QR code format [TBD]:
  - Proposal: `hongbao://<eth_address>?identity=<identity_pubkey_hex>&chain=<chainId>`
  - Or: JSON in QR? URL to website that redirects to App?
- UI/UX [TBD]:
  - Onboarding for non-crypto users
  - Wallet creation flow (if user has no wallet)
  - Error states and recovery
  - Localization [TBD]
- Offline capability:
  - BLE connection + signing works offline
  - Relayer submission requires internet
  - App can queue claim for later submission

### dev/security.md — End-to-End Security

- Threat model: assets (locked tokens), attackers (remote, physical, supply chain, insider)
- Security by layer:

  | Layer | Mechanism | Protects Against |
  |-------|-----------|-----------------|
  | Secure element (MOD8) | Key gen + storage inside tamper-resistant chip | Key extraction, side-channel |
  | HMAC binding | MCU UUID ↔ MOD8 slot verification | MCU/chip swap attack |
  | Identity verification | ECDSA challenge-response + QR pubkey comparison | MITM, fake device |
  | Connection confirmation | Physical 3s button hold, 10s timeout | Unauthorized BLE access |
  | Sign authorization | Physical 10s button hold | Remote/accidental signing |
  | Single-sign (release) | Firmware enforces sign_count ≤ 1 | Double-claim at device level |
  | EIP-712-like signature | Recipient inside signed message | Relayer/MITM redirect |
  | Contract enforcement | ecrecover + one-time claim | Signature forgery, replay |
  | Watchdog (IWDG) | Hardware reset on firmware hang | Denial of service via hang |

- Attack scenario analysis:
  | Attack | Vector | Mitigation | Residual risk |
  |--------|--------|-----------|--------------|
  | Eavesdrop BLE | Passive radio | Key never transmitted; signature is public anyway | None |
  | Fake device | Attacker replaces device | Identity key + QR comparison in App | User must scan QR |
  | Swap MOD8 chip | Physical tampering | HMAC binding fails on boot | Requires matching MCU |
  | Remote sign | BLE without physical access | Connection confirm + sign button | Attacker needs device |
  | Relayer redirects funds | Malicious relayer | Recipient in signed EIP-712-like message | None |
  | Double claim | Replay signature | Contract one-time claim + device single-sign | None |
  | Front-running | MEV bot replaces relayer tx | Recipient is inside signature, cannot change | None |
  | Device lost | Physical loss | Sender refund after expiry | Tokens locked until expiry |
  | Supply chain | Compromised factory | Key gen on-device, SWD lock, HMAC binding | [TBD: secure boot] |

- BLE transport: unencrypted by design (signatures are unforgeable, no secrets transmitted)
- Relayer trust: zero trust required (can only submit, not modify)
- Contract audit status [TBD]

### dev/lifecycle.md — Device Lifecycle

- Factory provisioning:
  1. Flash test firmware via SWD
  2. First boot: auto key-gen (identity Slot 0, signing Slot 2, HMAC Slot 6)
  3. Lock config zone + data zone (irreversible)
  4. Test: sign + verify + identity challenge
  5. Clear sign record
  6. Flash release firmware
  7. Read public keys → generate QR code data
  8. SWD lock (prevents firmware extraction)
  9. Print QR label, attach to device, package
- Pre-sale storage:
  - Device is powered off (deep sleep or no battery contact)
  - No tokens locked yet — device is inert
- Sender flow:
  - Buy device → get QR code (ETH address)
  - Lock tokens to contract
  - Gift device (physical handover)
- Receiver flow:
  - Power on → App connect → confirm → sign claim → done
- Post-claim state:
  - Device: sign_count = 1, red LED on, cannot sign again
  - Contract: claimed = true, tokens transferred
  - Device is effectively spent
- End-of-life:
  - Device has no further function
  - Battery will eventually die [TBD: battery life estimate]
  - Disposal: standard electronics recycling
- Failure modes and recovery:
  | Failure | Impact | Recovery |
  |---------|--------|----------|
  | Dead on arrival | Cannot connect/sign | Manufacturer replacement [TBD] |
  | Battery dies before claim | Cannot sign | Replace battery? Sender refund after expiry? [TBD] |
  | Lost device | Cannot claim | Sender refund after expiry [TBD] |
  | BLE connection issues | Cannot complete claim | Retry, bring closer, check App version |
  | Relayer down | Signature obtained but not submitted | App queues, retry later, or user submits directly |
