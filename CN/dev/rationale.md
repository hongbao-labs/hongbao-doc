# 设计原理 (Design Rationale)

这份文档解释 Hongbao 协议每一项设计选择**背后的"为什么"**——不是它做什么（其他 dev 文档讲），而是它为什么这么做、规避了哪些已知失败模式、付出了哪些代价。

> **配合阅读**：[architecture.md](architecture.md) 看系统架构、[contract.md](contract.md) 看合约接口、[device.md](device.md) 看设备 BLE 协议、[relayer.md](relayer.md) 看 Relayer、[security.md](security.md) 看威胁模型。本文档是这五份的"动机层"伴侣。

## 受众

- 想理解每一项设计决策动机的开发者 / 集成方
- 评估 Hongbao 是否适合自己业务场景的发卡方技术负责人
- 安全研究者 / 审计方
- 想 fork 协议或基于 Hongbao 标准做衍生开发的团队

---

## 一、核心设计原理：架构层非托管

> "不碰资金"不是运营策略，是**写进协议的硬约束**。本节解释怎么实现的、为什么重要。

### 1.1 私钥从未存在 Hongbao 任何系统中

| 机制 | 防护对象 |
|---|---|
| 芯片内 TRNG 自生成 secp256k1 私钥 | 出厂前任何人/机器读取 |
| HMAC 绑定 MCU UUID 与 secure element slot | 换芯片攻击（焊到其它 secure element 上）|
| SWD 烧录后锁定 | 固件提取与注入 |
| 工厂模式锁定不可逆 | 出厂后特权指令触达 |
| 安全芯片 tamper-resistant 设计 | 物理拆解、侧信道 |

我们公司、制卡厂、发卡方、连持卡人自己都**没有任何方法**导出这把私钥。详见 [device.md § HMAC 绑定](device.md) 和 [security.md § 设备层不变量](security.md)。

### 1.2 资产不在 Hongbao 控制下

合约设计强制了非托管：

- **Pool 合约 immutable**：constructor 之后所有状态变量都不可修改。无 owner、无 admin、无 pause、无升级路径
- **`withdraw(unlockAddress, to, v, r, s)` 不检查 `msg.sender`**：任何 EOA 都能调用，合约只验签 + 转账
- **`withdrawExpired` 仅限 initiator 在 30 天后调用**：发卡方对未过期资产有 0 控制权
- **CREATE2 确定性部署**：项目方部署前就能预测 Pool 地址，不依赖 Factory operator

详见 [contract.md § Pool 接口](contract.md)。

### 1.3 Relayer 是便利工具，不是必经路径

合约层 `withdraw` 不限制 `msg.sender` 意味着：

- Hongbao 默认 Relayer 只是 zero-config gas 代付
- 项目方可自托管 Relayer，App 同时双广播抢提交
- 持卡人可用任意 EOA 自行提交（仅限自建客户端场景）
- **任意一方拒绝服务都不影响最终领取能力**

详见 [relayer.md § Relayer 是什么](relayer.md)。

### 1.4 这种结构的实际后果

- 公司层面合规接触面最小：技术与硬件供应商，**不是**资金中介
- 卡的领取能力**由协议本身保证**，独立于任何中心化服务的运营状态
- 任何一方（我们 / 发卡方 / 制卡厂）都没有能力私吞资产或冻结领取——这是 cryptographic guarantee，不是 organizational policy

### 1.5 任务卡的信任分层（重要）

任务卡（task card）引入了一个 plain card 没有的角色：**任务 verifier**——它判定"用户是否真的完成了任务"，然后把任务槽的预映像 `n_i` 释放给用户。这是协议里**唯一的新信任点**，必须诚实区分两层：

| 层 | 信任假设 | 最坏情况 |
|---|---|---|
| **基础份额（basic）** | 完全去信任——纯设备签名 `withdraw` 领取 | 无 |
| **任务份额（task）** | 依赖 verifier 释放预映像 | verifier 拒绝释放 → 用户拿不到 bonus → 过期后 initiator 赎回 |

关键：**verifier 无法偷钱**。`claimTask` 把资金强制打到用户首次签名锁定的 `boundTo`——verifier 最多只能"不给你解锁的钥匙"，不能把钱重定向到自己。预映像泄露同理无害。

**verifier 由谁运营是可配置的**：预映像由项目方生成；任务完成判定可以托管在 Hongbao Web，也可以由项目方自建后台——**完成判定权在发卡方手里**。

