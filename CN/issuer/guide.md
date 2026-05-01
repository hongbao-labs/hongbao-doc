# 发卡方端到端流程

从下单到用户领取，整个流程像下面这样。**所有合约交互都集成在 Hongbao Web Dapp 里——项目方不需要写脚本、不需要直接调合约、不需要部署 Factory / Pool**，链上动作全部由前端按钮触发。

```
1. 下单
2. 我们寄卡 + JSON
3. 项目方收货验证
4. 在 Web Dapp 一键锁定资产
5. 派发实体卡
6. 持卡人扫码领取
7. （可选）过期一键赎回
```

> 想绕过 Web Dapp、直接走合约层 / 自建客户端的开发者团队，参考 [dev/](../dev/)。本文面向项目方运营 / 商务侧，按 Web Dapp 流程描述。

---

## 1. 下单

按订单交付。下单时确认：

- **数量**
- **目标链**：协议层支持任何 secp256k1 验签的链；当前已开发 EVM 全系合约（其他链按订单扩展）
- **资产类型**：当前 EVM 合约覆盖 ERC20 + ERC721；ERC1155 / 原生币 / 非标代币按订单定制
- **卡面定制方案**：详见 [customization.md](customization.md)

卡到货时已完成全部出厂工序：

- 芯片内随机生成 secp256k1 私钥（永久封存，无人可读出）
- HMAC 绑定 MCU + 安全芯片（防换芯片攻击）
- SWD 烧录锁定（防固件提取）
- 工厂锁定（防出厂后恶意指令）
- 签名 / 验证 / 身份认证测试通过
- 深度休眠状态（零功耗）

你**不需要**做任何固件层操作。

## 2. 我们寄卡 + JSON

每批卡随附一份 JSON 元数据文件，结构形如：

```json
{
  "batch_id": "...",
  "chain": "ethereum",
  "asset_contract": "0x...",
  "card_count": 1000,
  "cards": [
    { "eth_address": "0xAbc...", "qr_code_url": "https://hongbao.digital/_c?ea=...", "..." },
    ...
  ]
}
```

> [TBD: JSON 完整字段定义 / 示例文件]

## 3. 收货验证

收到卡片 + JSON 后，建议做一次验卡：

- **抽样验证**（推荐）：随机挑若干张卡，用 Hongbao 提供的工具读取每张卡的真实链上地址，与 JSON 中的 `eth_address` 比对
- **全量验证**：批次涉及金额特别大时可以全量做一遍

[TBD: 验卡工具下载链接 + 操作步骤]

确认无误后进入下一步。

## 4. 在 Web Dapp 一键锁定资产

登录 [TBD: Hongbao Issuer Dapp URL]，连接你的 deposit 钱包：

[TBD: 截图 + 文字步骤]
- 上传 / 选择批次 JSON
- 选择资产合约（自动校验与 JSON 一致）
- 设置每张卡锁定金额（ERC20）/ 选择 tokenId 列表（ERC721）
- 设置过期时间（最少 30 天）
- 点击「Lock」

后台一次性完成（你不需要关心）：

- （首次该链该资产）部署 Factory
- 创建 Pool（每种资产 + 每个 deposit 钱包一次，已存在则复用）
- ERC20 合约 approve
- 按链上 gas limit 自动拆分批次 batchDeposit
- 每笔交易状态实时回显，失败可重试

进度走完后，所有卡都进入「可领取」状态。

## 5. 派发

把实体卡寄 / 送给用户。怎么送是你的事——内嵌贺卡、活动现场、快递邮寄都行。

派发时建议同时告知用户：

- 这是张红包卡，扫码就能领
- 过期时间（避免用户错过）

二维码默认指向 `https://hongbao.digital/...`——扫出来直接进 Hongbao 官方领取入口（Web 端自动适配；安装了 Hongbao App 会优先打开 App），不需要额外引导。持卡人入口的标准化是产品保障，发卡方不另行托管 / 替换前端。

## 6. 持卡人领取

详见 [持卡人领取指南](../receiver/guide.md)。

链上交易通过 Hongbao 官方 Relayer（默认）或自托管 Relayer 提交。你不需要在领取流程中做任何事。

链上事件可以监听，用于更新自己后台的兑付状态：

| 资产 | 事件 |
|---|---|
| ERC20 | `Withdraw(unlockAddress, to, amount)` |
| ERC721 | `WithdrawNFT(unlockAddress, to, tokenId)` |

## 7. 过期赎回（可选）

最早可在 deposit 后 `lockTime` 秒发起。在 Web Dapp 同一界面里：

[TBD: 截图 + 步骤]
- 选择批次
- 点击「Withdraw Expired」

行为：

- 已被领取的卡 → 自动跳过
- 没有 deposit 记录 → 自动跳过
- 资产回到你的 deposit 钱包

---

## 端到端示例

某 DeFi 项目方给 1000 名 KOL 各空投 100 USDT，托管在 Polygon：

```
1. 下单 1000 张卡（Polygon / USDT / 卡面联名定制方案）
2. 我们寄卡 + 批次 JSON
3. 项目方抽样读 50 张卡比对地址，确认无误
4. 登录 Web Dapp → 上传 JSON → 100 USDT/张 → 60 天过期 → Lock
5. 寄卡给 KOL
6. KOL 扫码领取（Hongbao 官方入口，gas 由默认 Relayer 代付）
7. 60 天后回到 Web Dapp，一键 Withdraw Expired 把未领部分赎回
```

项目方可见的链上交互：approve + 若干笔 batchDeposit + 后续可选 withdrawExpired，**全部通过 Web Dapp 触发，不需要写脚本**。

## 注意事项

- **批量大小**：Web Dapp 按目标链 gas limit 自动拆分，不需要手动算 batch size
- **NFT 收款地址校验**：合约层不限制收款地址类型，但 Hongbao 官方 App 会在持卡人签名前校验地址是否能接收 ERC721（避免 NFT 转入不实现 `onERC721Received` 的地址而报废）
- **过期时间最少 30 天**：合约硬编码常量
- **资产范围**：每个 Pool 绑定一种资产；多种资产 = 多个 Pool（Web Dapp 内部分别管理）
- **跨链 deposit**：每条链各自独立。卡是 secp256k1 地址形态，跨 EVM 链同址，但**卡只能签一次**——同一张卡只能在一条链上锁、一条链上领。**不要往同一张卡的地址在多条链同时锁资产**，否则用户在哪条链上领，其他链的资产就再也取不出来（只能等过期赎回）
