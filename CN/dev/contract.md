# 合约接口

Hongbao 的卡片在硬件层只做一件事：对一个 32 字节摘要做 ECDSA secp256k1 签名。**摘要是什么、签名怎么用、最终怎么放款，由 chain-specific 的合约或脚本决定。**

我们为每个目标生态提供"标准合约"作为参考实现。集成方可以直接用、可以 fork 后扩展业务逻辑、也可以从零自实现——只要遵循"用 secp256k1 签名 + 单卡单签"的核心约束即可。

| 生态 | 标准合约 | 状态 |
|---|---|---|
| **EVM**（Ethereum / BSC / Polygon / Arbitrum / Base / ...） | `HongBaoTokenPool` (ERC20) + `HongBaoNFTPool` (ERC721) | 已开源 [TBD: GitHub URL] |
| **Bitcoin (Taproot)** | — | 按需开发 |
| **Cosmos / Tendermint** | — | 按需开发 |
| 其他 secp256k1 链 | — | 按客户需求评估 |

下文以 **EVM 参考合约** 为例展开接口细节。其他生态的接口按相同设计原则定义（锁仓、单签兑付、过期赎回、无特权），具体形式因链而异。

## 设计原则（跨生态通用）

1. **单卡单签**：合约层面记录"已兑付"标志，已领取的卡再次提交永久 revert。
2. **收款地址在签名内**：领取时签的内容包含收款地址，中间人无法改向。
3. **签名验证用 secp256k1 ECDSA**：链原生 ecrecover / 等价指令验签，与卡片签名兼容。
4. **去特权**：合约/脚本不持 owner、不可暂停、不可升级。
5. **可赎回**：过期后发卡方可取回未兑付资产。最小锁定时长由实现决定（EVM 参考合约：30 天硬编码）。

集成方做衍生开发时，只要保持上述五点，就符合 Hongbao 的安全约束；其余业务逻辑（动态费率、staking、多签、白名单等）自由扩展，但需自行审计。

---

## EVM 参考合约

公开仓库：[TBD: GitHub URL]
集成示例（含 viem）：仓库内 `integration-examples/`

两个变体共用同一套交互模型：

```
HongBaoTokenFactory  ──CREATE2──►  HongBaoTokenPool   (一个 ERC20, 一个 initiator)
HongBaoNFTFactory    ──CREATE2──►  HongBaoNFTPool     (一个 ERC721 collection, 一个 initiator)
```

每个 (asset, initiator) 部署一个独立 Pool，自己持有资产、自己存卡片状态、自己做 EIP-712 验签。Factory 仅做注册和确定性部署，不持有任何资金。

### EIP-712 签名 schema（两套合约共用）

```solidity
// Domain
{
  name: "HongBao",
  version: "1",
  chainId: <当前链>,
  verifyingContract: <pool 地址>
}

// Type
struct Withdraw {
  address unlockAddress;  // 卡片 ETH 地址
  address to;             // 收款地址
}

// TypeHash
keccak256("Withdraw(address unlockAddress,address to)")
```

Digest：`keccak256(abi.encodePacked("\x19\x01", DOMAIN_SEPARATOR, structHash))`
链上验证：`ecrecover(digest, v, r, s) == unlockAddress`

合约暴露 helper：

```solidity
function getWithdrawDigest(address unlockAddress, address to) external view returns (bytes32);
function DOMAIN_SEPARATOR() external view returns (bytes32);
function WITHDRAW_TYPEHASH() external view returns (bytes32);
```

不需要 nonce——`unlockedAt != 0` 后再 withdraw 直接 revert。
防跨链/跨合约重放——domain 绑定 `chainId + verifyingContract`。

### Pool 模式（仅 Token 变体）

ERC20 Pool 在构造时通过 `initiator` 决定模式：

| `initiator` | 模式 | deposit 调用者 | withdrawExpired 调用者 |
|---|---|---|---|
| 非零 | 限定 | 仅 initiator | 仅 initiator，全额取回 |
| `address(0)` | 开放 | 任何人 | 各 depositor 各取自己份额 |

NFT Pool 仅支持限定模式（`initiator == 0` 构造时 revert）。

### Token Pool 接口