> 所以 task card 的正确表述是：**basic 层 trustless，task 层是 verified-unlock（有信任点，但资金安全 + 可赎回兜底）**。不要把任务卡也宣称为完全零信任。

---

## 二、损失模式 → 架构对应

[issuer/overview.md](../issuer/overview.md) 列了发卡方在传统纸片卡 / 兑换码场景下面临的 5 个损失模式。本节展开**每个损失模式具体被哪些架构特性规避**。

### 2.1 视觉泄露 / 晒单灾难

**威胁模型**：攻击者通过照片、直播、屏幕截图、社媒晒单等方式获得卡的领取信息。

**关键架构特性**：

1. **QR 码内容仅是 ETH 地址前缀指针**，不是私钥也不是签名。攻击者拿到 QR 照片只能查看链上余额，**不能签名、不能转移**
2. **签名命令必须经过 IDENTIFIED 会话级别**：先 BLE 连接 → 长按 3 秒确认（升到 CONFIRMED）→ IDENTITY_CHALLENGE 通过（升到 IDENTIFIED）→ SIGN 命令需要再长按 10 秒
3. **签名内容包含收款地址**：即便攻击者能远程发 SIGN 命令（实际不可能，需要物理按键），也无法修改 `to` 地址

**对比纸片卡**：私钥 / seed phrase 一旦视觉暴露 = 资产损失，无任何救济。Brazilian YouTuber $60K 案、DEFCON Casascius hologram 演示都是反例。

详见 [device.md § 访问级别 / 状态机](device.md) 和 [contract.md § EIP-712 签名 schema](contract.md)。

### 2.2 内部盗窃 / 供应链攻击

**威胁模型**：印厂员工、包装工、物流人员、仓库管理员在卡片到达收件人之前，私自获取或复制私钥。

**关键架构特性**：

1. **私钥在芯片内由 TRNG 在出厂线上自生成** —— 工厂任何环节都没有"明文 seed phrase"可以拷贝
2. **HMAC 绑定 MCU UUID 与 secure element slot** —— 换芯片攻击启动即停机
3. **SWD 锁 + 工厂模式锁** —— 出厂后即便有物理控制权也无法重新提取或植入
4. **设备 ETH 地址即唯一防伪 ID** —— 项目方可在收货时抽样比对地址，识别篡改

**残余风险**：实验室级 ASIC 微观攻击仍理论可能（依赖芯片厂的 tamper-resistance 承诺）—— 这是所有硬件钱包共有的边界，与 Hongbao 协议设计无关。

**对比纸片卡**：Home Depot 案显示——**有正规企业流程的环境下**，单一员工凭内部访问权限就能在 16 个月内盗取 $4M。纸片卡的私钥从打印机出来到被涂层覆盖前，任何看到它的人都能记下来。

详见 [security.md § 攻击面与缓解](security.md)。

### 2.3 Breakage / 过期沉没

**威胁模型**：发卡方派出去的卡片，相当大比例从未被领取（行业基准 10-50%）。资产沉没，发卡方真金白银投入回不来。

**关键架构特性**：

1. **`withdrawExpired(unlockAddress)`**：30 天锁定期满后，Pool 的 `initiator` 调用此函数即可把未领取份额全数转回 deposit 钱包
2. **`batchWithdrawExpired(unlockAddresses[])`**：批量赎回，已兑付 / 无 deposit 静默跳过，单笔失败不影响其他
3. **EIP-712 domain 绑定 `chainId + verifyingContract`**：跨链 / 跨合约重放不可能，每个 Pool 的 breakage 完全可控

**Hongbao 把这个损失模式从 10-50% 降到 0**——这是单一最大的 dollar 价值差异。

详见 [contract.md § Pool 接口](contract.md)。

### 2.4 Sybil 攻击 / 机器人薅羊毛

**威胁模型**：链上空投把代币撒向钱包地址列表，机器人农场用脚本批量生成钱包伪装真实用户领取，发卡方付钱但代币没到真人手里。

**关键架构特性**：

1. **物理卡 + 物理按键**：脚本无法批量"按按键 10 秒"
2. **IDENTITY_CHALLENGE**：每张卡有独立的 identity key，假设备无法绕过
3. **设备 sign_count 单调递增**：单卡只能签一次，没有"刷量"路径
4. **`unlockedAt != 0` 永久 revert**：合约层独立的 anti-replay

