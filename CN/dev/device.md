# 设备 BLE 接口

本节定义红包卡对外的接口契约：BLE 服务 / 特征值、二进制帧格式、命令表、状态机、二维码格式、签名流程。

## 这份 spec 是写给谁的

- **安全研究者 / 审计方**：独立验证设备行为，不需要看固件代码
- **想 fork / 魔改合约的集成方**：理解设备签什么、怎么签，配合 [contract.md](contract.md) 完整复现领取流程
- **极端去信任配置的发卡方**：自己实现 BLE 客户端做应急取卡 / 测试 / 审计，不依赖 Hongbao 任何运营服务

**这份 spec 不是写给"想做替代 App"的开发者的**。Hongbao 官方 App / Web 是唯一标准持卡人入口——硬件、客户端、合约三者紧耦合，统一审计、统一 UX、统一生态合作入口。日常体验请走官方 App。

> 固件代码闭源；本文档描述的全部是**对外接口**。任何尊重本接口的客户端都能正确驱动设备。

## 为什么 spec 公开但不发官方 CLI / SDK

**spec 公开**——这是 Hongbao 去信任承诺的一部分。即便我们的全部服务中断、官方 App 下线、Relayer 故障，任何拿到卡的人都能基于本文档自己实现一套客户端把资产取出来。这是合约去信任之外，硬件层去信任的硬保证。

**官方不发 CLI / SDK**——刻意如此。Hongbao 的核心入口体验是官方 App（也是与钱包 / 交易所 / Dapp 生态合作的接入点），我们不希望提供"开箱即用的替代客户端"分流官方 App 的体验路径。需要审计或测试的人按 spec 自己实现一份足够；想图省事跑替代客户端的，不在我们要服务的需求里。

**应急取卡**——如果你确实碰到了官方 App 不可用 + 你又急需立刻取出某张卡的资产，请联系 [TBD: 应急联系方式]，我们提供应急 CLI。这是人工通道、不是产品形态——常态用户用不到。

## 二维码格式

每张卡身上印有一张二维码，内容是一段 deeplink：

```
https://hongbao.digital/_c?ea=XXXXXXXX
```

| 字段 | 说明 |
|---|---|
| `https://hongbao.digital/_c` | 通用着陆页（自动跳转到 App 或 Web 客户端） |
| `ea` | ETH 地址前 4 字节（8 hex 字符） |

**完整 ETH 地址不在二维码里**——必须通过 BLE 读取。设计动机：

- 防止仅扫码就能批量收集卡地址做未授权 deposit
- 4 字节足够 App 在 BLE 扫描列表里定位"哪一张"（碰撞概率 1/2³² ，足够日常使用）

App 拿到 deeplink 后：

1. 解析 `ea` 前缀，BLE 扫描时只与 `hongbao_<ea>` 名称的设备建立连接
2. 连接后通过 `GET_ETH_ADDRESS`（命令 0x08）拿到完整 20 字节 ETH 地址

## BLE GATT 服务

| UUID | 类型 | 方向 |
|---|---|---|
| `0xFFFA` | Service | — |
| `0xFFFB` | Write Characteristic | App → 设备 |
| `0xFFFC` | Notify Characteristic | 设备 → App（需 enable CCCD） |

设备名形如 `hongbao_<前4字节地址 hex>`，例如 `hongbao_a1b2c3d4`。

## 二进制帧格式

```
请求 (App → 设备):  [CMD:1B] [LEN:1B] [PAYLOAD:0..255B]
响应 (设备 → App):  [CMD:1B] [STATUS:1B] [LEN:1B] [PAYLOAD:0..255B]
```

Notify 单帧上限 = BLE MTU = 20 字节，超过时设备会分片，每片以 `STATUS = MORE_DATA (0x80)` 标记，最后一片用真实状态码。

## 命令表（用户可见接口）

| CMD | 名称 | 访问级别 | Payload | 响应 |
|---|---|---|---|---|
| 0x01 | GET_PUBKEY | OPEN | — | 64B 签名公钥 |
| 0x02 | GET_IDENTITY | CONFIRMED | — | 64B 身份公钥 |
| 0x03 | IDENTITY_CHALLENGE | CONFIRMED | 32B 随机挑战 | 64B 签名 + 64B 身份公钥 |
| 0x04 | SIGN | IDENTIFIED | 32B digest | WAITING_BUTTON → OK + 64B 签名，或 TIMEOUT |
| 0x05 | VERIFY | OPEN | 96B (32B digest + 64B sig) | 1B (0=invalid, 1=valid) |
| 0x06 | SIGN_RECORD | IDENTIFIED | — | 4B count；如 >0 追加 32B digest + 64B 签名 |
| 0x07 | SLEEP | IDENTIFIED | — | 1B ack |
| 0x08 | GET_ETH_ADDRESS | OPEN | — | 20B ETH 地址 |
| 0x09 | GET_DIAG_LOG | IDENTIFIED | — | 分片诊断日志 |
| 0x0B | CONN_CONFIRM | — | — | 设备主动通知（连接确认状态） |

