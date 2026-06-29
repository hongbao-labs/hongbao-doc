# Card Customization

Hongbao cards offer a meaningful degree of customization — though not "unlimited" customization. In principle, a card breaks down into three parts:

1. **Hongbao branding**: must be retained;
2. **Customizable area**: where issuers can place their own brand content;
3. **Functional area**: printing, embedded components, buttons, and core logic — not modifiable.

These rules serve two goals at once: preserving Hongbao's consistent security and user experience, while still letting issuers put their own brand stamp on the card face.

> This specification is still being finalized. Items marked **🚧 Coming soon** — specs, pricing, and process — are not yet publicly finalized; the latest signed commercial agreement takes precedence. For specific quotes or design templates, reach out via [contact.md](../contact.md).

---

## Reserved Areas (Fixed)

| Location | Content | Reason |
|---|---|---|
| **Card front — top-left corner** | Hongbao logo | The anchor that lets cardholders recognize a trusted Hongbao card |
| **Card back** | QR code (links to the on-chain address / claim entry) | The sole entry point for cardholders to scan and claim |
| **Card back** | Required text (usage instructions / security notice / others, 🚧 Coming soon) | Compliance and safety notices |

> 🚧 Coming soon: front/back card diagrams annotating the exact dimensions and positions of the reserved areas.

## Customizable Areas (Open to Issuers)

| Area | Customizable Elements |
|---|---|
| **Front** (everything but the top-left logo) | Hero artwork, brand logo, campaign tagline, color scheme, special finishing |
| **Back** (whitespace outside the QR code + reserved text) | Issuer copy, social media handles, event details (character / font-size limits 🚧 Coming soon) |

Non-customizable elements (determined by the hardware / protocol layer):

- Card dimensions / thickness: 🚧 Coming soon
- QR code / button / indicator light positions and sizes
- Chip model, firmware, Bluetooth protocol

## Finishing & Materials

| Item | Options |
|---|---|
| **Substrate** | 🚧 Coming soon |
| **Printing** | 🚧 Coming soon |
| **Special finishing** | 🚧 Coming soon |
| **Surface treatment** | 🚧 Coming soon |

## MOQ & Pricing

| Item | Details |
|---|---|
| **Minimum order quantity (MOQ)** | 🚧 Coming soon |
| **Base card price** | 🚧 Coming soon |
| **Customization surcharge** | Quoted separately based on selected finishing — 🚧 Coming soon |
| **Sampling fee** | 🚧 Coming soon |

## Process & Timeline

```text
1. Business engagement → NDA / contract cadence (Coming soon)
2. Design file submission → Issuer submits against the Hongbao template (format per "Artwork Specifications" below)
3. Template review → Hongbao validates reserved areas + finishing feasibility (review turnaround: Coming soon)
4. Sample approval → Physical sample cards shipped to the issuer for sign-off (sampling turnaround: Coming soon)
5. Mass production → production lead time: Coming soon
6. Shipping → DOA policy per contract
```

## Artwork Specifications

> The file formats, bleed, resolution, and color mode below follow standard print conventions, so issuers can prepare artwork ahead of time; the Hongbao template and proofing color check take final precedence.

| Item | Requirement |
|---|---|
| **File format** | Vector formats such as AI / PDF / EPS; all text converted to outlines, with linked images packaged alongside the file |
| **Bleed** | 3 mm bleed on all four sides; keep important content ≥ 3 mm from the trim line |
| **Resolution** | Embedded raster elements ≥ 300 dpi at final printed size |
| **Color mode** | CMYK; if brand spot colors are needed, also annotate the Pantone color codes |
| **Required reserved areas** | The top-left reserved area (dimensions 🚧 Coming soon) must contain no elements; the back reserved area (area description 🚧 Coming soon) must not be overprinted with text |
| **Template download** | 🚧 Coming soon |

## FAQ

**Q: Can the Hongbao logo be removed entirely?**
No. The top-left logo is the sole anchor that lets cardholders recognize a trusted Hongbao card. It is required on every shipped card and cannot be waived commercially.

**Q: How long does sampling take? Can the sampling fee be credited toward the mass production order?**
Sampling turnaround, and whether the fee is credited toward the production order, are confirmed per order — contact hello@hongbao.digital (see [contact.md](../contact.md)).

**Q: Can a single batch include multiple designs (variants)?**
Whether this is supported, along with the MOQ and extra cost for multiple designs, is assessed per order — contact hello@hongbao.digital (see [contact.md](../contact.md)).

## Contact

For business engagement, design file submission, and quote inquiries, see [contact.md](../contact.md).
