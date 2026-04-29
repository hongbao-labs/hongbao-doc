# 发卡方端到端流程

从下单到用户领取的完整流程。本指南面向 ERC20 与 ERC721 两种资产，二者步骤几乎一致，差异在最后单独说明。

```
1. 采购实体卡 → 我方寄送
2. 收卡：扫码采集所有卡的 ETH 地址
3. 部署 Factory（一次性，整条链一次）
4. 创建 Pool（每种资产 + 每个 deposit 钱包一次）
5. deposit / batchDeposit：把资产锁到卡的地址
6. 派发实体卡给用户
7. 用户扫码领取（详见受领指南）
8. (可选) 过期后 withdrawExpired 赎回未领部分
```

---

## 1. 采购

按订单交付。我们会和你确认数量、目标链、资产类型（ERC20 / ERC721）。卡到货时已完成：

- 芯片内随机生成私钥
- HMAC 绑定 MCU + 安全芯片（防换芯片攻击）
- SWD 烧录锁定（防固件提取）
- 工厂锁（防出厂后恶意指令）
- 签名/验证/身份认证测试通过
- 深度休眠状态（零功耗）

你**不需要**做任何固件层操作。

## 2. 收卡：采集 ETH 地址

每张卡的二维码内容形如：

```
https://hongbao.digital/_c?ea=XXXXXXXX
```

`XXXXXXXX` 是 ETH 地址的前 4 字节（用于 App 端蓝牙快速识别）。**完整 ETH 地址需要通过蓝牙读取**——这是设计上的安全考虑，避免单纯扫码就能拿到地址做未授权 deposit。

实操上，我们提供一个采集脚本/工具（[TBD: 工具下载链接]），用蓝牙批量唤醒卡片、读取 ETH 地址，输出一个 `addresses.json`：

```json
{ "addresses": ["0xAbc...", "0xDef...", ...] }
```

后续 `batchDeposit` 直接吃这个文件。

## 3. 部署 Factory（一次性）

每条目标链上部署一次 Factory，之后所有项目方共用同一份 Factory（无许可、任何人可调用）。如果我们已经在该链上部署过，直接用现成的——查公开 [registry 地址列表 TBD] 或合约仓库 README。

如果链上还没有：

```bash
# Token Factory
forge script script/DeployFactory.s.sol --rpc-url $RPC --private-key $PK --broadcast

# NFT Factory
forge script script/DeployNFTFactory.s.sol --rpc-url $RPC --private-key $PK --broadcast
```

## 4. 创建 Pool

**每种 (资产, deposit 钱包) 组合部署一个独立 Pool。** 同一种资产、同一个 deposit 钱包 → 复用同一个 pool（已部署会 revert）。

```bash
# Token Pool
FACTORY=0x... TOKEN=0x<USDT 等> INITIATOR=0x<你的 deposit 钱包> \
forge script script/CreatePool.s.sol --rpc-url $RPC --private-key $PK --broadcast

# NFT Pool（INITIATOR 必填，NFT 不支持开放模式）
FACTORY=0x... COLLECTION=0x<NFT 合约地址> INITIATOR=0x<你的 deposit 钱包> \
forge script script/CreateNFTPool.s.sol --rpc-url $RPC --private-key $PK --broadcast
```

### Token Pool 模式选择

ERC20 Pool 支持两种模式（部署时选定，不可更改）：

| 模式 | `initiator` | 谁能 deposit | 谁能 withdrawExpired | 何时用 |
|---|---|---|---|---|
| **限定模式** | 非零地址 | 仅该地址 | 仅该地址 | 单一发卡方（推荐）|
| **开放模式** | `address(0)` | 任意地址 | 各 depositor 按份额取回 | 多人/众筹给同一批卡续充 |

NFT Pool 仅支持限定模式（构造时 `initiator == 0` 会 revert）。

## 5. Deposit：把资产锁进卡片地址

### ERC20

事前批准：

```solidity
IERC20(token).approve(pool, totalAmount);
```

批量存款（每张卡相同金额相同锁定时间）：

```bash
POOL=0x... AMOUNT_ETHER=100 LOCK_DAYS=30 ADDRESSES_JSON=./addresses.json \
forge script script/BatchDeposit.s.sol --rpc-url $RPC --private-key $PK --broadcast
```

或调合约：

```solidity
pool.batchDeposit(unlockAddresses, amount, lockTime);
// 单张：
pool.deposit(unlockAddress, amount, lockTime);
// 续充（限定模式同一卡多次 deposit，自动累加；lockTime 参数被忽略）：
pool.deposit(unlockAddress, additionalAmount, 0);
```

约束：

- `lockTime >= MIN_LOCK_TIME`（30 天，硬编码常量，不可调）
- 续充忽略 `lockTime`，过期时间以首次 deposit 为准

### ERC721