> 工厂模式专属命令（`GET_QR_DATA`、`FACTORY_LOCK` 等）在出厂锁定后永久禁用，普通用户/开发者**无法**触达。这里不列出。

### 状态码

| 代码 | 名称 | 含义 |
|---|---|---|
| 0x00 | OK | 成功 |
| 0x01 | ERROR | 通用错误（包括"设备已签名过"） |
| 0x02 | WAITING_BUTTON | 设备在等用户按按键 |
| 0x04 | TIMEOUT | 超时未按按键 |
| 0x07 | AUTH_REQUIRED | 会话未识别——先发 IDENTITY_CHALLENGE |
| 0x08 | RATE_LIMITED | 命令速率超限 |
| 0x09 | NOT_CONFIRMED | 连接未确认——先长按 3 秒 |
| 0x80 | MORE_DATA | 分片传输中，后面还有 |

## 访问级别

命令按三级会话状态门控：

| 级别 | 进入条件 | 可用命令 |
|---|---|---|
| **OPEN** | BLE 已连接 | GET_PUBKEY, GET_ETH_ADDRESS, VERIFY |
| **CONFIRMED** | 长按 3 秒确认连接 | + GET_IDENTITY, IDENTITY_CHALLENGE |
| **IDENTIFIED** | IDENTITY_CHALLENGE 通过 | + SIGN, SIGN_RECORD, SLEEP, GET_DIAG_LOG |

## 状态机

```
                    BLE connect
  ┌────────────┐ ──────────────► ┌────────────┐
  │ ADVERTISING│                 │  PENDING   │  红绿交替
  │ 绿灯慢闪    │ ◄────────────── │ (10s 闸门) │
  └─────┬──────┘  超时 / disconn └─────┬──────┘
        │                              │ 长按 3 秒
        │                              ▼
        │                        ┌────────────┐
        │       BLE disconnect   │ CONFIRMED  │  绿灯常亮
        │  ◄──────────────────── │            │
        │                        └─────┬──────┘
        │                              │ IDENTITY_CHALLENGE 通过
        │                              ▼
        │                        ┌────────────┐
        │       BLE disconnect   │ IDENTIFIED │  绿灯常亮，全功能
        │  ◄──────────────────── │            │
        │                        └─────┬──────┘
        │                              │
        │  长按 3s / 5min idle / SLEEP │
        ▼                              ▼
  ┌────────────────────────────────────────┐
  │     DEEP SLEEP（LED 全灭）             │
  │     唤醒：长按按键 3 秒                 │
  └────────────────────────────────────────┘
```

| 起始 | 事件 | 终态 | 行为 |
|---|---|---|---|
| ADVERTISING | BLE connect | PENDING | LED 红绿交替，每 2s 发 CONN_CONFIRM(WAITING_BUTTON) |
| PENDING | 长按 3s | CONFIRMED | 绿灯常亮，发 CONN_CONFIRM(OK) |
| PENDING | 10s 超时 | ADVERTISING | 断开，发 CONN_CONFIRM(TIMEOUT) |
| CONFIRMED | IDENTITY_CHALLENGE 通过 | IDENTIFIED | 全功能开放 |
| 任意已连接态 | BLE disconnect | ADVERTISING | 重置会话 |
| 任意态 | 长按 3s / 5min idle / SLEEP | DEEP SLEEP | 关电 |
| DEEP SLEEP | 长按 3s | ADVERTISING | 全量重新初始化 |

## 完整签名流程

```
App                                     设备
 │                                        │
 │ BLE connect                            │  → PENDING，LED 红绿交替
 │ ◄── CONN_CONFIRM(WAITING_BUTTON)       │  每 2s 心跳
 │                                        │
 │      用户长按 3 秒                      │  → CONFIRMED
 │ ◄── CONN_CONFIRM(OK)                   │
 │                                        │
 │ ── IDENTITY_CHALLENGE(32B 随机)──►     │  用 identity key 签名
 │ ◄── 64B 签名 + 64B identity pubkey     │  → IDENTIFIED
 │                                        │
 │ App 校验：pubkey == 二维码里的 identity │
 │  （如果二维码没带 identity，至少要保存 │
 │   首次见到的 identity 用于后续核对）   │
 │                                        │
 │ ── SIGN(32B digest) ──────────────►   │
 │ ◄── WAITING_BUTTON                     │  红灯闪烁
 │                                        │
 │      用户长按 10 秒                     │  用 signing key 签名
 │ ◄── OK + 64B 签名（r||s）              │  设备 sign_count→1，已用
 │                                        │
 │ App 推导 v（试 27/28）                 │
 │ App 把 (unlockAddress, to, v, r, s)    │
 │  发给 Relayer 或自行提交               │
```

### 签名内容是什么

