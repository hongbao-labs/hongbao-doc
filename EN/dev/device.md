# Hongbao Device

The Hongbao device is a BLE-connected hardware signer. It generates and stores an ECDSA secp256k1 key pair that never leaves the device. External clients interact with it over a binary BLE GATT protocol.

## Hardware

| Component | Role |
|-----------|------|
| MCU | ARM Cortex-M0 with BLE 5.0 radio |
| Secure Element | ECDSA secp256k1 key gen/sign/verify, HMAC-SHA256, tamper-resistant packaging |
| User Interface | 1 button, 2 LEDs (red/green) |

The private key is generated inside the secure element during manufacturing and permanently sealed. Nobody — including the manufacturer — can extract it.

## Key Architecture

The device holds two separate key pairs:

| Key | Purpose | Used When |
|-----|---------|-----------|
| **Signing key** | Signs claim digests — controls tokens on-chain | Claim (one-time) |
| **Identity key** | Proves device authenticity over BLE (challenge-response) | Every BLE session |

The device's **ETH address** is derived from the signing key's public key: `keccak256(pubkey)[12..32]`. This address is printed on the device's QR label and is what the sender locks tokens to.

An additional symmetric key binds the MCU to the secure element, preventing chip-swap attacks.

## BLE Protocol

### GATT Service

| UUID | Type | Direction |
|------|------|-----------|
| `0xFFFA` | Service | — |
| `0xFFFB` | Write Characteristic | Client → Device |
| `0xFFFC` | Notify Characteristic | Device → Client (CCCD enable required) |

### Frame Format

**Request** (client → device): `[CMD:1B][LEN:1B][PAYLOAD:0-255B]`

**Response** (device → client): `[CMD:1B][STATUS:1B][LEN:1B][PAYLOAD:0-255B]`

Notify responses larger than 20 bytes (BLE MTU) are chunked into 20-byte segments.

### Commands

| CMD | Name | Access | Payload | Response |
|-----|------|--------|---------|----------|
| 0x01 | GET_PUBKEY | OPEN | — | 64B signing public key |
| 0x02 | GET_IDENTITY | CONFIRMED | — | 64B identity public key |
| 0x03 | IDENTITY_CHALLENGE | CONFIRMED | 32B random challenge | 64B signature + 64B identity pubkey |
| 0x04 | SIGN | IDENTIFIED | 32B digest | WAITING_BUTTON → OK + 64B signature, or TIMEOUT |
| 0x05 | VERIFY | OPEN | 96B (32B digest + 64B sig) | 1B (0=invalid, 1=valid) |
| 0x06 | SIGN_RECORD | IDENTIFIED | — | 4B count; if >0: +32B digest +64B signature |
| 0x07 | SLEEP | IDENTIFIED | — | 1B ack |
| 0x08 | GET_ETH_ADDRESS | OPEN | — | 20B ETH address |
| 0x09 | GET_DIAG_LOG | IDENTIFIED | — | Chunked diagnostic data |
| 0x0B | CONN_CONFIRM | — | — | Unsolicited notification from device |

### Access Levels

Commands are gated behind a three-tier session state:

| Level | Requirement | Available Commands |
|-------|-------------|----------|
| **OPEN** | BLE connected | GET_PUBKEY, GET_ETH_ADDRESS, VERIFY |
| **CONFIRMED** | Physical button hold (3 seconds) | + GET_IDENTITY, IDENTITY_CHALLENGE |
| **IDENTIFIED** | Successful identity challenge | + SIGN, SIGN_RECORD, SLEEP, GET_DIAG_LOG |

### Status Codes

| Code | Name | Meaning |
|------|------|---------|
| 0x00 | OK | Success |
| 0x01 | ERROR | Generic error (includes: device already signed) |
| 0x02 | WAITING_BUTTON | Device waiting for user to press button |
| 0x04 | TIMEOUT | Button not pressed within timeout window |
| 0x07 | AUTH_REQUIRED | Session not identified — send IDENTITY_CHALLENGE first |
| 0x08 | RATE_LIMITED | Too many commands in time window |
| 0x09 | NOT_CONFIRMED | Connection not confirmed — press button to confirm |
| 0x80 | MORE_DATA | Chunked transfer: more data follows |

## Device State Machine

```
                BLE connect
  ┌───────────┐ ──────────► ┌───────────┐
  │ADVERTISING│             │  PENDING   │  Red/green LEDs alternate
  │Green blink│ ◄────────── │ (10s gate) │
  └─────┬─────┘  Timeout    └─────┬─────┘
        │        or reject        │ Button hold 3s
        │                        ▼
        │                  ┌───────────┐
        │   BLE disconnect │ CONFIRMED  │  Green LED on
        │  ◄────────────── │            │
        │                  └─────┬─────┘
        │                        │ Identity challenge OK
        │                        ▼
        │                  ┌───────────┐
        │   BLE disconnect │ IDENTIFIED │  Green LED on, full access
        │  ◄────────────── │            │
        │                  └─────┬─────┘
        │                        │
        │  Long-press / idle /   │ SLEEP command
        │  SLEEP command         │
        ▼                        ▼
  ┌──────────────────────────────────┐
  │     DEEP SLEEP (LEDs off)        │
  │  Wake: hold button 3 seconds     │
  └──────────────────────────────────┘
```

