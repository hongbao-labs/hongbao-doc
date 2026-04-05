# Hongbao Technical Documentation

Hongbao is a one-time hardware signing device designed as a crypto gift card. It stores a private key that never leaves the chip — anyone can lock tokens to its public address, and the person holding the device can claim them with a single button press.

## Documentation Structure

### For Users

Explains what Hongbao is and how to use it. No code, no implementation details.

| Document | Content |
|----------|---------|
| [user/overview.md](user/overview.md) | What is Hongbao, how it works, key concepts |
| [user/sender-guide.md](user/sender-guide.md) | How to buy a Hongbao, lock tokens, gift it |
| [user/receiver-guide.md](user/receiver-guide.md) | How to open, connect, and claim your tokens |
| [user/faq.md](user/faq.md) | Common questions: lost device, expiry, safety |

### For Developers

System design, protocols, security model, and integration specs for each component.

| Document | Content |
|----------|---------|
| [dev/architecture.md](dev/architecture.md) | System architecture, component diagram, data flow, trust model |
| [dev/device.md](dev/device.md) | Hardware device: BLE protocol, state machine, security model |
| [dev/contract.md](dev/contract.md) | Smart contract: lock/claim, EIP-712-like typed data, token support |
| [dev/relayer.md](dev/relayer.md) | Relayer service: API, gas sponsorship, abuse prevention |
| [dev/app.md](dev/app.md) | App client: BLE integration, signing UX, QR code format |
| [dev/security.md](dev/security.md) | End-to-end security: threat model, attack scenarios, mitigations |
| [dev/lifecycle.md](dev/lifecycle.md) | Device lifecycle: factory provisioning → gift → claim → end-of-life |

## Status

| Component | Status | Notes |
|-----------|--------|-------|
| Device firmware | Implemented | See [`../README.md`](../README.md) for full firmware docs |
| Smart contract | Design phase | EIP-712-like structure TBD |
| Relayer | Design phase | API spec TBD |
| App client | Design phase | Platform TBD |
| User docs | Outline only | Pending product finalization |