发卡方使用 Hongbao = 主动选择把 sybil 攻击面从"无限"压到"卡的实际数量"。

详见 [device.md § 完整签名流程](device.md) 和 [contract.md § withdraw 验证](contract.md)。

### 2.5 多链 SKU 复杂度

**威胁模型**：项目方在 Polygon + BSC + Solana 各做活动，纸片卡形式必须做 3 种独立 SKU（私钥编码 / 钱包导入 / 兑换文档不同）。库存复杂、MOQ 分散、单价上升。

**关键架构特性**：

1. **secp256k1 是几乎所有主流公链共用的签名曲线**：Bitcoin（含 Taproot）、所有 EVM、Tron、Cosmos 系、Litecoin / Doge / BCH 原生支持；Solana / Sui / Aptos 也已通过 precompile / 升级支持
2. **设备本身 chain-agnostic**：固件只对 32 字节摘要做 ECDSA 签名，**不关心摘要代表哪条链上的什么交易**
3. **要支持新链只需在那条链上部署对应的"锁仓-签名验证-放款"合约**——卡可以原样使用

**结果**：一个 SKU 适配所有 secp256k1 链，库存 / MOQ / 物流复杂度从 N 变 1。

详见 [README § 一张卡，多链通吃](../README.md#一张卡多链通吃)。

---

## 三、协议级差异化论证

### 3.1 vs 硬件钱包

| 维度 | 传统硬件钱包 | Hongbao |
|---|---|---|
| 私钥管理 | 用户自己生成 + 备份 seed phrase | 芯片自生成、永不导出，**没有 seed phrase**这个概念 |
| 签名次数 | 多次（用户长期持有） | **单次**（设计承诺 + 固件 + 合约三层强制） |
| 资产模型 | 用户自己持有任意资产 | 发卡方 deposit 到协议合约绑定到卡地址 |
| 谁验证签名 | 用户自己的钱包 / dApp | Hongbao 标准合约 `ecrecover` |
| Recovery model | seed phrase 备份 | **不可恢复**，过期由发卡方赎回再补卡 |
| 商业角色 | 卖给最终用户的安全产品 | 卖给资产分发方的协议组件 |

**核心差别**：硬件钱包是"产品"（用户买回去自己用、长期持有）；Hongbao 是"协议组件"（项目方采购给特定收件人、用一次完成所有权转移）。**两者解决的问题集几乎不重叠**。

### 3.2 vs 资金托管型加密礼品卡

| 维度 | 资金托管型礼品卡 | Hongbao |
|---|---|---|
| 资金路径 | 用户付款 → 平台账户 → 平台兑付 | 项目方自锁合约 → 用户直接从合约提取 |
| 平台是否能冻结 | 能（平台余额是平台账目） | 不能（合约无 admin / pause） |
| 平台是否能挪用 | 理论能（取决于内控） | 不能（合约无 admin key） |
| 平台运营状态变化 | 用户余额可能归零 / 沉淀资金归属不清 | 卡的领取能力**由协议本身保证**，独立于公司运营 |
| 监管接触面 | 资金中介类金融牌照（重监管） | 技术与硬件供应商 |
| 跨链 / 跨资产 | 单一币种或平台支持的少数 | 任意 secp256k1 链 / 任意 ERC20 / NFT |

**核心差别**：资金路径在不在你（发卡方）手里。Hongbao 永远在；资金托管型礼品卡永远不在。

### 3.3 vs 链上空投（无实体载体）

| 维度 | 链上空投 | Hongbao |
|---|---|---|
| Sybil 风险 | 高（48% token 被机器人捕获） | 物理筛选机器人无法过门 |
| 真实用户筛选 | 链上行为画像（不可靠） | 发卡方控制实物分发渠道 |
| 新用户 onboarding | 收件人需已是钱包活跃用户 | App 引导新用户完成钱包/交易所注册 |
| 未领取赎回 | 通常无法回收 | 30 天后 `withdrawExpired` 全数回收 |
| 物理 / 社交载体 | 无 | 实体卡，可联名定制，可社交礼物 |

**核心差别**：空投是"撒种子，看哪个发芽"；Hongbao 是"精确递交"。

---

## 四、设计取舍 (Trade-offs)

我们刻意做了一些限制——这些不是 bug，是为了换更强保证而付出的代价。

### 4.1 30 天最小锁定期硬编码

- **为什么**：防止发卡方临时反悔挪用，给持卡人足够时间领取，避免与短锁定期产生扯皮
- **代价**：无法做"24 小时限时领取"等短期场景

### 4.2 卡只能签一次

- **为什么**：bearer instrument 模型必须有"已用"状态防双花
- **代价**：领取人无法分多次取出、无法变更收款地址、无法把同一张卡发给多人共享

### 4.3 私钥不可备份

- **为什么**：任何"备份"都意味着多了一份攻击面，违背"持卡即所有"承诺
- **代价**：卡丢失 / 损坏 = 资产需要等过期赎回再补卡（30 天延迟）

### 4.4 没有官方 SDK / CLI 仅作为审计工具公开

- **为什么**：维持 UX 一致性、统一固件审计与生态合作入口、防止山寨客户端误导用户
- **代价**：开发者集成需要按 BLE spec 自实现；分流路径有限

### 4.5 合约不可升级

- **为什么**：任何升级路径都意味着 admin key 或时间锁，违背零信任承诺
- **代价**：发现重大问题只能发新版本合约（新 Factory），老 Pool 按部署时逻辑运行

### 4.6 不发原生币只发 wrapped token

- **为什么**：原生币不走 ERC20 接口，需要单独合约。统一 ERC20 接口降低实现复杂度和审计成本
- **代价**：发卡方需先把原生币 wrap 成 WETH/WBNB 等再 deposit

---

## 五、信任模型边界

### 必须信任的

1. **芯片厂商**对 tamper-resistant 的承诺（私钥不可提取、HMAC 不可绕过）
2. **secp256k1 + ECDSA + keccak256** 这套密码学原语（与以太坊本身共享假设）
3. **持卡人**自己保管好卡片
4. **链本身**共识安全（不被 51% 攻击）
5. **（仅任务卡的任务份额）任务 verifier** 会在用户完成任务后释放预映像——但 verifier 无法偷钱，最坏只能拒绝释放（详见 § 1.5）

### 不需要信任的

- Hongbao 公司的运营状态（不持有任何卡的私钥；合约无 admin；服务暂时不可用不影响已发出卡的可领性）
- 发卡方（不能改你的收款地址；不能在过期前撤回）
- App（行为可审计——所有命令都通过公开的 BLE 接口与设备 / 合约交互，改签名内容会让 ecrecover 失败）
- Relayer（任意 EOA 都能当 Relayer；可同时广播到多个 relayer 抢提交）
- BLE 链路（不加密——但传输的内容里没有秘密；签名是公开数据）

详见 [security.md § 信任模型](security.md)。

---

## 六、为什么 BLE 链路不加密

短答：**资产层安全性不依赖 BLE 加密，加密只会增加产线 / 调试 / 集成成本**。

- 私钥永不通过 BLE 传输
- 签名是公开数据（最终上链人人可见）
- 设备身份用 ECDSA challenge-response 自证，不依赖 BLE pairing
- 物理按键是签名授权的真实闸门——不是加密通道

详见 [security.md § 不做加密的 BLE，安全吗？](security.md)。

---

## 七、未来扩展方向

### 7.1 App 客户端开源（UX 层 trustless）

当前协议层已 trustless（合约 + BLE spec + Relayer 全部 permissionless），UX 层仍依赖官方 App。开源 App 客户端代码将让 UX 层依赖也归零。时间表 [TBD]。

### 7.2 跨生态标准合约

当前 EVM 全系（ERC20 + ERC721）已发布。Bitcoin（Taproot）、Solana、Sui、Aptos、Cosmos 等按客户需求评估开发。所有这些链原生支持 secp256k1 验签——卡片本身无需修改。

### 7.3 资产类型扩展

ERC1155、原生币、项目方自定义合约按订单定制。详见 [contract.md § 自实现合约时的最小契约](contract.md)。

### 7.4 第三方 Relayer 生态

`withdraw` 不限制 `msg.sender` 意味着 Relayer 是开放角色——任何团队都能基于 OpenAPI 草案运行兼容 Relayer，App 自动双广播。详见 [relayer.md § 自托管 Relayer](relayer.md)。

---

## 参考资料

- [architecture.md](architecture.md)：系统架构总览
- [contract.md](contract.md)：合约接口规范
- [device.md](device.md)：设备 BLE 协议
- [relayer.md](relayer.md)：Relayer 角色
- [security.md](security.md)：安全模型
- 业务侧文档：[issuer/overview.md](../issuer/overview.md)、[receiver/overview.md](../receiver/overview.md)