```solidity
// 存款
function deposit(address unlockAddress, uint256 amount, uint256 lockTime) external;
function batchDeposit(address[] unlockAddresses, uint256 amount, uint256 lockTime) external;
//   首次：lockTime >= MIN_LOCK_TIME (30 天)
//   续充（同 unlockAddress 再次 deposit）：lockTime 被忽略，过期时间以首次为准

// 提取
function withdraw(address unlockAddress, address to, uint8 v, bytes32 r, bytes32 s) external;
//   任何人可调用。校验 ecrecover(digest, v, r, s) == unlockAddress 且未兑付。
//   全额转给 to，标记 unlockedAt = block.timestamp。

function withdrawExpired(address unlockAddress) external;
//   限定模式：仅 initiator；开放模式：任何 depositor 取自己份额。
//   严格 revert（无份额 / 未过期 / 已兑付都 revert）。
function batchWithdrawExpired(address[] unlockAddresses) external;
//   批量。无份额/已兑付的条目静默跳过。

// View
function cardTotal(address unlockAddress) external view returns (uint256);
function cardExpire(address unlockAddress) external view returns (uint256);
function cardUnlockedAt(address unlockAddress) external view returns (uint256);
function depositRecord(address unlockAddress, address depositor) external view returns (uint256);
function lockedToken() external view returns (address);
function initiator() external view returns (address);

function isLocked(address unlockAddress) external view returns (bool);
function isExpired(address unlockAddress) external view returns (bool);
function remainingLockTime(address unlockAddress) external view returns (uint256);

function getWithdrawDigest(address unlockAddress, address to) external view returns (bytes32);
function DOMAIN_SEPARATOR() external view returns (bytes32);
function WITHDRAW_TYPEHASH() external view returns (bytes32);
function MIN_LOCK_TIME() external pure returns (uint256);  // 30 days
```

### 任务卡（Task Card）

同一个 Token Pool 支持两种卡：

| 卡型 | 创建方式 | 行为 |
|---|---|---|
| **Plain card**（`taskCount == 0`） | `deposit` / `batchDeposit` | 全额一次性签名领取——上面描述的经典模型，已有集成无需改动 |
| **Task card**（`taskCount > 0`） | `depositWithTasks`（仅限定模式） | 份额拆成 `basicAmount` + 1~255 个哈希任务，分级解锁 |

**核心思路**：task card 的设备签名不再是"领全额"，而是**领基础份额 + 绑定收款地址**。绑定之后，每个任务由任何人提交预映像（preimage）解锁，资金强制流向绑定地址——**所以泄露预映像不会被冒领**。

```solidity
// 创建任务卡（仅限定模式）
function depositWithTasks(
    address unlockAddress,
    uint256 basicAmount,            // 设备签名领取的基础份额（可为 0）
    bytes32[] taskHashes,           // 每个任务的承诺哈希，长度 1..255
    uint256[] taskAmounts,          // 每个任务的金额，与 taskHashes 等长
    uint256 lockTime                // 首次 >= MIN_LOCK_TIME
) external;
//   卡片总额 = basicAmount + Σ taskAmounts
//   taskHashes[i] 必须等于：
//     keccak256(abi.encode(block.chainid, address(pool), unlockAddress, uint8(i), n_i))
//   其中 n_i 是项目方为该 (卡, 任务槽) 生成的预映像。
//   任务槽创建后不可变；后续 deposit 续充只进 basicAmount。

function batchDepositWithTasks(
    address[] unlockAddresses,
    uint256[] basicAmounts,
    bytes32[][] taskHashes,
    uint256[][] taskAmounts,
    uint256 lockTime
) external;
//   原子批量；任一失败整批 revert。

// 领基础份额 + 绑定收款地址（task card 语义）
function withdraw(address unlockAddress, address to, uint8 v, bytes32 r, bytes32 s) external;
//   task card：转 basicAmount 给 to（可能为 0），记 boundTo = to、unlockedAt。
//   任务槽保持可领，其资金后续强制流向这个 to。

// 解锁单个任务
function claimTask(address unlockAddress, uint8 taskIdx, bytes calldata n) external;
//   任何人可调用；资金强制打到 boundTo。要求：
//     1. 是 task card 且未 close
//     2. 设备签名已绑定 boundTo（否则 BasicNotCompleted）
//     3. 该任务槽未被领取
//     4. keccak256(abi.encode(block.chainid, pool, unlockAddress, taskIdx, n)) == taskHashes[taskIdx]

function batchClaimTask(
    address[] unlockAddresses,
    uint8[] taskIdxs,
    bytes[] preimages
) external;
//   批量；个别 revert 的条目静默跳过（通过 TaskClaimed 事件判断结果）。

// 过期赎回（task card）
function withdrawExpired(address unlockAddress) external;
//   task card：仅 initiator，收回全部剩余（未领 basic + 未领任务）并 close 卡片。
//   close 之后 withdraw / claimTask 都 revert。

// Task card 专属 View
function cardBasicAmount(address unlockAddress) external view returns (uint256);
function cardTaskCount(address unlockAddress) external view returns (uint8);   // 0 = plain card
function cardBoundTo(address unlockAddress) external view returns (address);   // 未绑定为 0
function cardClosed(address unlockAddress) external view returns (bool);
function task(address unlockAddress, uint8 taskIdx)
    external view returns (bytes32 hash, uint256 amount, uint256 claimedAt);
function taskKey(address unlockAddress, uint8 taskIdx) external pure returns (bytes32);
function computeTaskHash(address unlockAddress, uint8 taskIdx, bytes calldata n)
    external view returns (bytes32);  // 项目方承诺 / 领取方自检用
function MAX_TASKS_PER_CARD() external view returns (uint8);  // 255
```

