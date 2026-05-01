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

## Relayer 怎么被 App 选中

Hongbao 官方 App / Web 默认提交到 Hongbao 官方 Relayer。**项目方可以在 Hongbao Web Dapp 锁卡时填入一个自托管 Relayer URL**——这个 URL 写到批次元数据里。持卡人扫码领取时，App 会**同时把签名广播给两个 Relayer**：

```
                    ┌──► Hongbao 默认 Relayer ──► 链上 withdraw
设备签名 ──► App ──┤
                    └──► 项目方自托管 Relayer ──► 链上 withdraw
                         （仅当项目方在锁卡时填了 URL）
```

两个 Relayer 抢着提交，先打包成功的入链；另一个发的同样 calldata 在合约层会因为 `unlockedAt != 0` revert。**不会双花，不会冲突**——多花的只是另一边一笔 revert 交易的 gas（由该 relayer 自己承担）。

为什么这么设计：

- **Hongbao 默认 relayer 多链多项目方**——总会有延迟峰值，没法对所有客户都做最高优先级 SLA
- **项目方自托管 relayer 服务自家用户**——延迟通常低于默认 relayer
- **同时广播 = 取较快的那个**——持卡人体验上限，又不依赖项目方一定要自部署

合约层 `withdraw(unlockAddress, to, v, r, s)` 不限制 `msg.sender`——任何 EOA 都能调用。这意味着 Relayer 只是**纯运营组件**，对资产没有任何破坏能力。

| 场景 | 提交者 | 谁出 gas |
|---|---|---|
| 默认（项目方未填自托管 URL） | Hongbao 默认 relayer | Hongbao |
| 项目方填了自托管 URL | Hongbao 默认 + 项目方 relayer 双广播 | 哪个先成功哪个 |
| 自建客户端 + 用户付 gas | 用户自己钱包 | 用户 |

> "用户自己钱包付 gas" 这条路径**仅在自建客户端场景下存在**——Hongbao 官方 App 不暴露这个开关，默认走 Relayer 体验。

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

## 项目方自托管 Relayer 的接入

接入路径：

1. 部署你自己的 Relayer 服务（接受跟 Hongbao 默认 Relayer **完全相同的 POST 接口**——见上文 OpenAPI 草案）
2. 在 Hongbao Web Dapp 锁卡时，把你的 Relayer URL 填入批次配置
3. 完成 deposit 后，URL 会被写入批次元数据；持卡人扫码后，Hongbao 官方 App 会自动从元数据拿到这个 URL
4. App 提交签名时，**同时**广播给 Hongbao 默认 Relayer 和你的 Relayer——两个抢提交，先成功的入链，另一个会被合约 `unlockedAt != 0` 自然 revert

你的 Relayer 必须实现的接口形状：

```
POST <你的 endpoint>
Content-Type: application/json
Body: { chainId, pool, unlockAddress, to, v, r, s }
→ 200 { txHash, status }
```

跟 Hongbao 默认 Relayer 的接口对称，方便 App 用同一段代码同时广播。

**为什么要双广播而不是切换**：

- 如果切换（"有项目方 relayer 就只发那个"），项目方 relayer 一旦故障，持卡人卡死
- 双广播的稳定性来自冗余——任何一边能用，持卡人就能领
- 项目方 relayer 的额外好处：自家用户的领取交易优先级更高，延迟显著低于多客户共享的默认 relayer

**你不一定要部署 Relayer**——不部署就只走默认 relayer，体验仍然完整，只是延迟受 Hongbao 默认 Relayer 的多客户排队影响。规模不大 / 对延迟不敏感 / 不想运维 Relayer 的项目方完全可以略过。

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

**Q：如果 Hongbao 默认 Relayer 挂了怎么办？**
- 项目方填了自托管 Relayer 的批次：自托管 Relayer 仍在运行，签名照常上链。
- 项目方没填的批次：领取会延迟到 Hongbao 默认 Relayer 恢复。极端情况下持卡人也可以用任意 EOA 自行提交 `withdraw`（不依赖任何 Relayer），但这条路径目前只在自建客户端场景下有 UX 支持，不在官方 App 的默认开关里。

**Q：两个 Relayer 同时收到签名都成功打包，会双花吗？**
不会。合约层 `withdraw` 一次性把卡的 `unlockedAt` 标记为非零，第二笔 tx 进入 mempool 时即便能 broadcast，进合约时也会 revert。最终上链的只有一笔，多花的只是另一边的 revert gas。

**Q：Relayer 能不能扣手续费？**
合约层面**不能**——合约不知道也不在乎是谁提交的。但 relayer 服务可以在自己 API 层面做付费/订阅墙（比如要求集成方付费才能用你的 relayer），这是商业层面的事。我们的默认 relayer 当前不收费。
