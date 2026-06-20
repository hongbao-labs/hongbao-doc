# Claim Guide

The whole process takes about 1 minute. Before you start, you'll need:

- Your Hongbao card
- A phone or computer with Bluetooth
- The Hongbao App open ([Android APK](https://github.com/hongbao-labs/HB_Android/releases/download/v1.0.4/hongbao-v1.0.4-release.apk))

> **Don't have a crypto wallet or exchange account yet? No problem.** The App will walk you through signing up with a mainstream crypto wallet or exchange so you can get a receiving address, then bring you right back to continue. Hongbao itself **never creates, holds, or touches** your private keys — your wallet or exchange account is always managed by that provider; we only guide you through the setup.

---

## Step 1: Scan

Point your phone camera at the QR code on the card. You'll be taken to the official Hongbao claim page (works in your browser automatically; if you have the Hongbao App installed it will open there instead).

No matter which project issued your card, the claim flow is the same — cards may look different (issuers can customize the design), but the process is unified.

## Step 2: Connect over Bluetooth

Turn on your phone's Bluetooth and let the App connect to the card.

| LED status | What it means | What you do |
|---|---|---|
| Green light slow blink | Card is awake, waiting to connect | Tap "Connect" in the App |
| Alternating red-green blink | Bluetooth connected, waiting for your confirmation | **Press and hold the button for 3 seconds** |
| Green light solid | Connection confirmed | Proceed to the next step |

If no lights are on at all, the card is in deep sleep — **press and hold the button for 3 seconds** to wake it.

If you don't press the button within 10 seconds, the connection will drop automatically and you'll need to reconnect.

## Step 3: Authorize the signature

In the App, enter **your own receiving address** — this is where the assets will be sent.

> ⚠️ **Double-check that this address belongs to a wallet you control.** Once you authorize the signature, the card is spent — the address cannot be changed or reversed.

Once you confirm, the App sends the signing request to the card.

| LED status | What it means | What you do |
|---|---|---|
| Green light solid + red light blinking | Waiting for your authorization | **Press and hold the button for 10 seconds** |
| Green light solid + red light solid | Signature complete, card has been used | Wait for the transaction to confirm on-chain |

After you sign, the App submits the transaction for you (gas is covered by the issuer or a third party — you pay nothing). The assets reach the address you entered within seconds, sometimes up to a minute if the network is busy.

## Step 4 (Task cards only): Complete tasks to unlock more

If you have a **task card**, what you claimed in the previous step is the **basic amount** — the App will show you that you can unlock additional amounts by completing tasks.

- Tasks may include: following the issuer's account, sharing a post, joining a group, making an on-chain interaction, checking in at an event, etc.
- Each time you complete a task, the corresponding task amount is automatically sent to the same address you locked in earlier
- **You don't need the card for this step** — the card already locked in your receiving address in Step 3; all further unlocks happen in the App
- No rush to finish: any task amounts you don't claim before the deadline are returned to the issuer, and won't affect what you've already received

> Because your receiving address was locked in during Step 3, task amounts can only go to your address — even if someone else gets hold of your task credentials, they cannot claim anything.

## Troubleshooting

| What you see | Possible cause | Fix |
|---|---|---|
| No lights at all | Card is in deep sleep | Press and hold for 3 seconds to wake |
| Can't connect via Bluetooth | Too far away, or Bluetooth is off | Move closer; make sure your phone's Bluetooth is on |
| Alternating red-green blink then disconnects | Button not pressed within 10 seconds | Reconnect, then press and hold for 3 seconds right away |
| No response after holding for 10 seconds | Didn't hold long enough, or missed the button | Try again, pressing firmly from the very start |
| Green + red both solid (card is brand new) | Card has already been claimed | Contact the issuer to verify |
| Red light solid only, green off (card is brand new) | Card malfunction | Contact the issuer to verify / request a replacement |
| Signature done but App is stuck | Network issue, submission failed | The App will retry automatically; or contact the issuer to submit manually |

Once the signature succeeds (green + red both solid), even if there's a problem submitting the transaction, **your assets are safe** — the signature already contains your receiving address, and whoever submits it, the funds can only go to the address you entered.

## Can I check how much is on the card?

Yes. Once you connect the card in the App, it will show you the type and amount of assets locked on the card, along with the expiry date. This information is read directly from the smart contract on-chain — it doesn't depend on the issuer.

## After you claim

- Green + red both solid: the card has been used and can no longer sign.
- Your assets are now in your wallet, just like any other on-chain assets — you can transfer or trade them freely.
- The card itself has no further use. Keep it as a memento, or recycle it as you would any ordinary electronic device.
- If the signature data is ever lost unexpectedly (relayer failure / App backend storage loss), don't worry — at the moment of signing, the Hongbao hardware records the complete signature in its secure chip. You can retrieve your previous signature at any time after signing.