**任务哈希的域绑定**：`keccak256(abi.encode(chainid, pool, unlockAddress, taskIdx, n))` 把每个预映像绑定到「这条链、这个 pool、这张卡、这个任务槽」——**跨链 / 跨 pool / 跨卡 / 跨槽都无法重放**。

**为什么泄露预映像无害**：`claimTask` 把资金强制打到 `boundTo`（用户首次签名时锁定的地址）。即便预映像被第三方截获，提交后资金也只会流向原持卡人——攻击者拿不走。前提是设备签名的地址绑定已经发生到一个可信 `to`。

**事件**：

```solidity
event TaskDeposited(address indexed unlockAddress, uint8 indexed taskIdx, uint256 amount, bytes32 hash);
event Withdrawn(address indexed unlockAddress, address indexed to, uint256 amount);   // task card：amount = 释放的 basicAmount
event TaskClaimed(address indexed unlockAddress, uint8 indexed taskIdx, address indexed to, uint256 amount);
```

> **状态**：task card 合约已在仓库实现（`pow` 分支）。配套的任务后端与数据看板仍在建设中。

### NFT Pool 接口

```solidity
// 存款（任选 pull / push 路径）
function deposit(address unlockAddress, uint256 tokenId, uint256 lockTime) external;
//   pull：initiator 先 approve 后调用。

function onERC721Received(address, address, uint256 tokenId, bytes calldata data)
    external returns (bytes4);
//   push：initiator 直接 collection.safeTransferFrom(initiator, pool, tokenId,
//                                                    abi.encode(unlockAddress, lockTime))

// 提取
function withdraw(address unlockAddress, address to, uint8 v, bytes32 r, bytes32 s) external;
//   合约内部用 safeTransferFrom，to 必须能接收 ERC721。
//   ⚠️ 让设备对错误的 to（如不实现 IERC721Receiver 的合约）签名 = 卡报废。

function withdrawExpired(address unlockAddress) external;
function batchWithdrawExpired(address[] unlockAddresses) external;
//   仅 initiator。batch 中已兑付/无 deposit 静默跳过；
//   单条 safeTransferFrom 失败也跳过（状态保留以便重试）。

// View
function cardTokenId(address unlockAddress) external view returns (uint256);
//   ⚠️ tokenId = 0 是合法值。判断卡是否存在用 cardExpire != 0。
function cardExpire(address unlockAddress) external view returns (uint256);
function cardUnlockedAt(address unlockAddress) external view returns (uint256);
function lockedCollection() external view returns (address);
function initiator() external view returns (address);
// ... 共用 view 同 Token Pool
```

### Factory 接口

```solidity
// HongBaoTokenFactory
function createPool(address token, address initiator) external returns (address pool);
function pools(address token, address initiator) external view returns (address);
function computePoolAddress(address token, address initiator) external view returns (address);

// HongBaoNFTFactory（接口对称）
function createPool(address collection, address initiator) external returns (address pool);
//   ⚠️ NFT Factory 拒绝 initiator == 0
function pools(address collection, address initiator) external view returns (address);
function computePoolAddress(address collection, address initiator) external view returns (address);
```

`(asset, initiator)` 全局唯一——重复 createPool 会 revert `PoolExists`。
`computePoolAddress` 支持部署前预测地址，方便后端预先索引或预 approve。

### 常量

| 常量 | 值 |
|---|---|
| `MIN_LOCK_TIME` | 30 天 |
| `WITHDRAW_TYPEHASH` | `keccak256("Withdraw(address unlockAddress,address to)")` |

### 事件

```solidity
// Token Pool
event Deposit(address indexed unlockAddress, address indexed depositor, uint256 amount, uint256 expire);
event Withdraw(address indexed unlockAddress, address indexed to, uint256 amount);
event WithdrawExpired(address indexed unlockAddress, address indexed depositor, uint256 amount);

// NFT Pool
event DepositNFT(address indexed unlockAddress, uint256 indexed tokenId, uint256 expire);
event WithdrawNFT(address indexed unlockAddress, address indexed to, uint256 indexed tokenId);
event WithdrawExpiredNFT(address indexed unlockAddress, uint256 indexed tokenId);

// Factory
event PoolCreated(address indexed asset, address indexed initiator, address pool);
```

