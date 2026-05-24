# 系统安全

本节从**接口和系统层面**说明 Hongbao 的安全保证、威胁模型与攻击面。不涉及固件实现、芯片内部细节、工厂流程——这些是闭源部分。

> 团队成员均为安全背景（含合约审计员）。当前阶段未做第三方审计；代码与接口完全公开，欢迎独立审计 [TBD: GitHub URL]。

## 安全目标

按重要性排序：

1. **资产只能转给 `to`**：链上资产仅在持卡人的明确授权下、转给持卡人指定的收款地址。
2. **签名一次性**：一张卡只能领一次，不能双花。
3. **资产可恢复**：未领取的资产在过期后能由发卡方赎回，不会永久卡死。
4. **去中心化**：合约无 owner / pause / 升级，发卡方与我们都不能随意操作链上资产。

## 威胁模型

**资产**：锁在 Pool 合约里的 ERC20 / ERC721 资产。

**潜在攻击者**：

| 类别 | 能力 | 例子 |
|---|---|---|
| 远程攻击者 | 网络侧 | 截获 BLE 流量、伪造 relayer 请求、front-running |
| 物理攻击者 | 拿到卡 | 拆卡、侧信道、电源故障注入 |
| 供应链攻击者 | 渗透生产环节 | 替换芯片、植入后门固件 |
| 内鬼 | 我们/发卡方/制卡厂员工 | 想办法预知/复制私钥 |

**信任假设**：

- secp256k1 + ECDSA + keccak256 安全
- 安全芯片厂商对 tamper-resistant 的承诺成立（私钥不可提取、HMAC 不可绕过）
- 链本身共识安全（不被 51% 攻击）
- 持卡人在按下"长按 10 秒授权签名"按键时，确实想授权当前 App 显示的收款地址

## 安全机制（按层）

| 层 | 机制 | 防御对象 |
|---|---|---|
| 安全芯片 | 私钥在芯片内生成、永不导出；防侧信道、防物理拆解封装 | 私钥泄漏、侧信道 |
| HMAC 绑定 | MCU UUID ↔ 安全芯片 slot 双向校验，启动时验证 | 换芯片攻击（把 MCU 焊到其他 secure element 上）|
| 身份验证 | identity key 的 ECDSA challenge-response | 假设备替换、会话内中间人 |
| 连接确认按键 | 长按 3s，10s 超时 | 远程蓝牙劫持 / 路过偷连 |
| 签名授权按键 | 长按 10s | 远程触发签名 / 误操作 |
| 一次性签名（固件层）| `sign_count > 0` 后 SIGN 永久 ERROR | 设备级双花 |
| EIP-712 签名 | 收款地址写入签名内容 | Relayer / MITM 改 `to` |
| 合约 ecrecover + 状态机 | 链上验签 + 标记 unlockedAt | 签名伪造、合约级双花、过期前赎回 |
| 合约无 owner / 不可升级 | 合约逻辑固定 | 我方/发卡方事后篡改规则 |
| Watchdog (IWDG) | 设备硬件看门狗 | 固件 hang 导致拒绝服务 |

每一层独立，多个机制互相不依赖。攻击者要拿走资产，需要同时绕过设备级一次性签名 **且** 合约级 unlockedAt 标记 **且** 物理按键 **且** ecrecover——目前为止没有已知方法。

## 攻击面与缓解

| 攻击 | 路径 | 缓解 | 残余风险 |
|---|---|---|---|
| BLE 嗅探 | 被动监听射频 | BLE 不传输任何秘密——签名是公开数据，私钥永不出芯片 | 无 |
| BLE 中间人改 to | 主动篡改帧 | `to` 是签名内容，改了 ecrecover 失败 | 无（资产层）|
| 假设备替换 | 攻击者整张换卡 | identity 公钥校验 + 物理外观/包装防伪 | 用户必须在线核对 identity（标准流程未默认；可由发卡方增强） |
| 远程触发签名 | 远程连蓝牙发 SIGN 命令 | 物理按键 3+10 秒；设备隔空无法触发 | 攻击者必须物理接触设备 |
| 路过偷连蓝牙 | 短暂物理接近发命令 | 必须长按 3 秒确认连接，10 秒超时 | 极短窗口可能 spam，但无法升级到签名 |
| 拆卡读私钥 | 物理破封读取安全芯片 | 安全芯片 tamper-resistant 设计 | 实验室级 ASIC 微观攻击 [取决于芯片厂商承诺]|
| 换芯片 | 把 MCU 焊到另一颗安全芯片 | HMAC 绑定校验失败，启动即卡死 | 同时换 MCU 和 secure element 等于换全卡，不构成本卡攻击 |
| 供应链 | 工厂植入后门固件 | 出厂前 SWD 锁定 + 工厂锁；公开 BLE 接口可独立验证设备行为 | 我们没做正式 secure boot；当前依赖 SWD 锁防固件提取 [TBD: 后续考虑 secure boot] |
| Relayer 改 to / 私吞 | 恶意 relayer | `to` 在签名里；relayer 改了 ecrecover 失败 | 无 |
| Relayer 拒绝服务 | relayer 不提交 | 任意 EOA 都能提交；fallback 多通道 | 用户须知如何手动提交（App 应内置 fallback） |
| Front-running / MEV | 抢跑 relayer 交易 | `to` 在签名里——抢跑只会用同样的 to 提交，资产仍到达预定地址 | 无（甚至给用户加速）|
| 双花/重放 | 重新提交 / 跨链重放 | 合约 unlockedAt + 设备 sign_count 双层；EIP-712 domain 绑 chainId + pool | 无 |
| 卡丢失 | 物理丢卡 | 卡 = 私钥；丢失视同丢钱包 | 过期后发卡方可 withdrawExpired 赎回，给用户补卡 |
| 用户被骗签到错地址 | 钓鱼/社工诱导填错 to | 签名前 App 应清晰展示 to；用户必须手动输入并确认 | 不能完全防御——是用户教育问题 |
| NFT 签到不能接收 ERC721 的合约 | App 没校验 to | 合约用 safeTransferFrom，会 revert，但**签名已消耗**——卡报废 | 集成方必须在 App 层校验 to；我们的参考 App 已做 |

