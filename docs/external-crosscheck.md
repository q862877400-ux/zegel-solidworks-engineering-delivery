# 外部素材扫描结果：17 个本地仓库里有什么

> 扫描时间：2026-09-29 · 扫描对象：`C:\swprojects\` 下 19 个目录
> 方法：按 AGENTS.md §四.2 **先分许可**，只对 MIT 仓库读内容

## 一、许可分区（铁律 6）

| 处置 | 仓库 | 本次是否读取 |
|---|---|---|
| **MIT，可读可抄** | codestack · solidworks-api · SolidworksMCP-TS · CSharpAndSolidWorks · Solidworks-MCP · solidworks-skills · solidworks-auto-modeling · sw-ai-bridge · sw-api-skill · solidworks-com-automation-skill | ✅ 全部扫了 |
| **只读思想** | mcp-server-solidworks(AGPL) · q3ds-solidworks-mcp(AGPL) · pySW(GPL) · offline-solidworks-api-docs(无许可) · solidworks-build-mechanical-models(无许可) · ddeng-skills(全版权) | ❌ 未读内容 |
| **零接触** | SolidWorks-CAD · Solidworks-Crack（投递页 / 破解指南） | ❌ 未下载未读取 |

## 二、扫出来的「官方文档没有的实操写法」

**结论：有，但不多 —— 集中在一个仓库（`solidworks-skills`）的 CHANGELOG。**

### ① 参数个数的独立佐证（4 条，全部与我的反射一致）

`solidworks-skills` 声称的，我逐条回反射核过：

| 成员 | 仓库说法 | 我的反射 | 判定 |
|---|---|---|---|
| `SelectByID2` 第 8 参数 | 必须是 `VARIANT(VT_DISPATCH, None)`，不能用 Python `None` | 第 8 参类型正是 `Callout` | ✅ 对上 |
| `FeatureExtrusion2` | 23 参数 | 23 | ✅ 对上 |
| `FeatureExtrusion3` | 23 参数 | 23 | ✅ 对上 |
| `FeatureCut4` | 27 参数 | 27 | ✅ 对上 |
| `FeatureCut` 全系列 | 20 / 23 / 26 / 27 | **20 / 23 / 26 / 27** | ✅ **四个版本全对上** |
| `AddMate5` | 15 参数 | 在 **`IAssemblyDoc`** 上，15 参 | ✅ 对上（我第一次核时查错了接口 `IMate2`） |

> ⚑ 这批**不增加清单**，只**佐证**清单没错 —— 是「第二来源交叉验证」，
> 正好补上 AGENTS.md §四 要求的「两套都要用」里我此前缺的**第三方**这一路。

### ② 一个官方文档不会给的错误码

`codestack/solidworks-document-manager-api/getting-started/create-connection/index.md`：

> `Class is not licensed for use (Exception from HRESULT: 0x80040112)`

**`0x80040112` = COM 的「类未授权」**，出现在 PDM 建连接时。
对域 14 有用：看到这个码就是 **PDM 没许可**，不是代码写错。

### ③ pywin32 版本坑（`solidworks-skills/CHANGELOG.md`）

> `requirements.txt`：pywin32 >= 306 → **>= 311**（v306 有 >12 参数 API 问题）

⚠ 这条与 AGENTS.md §六 事实 3 呼应 ——「>12 参数 IDispatch 会失败」在
**特定 pywin32 版本上**确实存在，事实 3 说这条说法「是错的」指的是
**当前版本**不成立，不是说它从来没成立过。两条要合起来看。

## 三、扫不到的东西（明确记为「没有」）

| 域 | 结论 |
|---|---|
| Simulation 仿真 | 11 个 MIT 仓库**零实现**（与 AGENTS.md §六 事实 13/14 一致） |
| Motion Study | 零实现（同上） |
| DimXpert / GD&T | 零命中 |
| PDM | 只有 codestack 的 VBA 示例，无 Python |
| Routers / Composer | 只有零星片段 |

## 四、能不能抄进本仓库

**能抄的（MIT）**：
- 那 6 条参数个数的**交叉佐证** → 写进 `docs/external-crosscheck.md`，作为清单正确性的第二来源
- `0x80040112` 的含义 → 写进域 14 的说明

**不能抄的**：
- `solidworks-skills` 的 CHANGELOG 原文（它是 MIT，但内容是**它自己**的
  变更记录，抄进本仓库会造成来源混淆）⇒ **只取经我反射核实过的结论，不抄文本**
- 所有 READ-ONLY 仓库的任何内容

## 五、对清单的影响

**零。** 本仓库的 12 份官方 API 索引来自对官方 interop 程序集的反射，
外部仓库提供的是**佐证**而非**补充**。

> 这是一句重要的实话：**外部仓库没能补上任何官方 API 清单里没有的东西。**
> 它们的价值在于「证明我没抄错」，以及「提供官方文档没有的调用坑」。
