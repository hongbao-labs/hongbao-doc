# How to Claim

The whole process takes only about a minute. Before you start, all you need is:

- The Hongbao card itself
- A phone or computer with Bluetooth
- The Hongbao App, open ([Android APK](https://github.com/hongbao-labs/HB_Android/releases/download/v1.0.4/hongbao-v1.0.4-release.apk); iOS and Web coming soon)

> Don't have a crypto wallet or exchange account yet? No problem. The App will first walk you through signing up with a mainstream wallet or exchange to get a recipient address, then bring you back to continue the claim. Hongbao never creates, holds, or touches your private keys — your wallet or exchange account always stays under the control of that provider; we only guide you through the setup.

---

## Step 1: Scan

Use your phone's camera to scan the QR code on the card. This takes you to the official Hongbao claim page. The Web version adjusts to your screen automatically, and if you already have the Hongbao App installed, the page opens there instead.

No matter which project issued the card, the claim entry point is the same. The card design may look different, but the steps are identical.

## Step 2: Connect over Bluetooth

Turn on your phone's Bluetooth and let the App connect to the card.


| LED status | What it means | What you do |
|---|---|---|
| Green slow-blinking | Card is awake, waiting to connect | Tap "Connect" in the App |
| Red/green alternating blink | Bluetooth connected, waiting for confirmation | **Press and hold the button for 3 seconds** |
| Solid green | Connection confirmed | Proceed to the next step |

If none of the card's lights are on, it's in deep sleep — **press and hold the button for 3 seconds** to wake it.

If you don't complete the button confirmation within 10 seconds, the connection drops automatically and you'll need to reconnect.

## Step 3: Authorize the signature

In the App, enter your own recipient wallet address — this is where the assets will end up.

> ⚠️ **Be sure to double-check that this address really belongs to a wallet you control. Once you sign, the card is spent — after that it cannot be reversed, and the recipient address cannot be changed.**

Once you've confirmed it's correct, the App sends the data to be signed to the card.

| LED status | What it means | What you do |
|---|---|---|
| Solid green + red blinking | Waiting for you to authorize the signature | **Press and hold the button for 10 seconds** |
| Solid green + solid red | Signature complete, card has been used | Wait for the transaction to confirm on-chain |

After you sign, the App automatically submits the signature on-chain. The gas fee is covered by the issuer or a third party — you pay nothing yourself. The assets usually arrive at the wallet address you entered within a few seconds to a minute or so, depending on how busy the network is at the time.

## Step 4 (Task cards only): Complete tasks to unlock more

If you have a task card, what you claimed in the previous step is only the basic amount. The App will let you know that you can complete tasks to unlock more.

- Tasks may include: following the issuer, sharing a post, joining a group, making an on-chain interaction, checking in at an event, and so on
- Each time you complete a task, the matching amount is automatically sent to the very same address you locked in earlier
- This step no longer needs the card; your recipient address was already locked in during Step 3, and all further unlocks happen in the App
- Don't worry if you don't claim everything — any unfinished task amounts are reclaimed by the issuer after they expire, but this won't affect the portion you've already received

> Because your recipient address was locked in during Step 3, funds from task unlocks can only go to your address. Even if someone else gets hold of your task preimage, they cannot claim the funds.

## What to do if something goes wrong

| What you see | Possible cause | How to fix it |
|---|---|---|
| No lights | Card is in deep sleep | Press and hold the button for 3 seconds to wake it |
| Bluetooth connection fails | Too far away, or Bluetooth is off | Move closer, and make sure your phone's Bluetooth is on |
| Disconnects after red/green alternating blink | Button not confirmed within 10 seconds | Reconnect, then press and hold for 3 seconds immediately after connecting |
| No response after holding for 10 seconds | Didn't hold long enough, or didn't press firmly | Try again, making sure you hold steadily from the very start |
| Solid green + solid red (appears the moment you get the card) | Card has already been claimed | Contact the issuer to verify |
| Only solid red, green off (appears the moment you get the card) | Card malfunction | Contact the issuer to verify or request a replacement |
| App stuck after signing | Network issue or submission failed | The App will retry automatically; if it still fails, contact the issuer to submit manually |

Once the signature succeeds (solid green + solid red), a problem during the transaction submission step won't affect who the assets belong to. The signature already contains your recipient address — no matter who submits it, the funds can only go to the address you entered.

## Can I confirm how much is inside?

Yes. After you connect the card in the App, it shows the type and amount of assets currently locked on the card, along with the expiry date. This information is read directly from the smart contract on-chain, so it doesn't depend on the issuer.

## After you've claimed

- When the red and green lights are both solid, the card has been used and can no longer sign
- Your assets are now in your wallet, and just like any other on-chain assets, you can transfer or trade them freely
- The card itself has no further use; keep it as a memento, or recycle it as you would any ordinary electronic device
- If the signature data is ever lost unexpectedly (for example, a relayer failure or an issue with the App's backend storage), there's no need to worry: the moment it signed, the Hongbao card hardware saved the complete signature record in its secure element, and you can read it again at any time