## 不做加密的 BLE，安全吗？

是的。BLE 链路不启用 LE Secure Connections / pairing，**全程明文**。这是设计选择：

- 私钥永不通过 BLE 传输
- 签名是公开数据（最终上链人人可见）
- 设备身份用 ECDSA challenge-response 自证，不依赖 BLE pairing
- 物理按键是签名授权的真实闸门——不是加密通道

加 BLE 加密会让产线烧录、蓝牙调试、第三方 App 集成都更复杂，且不增加资产层安全性。我们刻意不做。

## 合约层不变量

下面是合约层面我们承诺的硬性不变量：

1. **签名只对当前 (chainId, pool) 有效**：domain 含 chainId + verifyingContract，跨链/跨合约签名 ecrecover 不通过。
2. **`to` 不可改**：写在签名内容里。
3. **`unlockedAt != 0` 后永久禁止 withdraw**：合约状态变量，无函数可清零。
4. **过期前 initiator 不可 withdrawExpired**：`require(block.timestamp >= cardExpire(...))`。
5. **withdrawExpired 不影响已 withdraw 的卡**：单调 revert / batch 静默跳过。
6. **没有 admin / owner / pause / upgrade 入口**：合约不存在这些函数。
7. **MIN_LOCK_TIME = 30 天**：常量，永久不可调。
8. **Factory `(asset, initiator)` 唯一性**：重复创建 revert。

## 设备层不变量

1. **私钥永不导出**：芯片内部生成、永不离开；芯片硬件防提取。
2. **HMAC 绑定**：每次启动校验 MCU UUID 与安全芯片 slot 是否匹配，否则停机。
3. **身份验证后才放开签名**：未通过 IDENTITY_CHALLENGE，SIGN 命令永远 AUTH_REQUIRED。
4. **物理按键不可绕过**：连接确认（3s）和签名授权（10s）都依赖按键事件，无法用 BLE 命令模拟。
5. **签名一次性（release 模式）**：`sign_count` 在签名后写入持久存储，再次 SIGN 永久 ERROR。
6. **工厂模式锁定不可逆**：FACTORY_LOCK 命令一次执行后无法回退（除非重新 SWD 烧录，但 SWD 已锁）。

## 最小信任设置（去信任审计 / 自助配置）

日常体验是 Hongbao 官方 App + 默认 Relayer——绝大多数发卡方和持卡人不需要碰下面这一节。

但如果你（发卡方 / 安全研究者 / 审计方）对 Hongbao 运营的信任度为零，仍然可以独立验证整套系统、独立完成发卡 + 领取的全流程：

- **合约公开** → 自审 / 第三方审计
- **任意 EVM 链** → 不依赖 Hongbao 运营任何链
- **自托管 Relayer** → 不依赖 Hongbao 的 API（项目方填入 Web Dapp，或完全不依赖 Hongbao 走脚本路径）
- **BLE 接口公开 + CLI 开源** → 可用开源 CLI 或基于公开 spec 自实现客户端（用于审计 / 自助取卡 / 测试场景；常态体验仍走官方 App，详见 [device.md](device.md)）
- **卡的固件闭源** → 但 BLE 接口公开，可独立验证：
  - GET_PUBKEY 拿到的 public key 是否真的对应 GET_ETH_ADDRESS
  - SIGN 返回的签名是否真的能被 ecrecover 恢复到 ETH 地址
  - SIGN 第二次是否真的会 ERROR
  - 所有这些都能在不接触固件源码的情况下验证

唯一无法去信任的部分：

- 安全芯片厂商对 tamper-resistant 的承诺
- HMAC 绑定确实没被绕过（依赖芯片厂的 slot lock 机制）

这两点是 hardware wallet 这一类产品的共同信任假设，与 Hongbao 设计无关。

## 已知限制 / 路线图

- 当前**无第三方审计**：早期阶段；按订单规模决定是否引入。
- **Secure Boot 未启用**：依赖 SWD 锁防固件提取。后续按需求评估。
- **Identity 公钥未默认上链/印在二维码**：身份验证依赖 App 自维护"期望的 identity"，部分场景下提供的安全收益有限。后续可以由发卡方在自己后端登记，App 在线核对。
- **NFT 变体的单元测试覆盖不全**：合约层 NFT pool 主测试在补，e2e 已通过。详情看仓库 README。

## 报告漏洞

如果你发现合约/接口层漏洞：[TBD: 安全联系邮箱 / 漏洞披露政策]

如果你发现卡片/设备层异常行为：[TBD: 同上]

我们会公开承认 + 修复 + 致谢报告者（按 responsible disclosure 流程）。