事件确切签名以仓库 ABI 为准。

### 集成步骤（脚本化 / 自建客户端视角）

> 项目方走 Hongbao Web Dapp 不需要碰这一节——Web Dapp 已经把 deposit / withdraw / withdrawExpired 全部封装。下面的步骤面向 (a) 想脚本化批量操作的开发者团队；(b) 想 fork / 魔改合约后自己接入的集成方；(c) 去信任审计 / 自助取卡场景的客户端实现。

无论 Token 还是 NFT：

```
1. 从硬件设备读到 unlockAddress（卡的 ETH 地址）
2. 调 pool view（Token: cardTotal/cardExpire/cardUnlockedAt；NFT: cardTokenId/cardExpire/cardUnlockedAt）
3. 用户填入 to
   ⚠️ NFT 必须校验 to 能接收 ERC721
4. digest = pool.getWithdrawDigest(unlockAddress, to)
5. 设备 BLE SIGN 命令签 digest，得到 64B sig (r||s)
6. 推导 v：试 27 / 28，本地 ecrecover 选出能恢复到 unlockAddress 的那个
7. 任意 EOA（自家 relayer / Hongbao 默认 relayer / 项目方自托管 relayer）提交：
   pool.withdraw(unlockAddress, to, v, r, s)
```

签名脚本 / digest 本地打包 / 推导 v 这一套逻辑两个变体可复用。viem 示例代码见仓库 `integration-examples/`。

### 易错点速查

- **MIN_LOCK_TIME = 30 天**：硬编码。`lockTime < 30 天` revert。
- **续充忽略 lockTime（仅 Token）**：过期时间以首次 deposit 为准。
- **NFT 无续充**：第二次 deposit 同一 `unlockAddress` revert。
- **NFT to 校验**：合约内部 `safeTransferFrom`。让设备对一个不能接收 ERC721 的 `to` 签名 = 卡报废。
- **tokenId = 0 是合法值**：NFT 判断卡存在用 `cardExpire != 0`。
- **签名一次性**：`unlockedAt != 0` 后永久 revert；卡固件层独立维护 `sign_count`，双层互不依赖。
- **跨链共址**：同一卡的同一地址在所有 EVM 链都相同。理论上可在多链各 deposit 一份，但卡只能签一次——用户在哪条链领，其他链的资产卡死直到过期。

---

## 自实现合约时的最小契约

如果你要在新链上自实现 Hongbao 兼容合约（不论是 fork 我们的标准合约改业务逻辑、还是用其他链的语言从零写），保持这些不变量：

1. **Withdraw schema 包含 `(unlockAddress, to)`** 两字段，外加 chain-specific domain（chainId、合约地址或等价物）防跨链重放。
2. **签名验证用 secp256k1 ECDSA**，恢复地址等于 `unlockAddress`。
3. **链上记录"已兑付"标志**，已兑付状态下 withdraw 永久 revert。
4. **过期前不允许任何方式提取资产**（除了用卡签名之外）。
5. **过期后只允许 deposit 时记录的 initiator/depositor 取回**，且只能取回属于自己的份额。
6. **不暴露任何 admin / pause / upgrade 入口**。

满足这些约束的合约，能直接复用 Hongbao 的 BLE 协议 + App 体系，把卡片的签名能力接入到任意链上。

### 魔改 / 自部署 Pool 怎么被 Hongbao 官方 App 识别

Hongbao 官方 App 不写死任何一个具体 Pool 地址——只要 Pool 暴露规范的 ABI（`cardTotal` / `cardExpire` / `cardUnlockedAt` / `getWithdrawDigest` / `withdraw` 等）+ 实现规范的 EIP-712 domain（`name="HongBao"`, `version="1"`, `chainId`, `verifyingContract=pool`），App 就能识别并完成兑付。

接入方式：项目方在 Hongbao Web Dapp 锁卡时**填入自部署 Pool 的合约地址**——这个地址会写到批次元数据里，发卡时随卡分发；持卡人扫码后 App 从二维码 / 元数据拿到 Pool 地址，按规范 ABI + Domain 与之交互。

也就是说：

- **Hongbao 标准合约 + 标准 Factory 部署**：默认路径，零成本接入。
- **Fork 标准合约改业务逻辑（白名单 / 动态金额 / staking 等）+ 自部署**：保持本节列出的 6 条最小契约，仍走 Hongbao 官方 App。
- **从零自实现合约（同链 / 新链）**：同上，保持 6 条契约 + 规范 ABI + 规范 EIP-712 domain。