设备签的是**32 字节摘要**（任意 32 字节）。设备本身**不知道也不验证**这个摘要的语义——只负责签。具体来说：

- App 调 `pool.getWithdrawDigest(unlockAddress, to)` 拿到 EIP-712 digest
- App 把这 32 字节通过 SIGN 命令送进设备
- 设备用 signing key 签，返回 64B 签名（`r || s`）

设备返回的签名**不带 v**。App 必须本地试两次 ecrecover（v=27 / v=28），选出能恢复到 `unlockAddress` 的那个 v，然后把 `(v, r, s)` 提交给合约。

### 身份验证为什么重要

签名命令 SIGN 在 IDENTIFIED 级别才可用。这意味着 App 必须先做一次 IDENTITY_CHALLENGE：

1. App 生成 32B 随机数发给设备
2. 设备用 identity key 签这 32B，返回签名 + identity 公钥
3. App 用返回的 identity 公钥验证签名（标准 ECDSA verify）
4. App 比对返回的 identity 公钥与"事先期望的 identity 公钥"

这一步防的是"假设备替换"——攻击者把真卡换成一个长得一样、能响应 BLE 的山寨卡片。攻击者不知道真卡的 identity 私钥，签名验证会失败。

> **二维码当前不携带 identity 公钥**——只有 ETH 地址前缀。所以"事先期望的 identity 公钥"在标准流程里是 None。即便如此身份验证仍有意义：它防的是**会话内中间人**——某个进程在 BLE 通道上代答；如果有人能持续 spoof 整张卡，确实能绕过这一步。补救：发卡方在生产时把 identity 公钥额外记录在自家服务端，由 App 在线核对（可选增强）。

## LED 行为

| 状态 | 绿灯 | 红灯 | 含义 |
|---|---|---|---|
| ADVERTISING（未签）| 慢闪 | OFF | 等待连接 |
| ADVERTISING（已签）| 慢闪 | 常亮 | 已用过的卡 |
| PENDING | 红绿交替 | 红绿交替 | 长按 3 秒确认 |
| CONFIRMED / IDENTIFIED（未签）| 常亮 | OFF | 命令通道开放 |
| CONFIRMED / IDENTIFIED（已签）| 常亮 | 常亮 | 命令通道开放，但 SIGN 会 ERROR |
| 等待签名按键 | 常亮 | 闪烁 | 长按 10 秒授权 |
| 错误/故障 | OFF | 常亮 | 加密初始化失败等致命错误 |
| DEEP SLEEP | OFF | OFF | 低功耗 |

## 速率限制

| 阶段 | 限制 |
|---|---|
| 未到 IDENTIFIED | 3 cmd/s |
| IDENTIFIED 之后 | 10 cmd/s |

超限返回 `RATE_LIMITED (0x08)`。正常用户场景碰不到这条线。

## 实现 BLE 客户端的最小步骤

如果你属于上面三类受众之一，需要自己实现一套 BLE 客户端（仅限审计 / 测试 / 应急取卡 / 配合魔改合约的集成场景），按下面的顺序走：

1. **解析二维码**：拿出 `ea` 前缀，确定要连的设备名 `hongbao_<ea>`
2. **BLE 扫描 + 连接**：建立 GATT 链接，订阅 0xFFFC notify
3. **等连接确认**：监听 CONN_CONFIRM；用户必须长按 3 秒
4. **身份认证**：发 IDENTITY_CHALLENGE，至少在会话内做一次签名验证
5. **读 ETH 地址**：发 GET_ETH_ADDRESS，得到完整 20B 地址
6. **读链上卡状态**：调 pool view 函数（cardTotal / cardExpire / ...）展示给用户
7. **构造 digest**：调 `pool.getWithdrawDigest(unlockAddress, to)`，得到 32B
8. **签名**：发 SIGN 命令 + 32B digest，用户长按 10s
9. **推导 v**：本地 try v=27/28，选能 recover 到 unlockAddress 的那个
10. **提交 withdraw**：自行提交、让用户的钱包提交、或 POST 到任意 relayer

**注意事项**：

- **不要**在客户端里持有 / 创建用户钱包私钥——Hongbao 协议刻意不做这件事
- **不要**假设设备能签多次——永远只能签一次
- **不要**忽略 ECDSA `s` 值的低-S 规范化（OpenZeppelin 的 ECDSA / 标准 `ecrecover` 都会处理；自己实现的库要注意）
- NFT 场景务必校验 `to` 能接收 ERC721——签错卡就报废

## Hongbao 官方实现

Hongbao 官方 App / Web 是绝大多数持卡人的实际使用入口：

- **Web**（已上线）— [TBD: URL]
- **Android**（开发中）
- **iOS**（Android 完成后移植）

普通持卡人使用任何一个即可——不需要碰 BLE spec，也不需要自己实现客户端。本文档面向的是上面"这份 spec 是写给谁的"列出的三类受众。