NFT 一卡一 tokenId，没有续充。两种 deposit 路径任选：

**Pull 路径**（先 approve，再调 deposit）：

```solidity
IERC721(collection).approve(pool, tokenId);
pool.deposit(unlockAddress, tokenId, lockTime);
```

**Push 路径**（直接 safeTransferFrom，data 里编码参数）：

```solidity
IERC721(collection).safeTransferFrom(
    initiator, pool, tokenId,
    abi.encode(unlockAddress, lockTime)
);
```

批量在脚本层面循环（任一失败整批 revert）：

```bash
POOL=0x... LOCK_DAYS=30 ENTRIES_JSON=./entries.json \
forge script script/BatchDepositNFT.s.sol --rpc-url $RPC --private-key $PK --broadcast
```

`entries.json`：

```json
{ "entries": [{ "unlockAddress": "0xAbc...", "tokenId": "1" }, ...] }
```

## 6. 派发

把实体卡寄给/送给用户。怎么送是你的事——内嵌贺卡、活动现场、快递邮寄都行。

派发时建议同时告知用户：

- 这是张红包卡，扫码就能领
- 过期时间（避免用户错过）
- 你的 App 入口（如果你套了自己品牌的领取页面）

如果用我们的标准领取页，二维码扫出来直接进 `https://hongbao.digital/...`，不需要额外引导。

## 7. 用户领取

详见 [持卡人领取指南](../receiver/guide.md)。简言之：用户扫码 → App 蓝牙连卡 → 输入收款地址 → 长按 10 秒签名 → 任意 EOA（默认我们的 relayer）提交 `withdraw(unlockAddress, to, v, r, s)`。

你不需要在领取流程中做任何事。链上事件（Token: `Withdraw`，NFT: `WithdrawNFT`）可以监听，用于更新自己后台的兑付状态。

## 8. 过期赎回未领资产

最早可在 deposit 后 `lockTime` 秒发起。**只有 deposit 钱包能调用**：

```solidity
// ERC20 限定模式：
pool.withdrawExpired(unlockAddress);
pool.batchWithdrawExpired(unlockAddresses);

// ERC20 开放模式：每个 depositor 各自调用，按自己份额取回
pool.withdrawExpired(unlockAddress);

// ERC721：
pool.withdrawExpired(unlockAddress);
pool.batchWithdrawExpired(unlockAddresses);
```

行为细节：

- 已被领取的卡 → ERC20 单调 revert，batch 静默跳过
- 没有 deposit 记录 → 单调 revert，batch 静默跳过
- ERC721 batch：单条 `safeTransferFrom` 失败也跳过、状态保留供后续重试
- 单调严格 revert 是为了让你能立刻定位错误；batch 静默跳过是为了让批量任务不会被一两条已领取的卡卡住

赎回的资产回到调用者钱包（限定模式 = `initiator`，开放模式 = 各 depositor）。

---

## 端到端示例：项目方做一次空投

假设你是某 DeFi 项目方，要给 1000 名 KOL 各空投 100 USDT，托管在 Polygon 上。

```
1. 下单 1000 张卡，目标链 Polygon
2. 收卡，用工具批量读取地址 → addresses.json
3. 部署 Polygon Token Factory（如尚未部署）
4. 创建 Pool：
     factory.createPool(USDT_POLYGON, my_deposit_eoa)
5. Approve + batchDeposit：
     usdt.approve(pool, 100_000 * 1e6)
     pool.batchDeposit(addresses, 100 * 1e6, 60 days)
6. 把 1000 张卡寄给 KOL，附说明卡片
7. KOL 各自扫码领取
8. 60 天后查未领的卡，batchWithdrawExpired 赎回
```

总链上交互：1 笔 `createPool` + 1 笔 `approve` + 1 笔 `batchDeposit`（按 batch size 拆几笔）+ 后续 `batchWithdrawExpired`。

## 注意事项

- **批量 size 上限**：单笔 `batchDeposit` 受 gas limit 约束，建议每批 50-100 张实测拆分。
- **NFT 收款地址校验**：让用户的 App 在签名前严格校验 `to` 能接收 ERC721——否则签了就报废。我们的参考 App 已实现，自建 App 一定要做。
- **过期时间最少 30 天**：合约硬编码，少于会 revert。
- **资产范围**：合约绑定一个具体 ERC20/ERC721 合约，无法在同一 pool 里混锁多种资产。要发不同资产就部署不同 pool。
- **跨链 deposit**：每条链各自独立部署/deposit。卡本身是地址形态的，同一张卡的地址在所有 EVM 链都是同一个；但卡只能签一次，所以**一张卡只能在一条链上锁、一条链上领**。
- **不要往同一张卡的地址在多条链锁资产**——只有一条链能被领取（用户随便选哪条链领，其他链的资产就再也签不出来）。
