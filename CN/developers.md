# 开发者

Hongbao 的链上层**完全开放**。标准合约和签名规范是 Hongbao 作为生态协议的根基——钱包、交易所、Dapp 都可以基于它们集成或扩展，任何人都可以部署、fork 或审计这些合约。

> **源代码：** [github.com/hongbao-labs/contracts](https://github.com/hongbao-labs/contracts) —— 协议接口、合约、安全模型与设计原理。

---

## 哪些开放 / 哪些由官方提供

| 层 | 开源 | 由 Hongbao 提供 |
|---|---|---|
| 标准合约 + 签名规范 | ✅ 部署 / fork / 扩展 | — |
| BLE 接口规范 | ✅ | — |
| CLI 工具 | ✅ | — |
| 硬件（卡片） | — | 由 Hongbao 设计、生产、销售 |
| 官方客户端（Web / Android / iOS） | — | 由 Hongbao 提供 |

硬件与官方客户端统一提供，是为了让安全芯片供应链可信、固件审计一致、持卡人体验标准化。二次开发的空间在链上层。

## 一分钟架构

1. **Factory** 部署一个 **Pool**（每条链 + 每种资产部署一次）。
2. 发卡方把资产按每张卡的链上地址锁进 Pool（`deposit` / `batchDeposit`，任务卡用 `batchDepositWithTasks`）。
3. 持卡人用卡内永封的私钥，对一段包含自选收款地址的内容签名。
4. 任何人（**Relayer**、用户，或你）提交 `withdraw(unlockAddress, to, v, r, s)`。Pool 校验签名后把资金放给 `to`。**没有 `msg.sender` 限制**——任何 EOA 都能提交。
5. 锁定期过后，发卡方可以 `withdrawExpired` 收回未领资金。

卡片本身是 chain-agnostic 的——它对 32 字节摘要做 ECDSA 签名，不关心摘要属于哪条链。**要支持新链，只需在那条链上部署一份对应的"锁仓 → 验签 → 放款"合约，卡可以原样使用。**

## 任务卡

金额拆成基础份额加最多 255 个任务份额。第一次签名领取基础份额并绑定收款地址；每个任务份额通过提交其**预映像（preimage）**释放。预映像绑定了特定的（链、Pool、卡、任务槽），资金强制流向绑定地址——凭证泄露也无法被冒领或重放。机制：`batchDepositWithTasks`、`claimTask`。完整规范见仓库。

## 可监听的事件

| 动作 | 事件 |
|---|---|
| ERC20 领取 | `Withdrawn(unlockAddress, to, amount)` |
| 任务解锁 | `TaskClaimed(unlockAddress, taskIdx, to, amount)` |
| ERC721 领取 | `WithdrawNFT(unlockAddress, to, tokenId)` |

## 自建客户端

你不一定要用官方 Web Dapp 或 Relayer。团队可以直接走合约层——自部署 Factory/Pool、自运营 Relayer（或者让用户自付 gas，因为 `withdraw` 不限制提交者），基于合约 ABI 和 BLE 规范自建发卡方或持卡人客户端。从[开源仓库](https://github.com/hongbao-labs/contracts)开始。

## 支持的链与资产

- **当前已上线：** 以太坊及全部 EVM 链（ERC20 + ERC721 标准合约）。
- **按需开放：** Bitcoin、Solana、Sui、Aptos、Cosmos 等其他 secp256k1 生态。
- 原生币（ETH、BNB 等）当前标准合约不支持，请先包装（如 WETH）。ERC1155 / 非标 / 自定义合约按订单定制。

各网络的合约部署地址在仓库中公布，也可通过 dev@hongbao.digital 获取。

## 安全与披露

合约无 owner、无 admin、无暂停、无升级路径——完整说明见[安全模型](security.md)。发现问题？请邮件 **security@hongbao.digital**，并留出合理的披露窗口。

## 联系

技术问题与集成支持：**dev@hongbao.digital**（见 [contact.md](contact.md)）。