| From | Event | To | Action |
|------|-------|----|--------|
| ADVERTISING | BLE connect | PENDING | LEDs alternate, send WAITING_BUTTON |
| PENDING | Button hold 3s | CONFIRMED | Green LED on, send CONN_CONFIRM OK |
| PENDING | 10s timeout | ADVERTISING | Disconnect, send CONN_CONFIRM TIMEOUT |
| CONFIRMED | Identity challenge OK | IDENTIFIED | Full command access |
| Any connected | BLE disconnect | ADVERTISING | Reset session |
| Any | Long-press 3s / 5min idle / SLEEP cmd | DEEP SLEEP | Power down |
| DEEP SLEEP | Button hold 3s | ADVERTISING | Full reinit |

## Connection and Signing Flow

Complete BLE interaction sequence for a claim:

```
App                                 Device
 │                                    │
 │  BLE connect                       │  → PENDING, LEDs alternate
 │  ◄── CONN_CONFIRM(WAITING_BUTTON)  │  Heartbeat every 2s
 │                                    │
 │      User holds button 3s          │  → CONFIRMED
 │  ◄── CONN_CONFIRM(OK)              │
 │                                    │
 │  ── IDENTITY_CHALLENGE(32B) ──►    │  Signs with identity key
 │  ◄── 64B signature + 64B pubkey    │  → IDENTIFIED
 │                                    │
 │  App verifies: pubkey == QR code   │
 │                                    │
 │  ── SIGN(32B digest) ──────────►   │
 │  ◄── WAITING_BUTTON                │  Red LED blinks
 │                                    │
 │      User holds button 10s         │  Signs with signing key
 │  ◄── OK + 64B signature            │  Device is now spent
 │                                    │
 │  App sends signature to Relayer    │
```

### What the Device Signs

The device signs a **32-byte digest**. It does not know or care what the digest represents. The App constructs the digest (e.g., hashing a claim message containing the recipient address and chain-specific data). The contract verifies that the signature recovers to the device's ETH address.

**Signature format**: 64 bytes — `r` (32B) + `s` (32B), ECDSA secp256k1. The recovery parameter `v` is not provided by the device; the App must determine it by trying both recovery IDs (27/28). The contract can use Solidity's standard `ecrecover` directly.


## Security Model

| Layer | Mechanism | Threat Mitigated |
|-------|-----------|-----------------|
| Key storage | Tamper-resistant secure element | Key extraction, side-channel |
| Hardware binding | HMAC-SHA256 MCU ↔ secure element | Chip-swap attack |
| Device identity | ECDSA challenge-response + QR pubkey | MITM, fake device |
| Connection gate | Physical button hold 3s, 10s timeout | Unauthorized BLE access |
| Sign authorization | Physical button hold 10s | Remote or accidental signing |
| Single-sign | Device can only sign once | Double-claim at device level |
| Rate limiting | 3 cmd/s before auth, 10 cmd/s after | Command flooding |

### Identity Verification

Every BLE session, the App should verify the device is genuine:

1. App sends a random 32-byte challenge via `IDENTITY_CHALLENGE`
2. Device signs it with the identity key and returns signature + identity public key
3. App compares the returned public key against the one from the QR code

If they match, the device is the one that was manufactured — not a substitute.

### Why BLE Encryption Is Not Used

- The private key is never transmitted over BLE
- Signatures are public (submitted to blockchain)
- Device authenticity is verified cryptographically, not by BLE pairing
- Physical button is required for all sensitive operations

## LED Behavior

| State | Green | Red | Meaning |
|-------|-------|-----|---------|
| Advertising | Slow blink | OFF | Ready for connection |
| Advertising (signed) | Slow blink | ON | Already claimed |
| Connection pending | Alternate | Alternate | Press button to confirm |
| Connected | ON | OFF | Ready for commands |
| Connected (signed) | ON | ON | Already claimed |
| Waiting for sign | ON | Blink | Hold button to authorize |
| Error | OFF | ON | Hardware fault |
| Deep sleep | OFF | OFF | Powered down |

## Power Management

- **Deep sleep**: All peripherals off, LEDs off, BLE disconnected. Wake by holding button 3 seconds.
- **Sleep triggers**: SLEEP command, 5-minute idle timeout, 3-second button long-press.
- **Watchdog**: Hardware watchdog auto-resets the device on firmware hang. A low-power timer feeds the watchdog during sleep to prevent false resets.
