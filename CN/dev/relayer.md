# Relayer

## Relayer 是什么

Relayer = **任意一个愿意替持卡人提交 `withdraw(...)` 交易并支付 gas 的 EOA**。

这就是它的全部职责。**Relayer 在系统里没有任何特权**：

- 不能改收款地址（`to` 是签名内容的一部分，改了签名失效）
- 不能私吞资产（`withdraw` 直接把资产转给签名里指定的 `to`）
- 不能阻止用户领取（用户可以换一个 relayer，或用自己的钱包提交）
- 不能修改资产数量（金额由链上 pool 状态决定）

合约层面 `withdraw` 不限制 `msg.sender`——任何 EOA 都能调。这意味着 relayer 是个**纯运营组件**，不是信任组件。

## 我们的默认 Relayer

我们运营一个公开 relayer，给用户/集成方提供 zero-config 的代付 gas 体验。

```
POST https://api.hongbao.digital/v1/claim     [TBD: 最终 URL]
Content-Type: application/json

{
  "chainId": 137,
  "pool": "0x...",                            // 目标 pool 地址
  "unlockAddress": "0x...",                   // 卡的 ETH 地址
  "to": "0x...",                              // 收款地址
  "v": 27,
  "r": "0x...",
  "s": "0x..."
}

→ 200 OK
{
  "txHash": "0x...",
  "status": "submitted"
}
```

```
GET https://api.hongbao.digital/v1/claim/{txHash}    [TBD]

→ {
  "status": "confirmed" | "pending" | "failed",
  "blockNumber": 12345,
  "error": null
}
```

> 接口字段当前为草案，最终以仓库内 OpenAPI 文档为准 [TBD: 链接]。

服务端会做的事：

1. 校验 chainId / pool 是否在白名单（防滥用）
2. 本地 ecrecover 校验签名有效（避免提交注定 revert 的交易）
3. 查 pool 状态确认卡未被领取（避免双花尝试）
4. 用 relayer EOA 签名并提交交易
5. 监听上链状态，返回 txHash

服务端**不会**：

- 修改/缓存 `to` 之外的任何用户私密信息
- 缓存或转发签名以外的钱包数据
- 对持卡人或发卡方收取任何形式的费用（早期阶段；未来可能加 fair-use 政策，会提前公告）

## 为什么 Relayer 是可选的

合约 `withdraw(unlockAddress, to, v, r, s)` 的 `msg.sender` 可以是任何地址。这意味着：

| 场景 | 提交者 | 谁出 gas |
|---|---|---|
| 默认（用户什么都不操心） | 我们的 relayer | 我们 |
| 项目方想自己控管 | 项目方自建 relayer | 项目方 |
| 用户有 native 币 | 用户自己钱包（MetaMask 等） | 用户 |
| 网络极端拥堵时备份 | 第三方 relayer 服务 | 第三方 |

签名一旦由设备产生，提交它就是个**纯链上操作**——签名本身不绑定任何提交者。

## 自托管 Relayer

完全可行，且推荐——尤其是：

- 你的发放规模大、希望控制 gas 预算
- 对 SLA / 监控 / 审计有自定义需求
- 想做特殊业务（KYC、领取条件、限速、数据落库）

最小可行实现：

```ts
// 收到 App POST 的 (chainId, pool, unlockAddress, to, v, r, s) 之后
import { createWalletClient, http } from 'viem';
import { mainnet } from 'viem/chains';
import { privateKeyToAccount } from 'viem/accounts';

const account = privateKeyToAccount(process.env.RELAYER_PK as `0x${string}`);
const wallet = createWalletClient({ account, chain: mainnet, transport: http(RPC) });

const txHash = await wallet.writeContract({
  address: pool,
  abi: HongBaoPoolAbi,
  functionName: 'withdraw',
  args: [unlockAddress, to, v, r, s],
});
```

加几道护栏：

- **签名预校验**：本地 ecrecover 一遍，避免提交注定 revert 的交易浪费 gas
- **状态预校验**：调 `cardUnlockedAt(unlockAddress)`，已领取直接拒绝
- **速率限制**：按 IP / 按 unlockAddress 限频，防 abuse
- **重放保护**：同一 (unlockAddress, to) 短时间内多次提交直接合并/去重
- **gas 预算**：单笔 maxFeePerGas 上限，防极端拥堵时 relayer 钱包被掏空
- **冗余**：多 RPC + 多 relayer EOA，单点故障切换

我们没有提供官方的"relayer SDK"——上面 20 行 viem 已经够用。如果需要更复杂的 abuse prevention，参考 OpenZeppelin Defender、Gelato Network 等成熟服务。

## 项目方自定义 Relayer 的接入

如果你（发卡方）部署了自己的 relayer，你的 App / 用户领取页应该把 POST 目标指向你的 endpoint，**不要**走我们的默认 relayer。这一步对用户透明——他们感知不到 gas 由谁付。

**我们不会强制 Relayer 路由**——卡片本身、合约本身都没有任何"指定 relayer"字段。完全由你的 App 决定。

## 信任路径回顾

```
设备签名
   │  (公开数据, 可被任何人观测/复制)
   ▼
Relayer 拿到签名
   │  (无法修改 to / amount / unlockAddress, 否则 ecrecover 失败)
   ▼
合约 ecrecover + transfer
   │
   ▼
资产到 to
```

**Relayer 唯一的"权力"是 不提交**——例如它可以拒绝服务（拒收某个 IP / 某张卡）。但这不会损失资产，用户换个 Relayer 即可。

这就是为什么我们说 Relayer 不是信任组件——它对资产**没有任何破坏能力**，只有**审查能力**，且审查可被旁路。

## FAQ

**Q：能用 ERC-4337 / Account Abstraction 替代 relayer 吗？**
理论上可以——把 withdraw 包装成 UserOp，通过 bundler 提交。但当前合约接口是普通 EOA call，没有内建 4337 支持。如果集成方有这个需求可以 fork 或在 App 层用 paymaster 包装。

**Q：Relayer 会不会泄漏用户隐私？**
我们的默认 relayer 收到的数据是 `(chainId, pool, unlockAddress, to, sig)`——这些都是签名一旦上链就完全公开的内容。我们的运营日志只保留必要的 abuse prevention 字段（IP + 时间戳），不长期留存。如果你介意，自托管。

**Q：如果你们的 Relayer 挂了怎么办？**
App 应该有 fallback：1) 自动切换到备用 relayer；2) 提示用户用自己的钱包提交。我们的参考 App 实现了第二种。

**Q：Relayer 能不能扣手续费？**
合约层面**不能**——合约不知道也不在乎是谁提交的。但 relayer 服务可以在自己 API 层面做付费/订阅墙（比如要求集成方付费才能用你的 relayer），这是商业层面的事。我们的默认 relayer 当前不收费。
