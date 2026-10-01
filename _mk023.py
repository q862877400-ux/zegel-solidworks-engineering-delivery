import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
S = Path(r"D:\AI\SW\specs\023-helix-from-true-missing")
S.mkdir(parents=True, exist_ok=True)

spec = """# 023 · 从「真缺」里补第一条：螺旋线

**Status**: Implemented（轮 104）

## 背景
前四轮（`020`/`021`/`022`）都在**核样**，收益递减 ⇒ 本轮**换方向**：
从 `010` 的「真缺」档里**挑一条实现出来**。
`helix`（螺旋线）在 `022` 的核样里被确认**确实没有**
（`InsertHelix` 只登记在 API 名表里，没有实现）。

## 做法（铁律 1 + 4：缝合、不发明；签名以官方源为准）
* **来源**：`本项目自建` —— 依据是**官方 API**（合法来源之一：
  「官方 API 文档 → 决定接口选型与参数顺序」）；
* **签名两源互证**：
  * 出厂反射 `iface_sldworks.txt`：`Void InsertHelix(Boolean×4, Int32, Double×5)`（在 **IModelDoc2** 上）
  * `C:\\swapi\\types\\IModelDoc2\\InsertHelix.md`：10 个具名参数
  * ⚠ **两源一致** ⇒ 无冲突，不需要类型库裁决；
* **并入规则 2**（单位）：长度 `_mm`、角度 `_deg`，换算只在边界做一次（`mm()` / `deg()`）。

## ★★ 本轮抓到的两个错
### ① 枚举值**凭记忆写反了**
```
我写的（错）                        官方真值（两源一致）
height_and_pitch = 1          ⇒     height_and_pitch = 2
height_and_revolution = 2     ⇒     height_and_revolution = 1
```
**两源**：出厂反射 `enum_values_sldworks.txt` + `C:\\swapi\\enums\\swHelixDefinedBy_e.md`。
★ 这是铁律 4「**不凭记忆写标准值**」的**具体实例** —— 我在**写完之后、跑门禁之前**
停下来查了，才拦住。**契约测试现在把枚举值单独钉住。**

### ② 门禁抓到两处「改了东西没同步」
`union-level-audit.md`（能力 31→32）与 `union-coverage-matrix.md`（独家 68→71）
⇒ 都是正常流程，非缺陷。

## 判据
| ID | 判据 |
|---|---|
| SC-1901 | 10 个参数**顺序与类型**照官方，一个不差 |
| SC-1902 | ★ **枚举值**与官方两源一致（单独一段常量 + 独立测试）|
| SC-1903 | 单位换算在**边界**做一次（100 mm ⇒ 0.1 m；180° ⇒ π rad）|
| SC-1904 | 没建出来时抛**带原因**的 `RuntimeError`（"没选圆"）|
| SC-1905 | 来源块写明等级 **`stitched`** 且**无本机运行证据** |
| SC-1906 | `capabilities.yaml` 新增 `helix_and_spiral`（`stitched`），31 → **32** 条 |
| SC-1907 | 门禁 + 回归不退化（回归 **1054 passed**）|

## ⚠ 明确记下的限度
* **等级是 `stitched`，不是 `verified`** —— 只有静态证据，**本机从未建过螺旋线**；
* **前置条件未查证**（官方示例先选一个圆）；
* `Pitch` 与 `TaperAngle` 的**单位官方没写** ⇒ 本模块按同类推断处理，**已在 limitations 声明**；
* 只做**定距**；变距（`InsertVariablePitchHelix`）未实现。
"""

plan = """# 023 · Plan

**不重造**：照 `scripts/sw_mold.py` 的模块形式（来源块 + `get_com_member` 约定 + 参数照反射）。

## 步骤
1. 查 `helix` 是否真的缺（`InsertHelix` 只在 API 名表里）⇒ 确认缺
2. **两源**取签名（反射 + swapi md）⇒ 一致
3. 取官方**枚举值**（反射 + swapi）⇒ ★ **发现我凭记忆写反了**
4. 写 `scripts/sw_helix.py`（照并入规则 1/2/4）
5. 写契约测试（8 条，含枚举值与单位换算两条钉死）
6. 加 `capabilities.yaml` 条目（`stitched`）
7. 重生成地图/等级审计/digest + 同步报告数字
8. 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| **凭记忆写枚举值** | ★ 本轮真的犯了 ⇒ 改成**查两源**，并用测试钉住 |
| 把 `stitched` 说成 `verified` | SC-1905 用测试钉住"来源块必须写 stitched + 无运行证据" |
| 单位搞错（官方只写明 2 个）| 写明的用 `mm()`/`deg()`；**没写明的标明是同类推断** |
| 真机测试触发弹窗（轮 98 的教训）| ★ **本轮不做真机测试** —— 等级就写 `stitched`，诚实 |
"""

tasks = """# 023 · Tasks（全部完成，轮 104）

- [x] T-1901 确认 `helix` 确实没实现
- [x] T-1902 两源取签名（反射 + swapi）⇒ 10 参一致
- [x] T-1903 ★ **取官方枚举值** ⇒ **发现凭记忆写反了 1 和 2**
- [x] T-1904 写 `scripts/sw_helix.py`
- [x] T-1905 契约测试 `tests/test_sw_helix_contract.py`（**8 passed**）
  `→ 验收:` `python -m pytest tests/test_sw_helix_contract.py -q`
- [x] T-1906 加 `capabilities.yaml` 条目（31 → **32**）
- [x] T-1907 重生成地图 / 等级审计 / digest + 同步报告数字
- [x] T-1908 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""

converge = """# 023 · Converge

**Converged**: 2026-10-01（轮 104）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-1901 10 参顺序与类型照官方 | ✅ 契约测试 |
| SC-1902 枚举值与两源一致 | ✅ **本模块第一版写反了，已修** |
| SC-1903 单位换算在边界 | ✅ 100 mm ⇒ 0.1 m · 180° ⇒ π rad |
| SC-1904 没建出来抛带原因的错 | ✅ 消息含「圆」与 `InsertHelix` |
| SC-1905 来源块写明 `stitched` | ✅ 测试钉住 |
| SC-1906 能力条目 31 → **32** | ✅ `helix_and_spiral`（`stitched`）|
| SC-1907 门禁 + 回归 | ✅ `release_check` exit 0 · 回归 **1054 passed** |

## 二、★ 本轮的值在于**拦下了一个凭记忆写错的枚举值**
```
我写的（凭印象）              官方真值（两源一致）
height_and_pitch = 1    ⇒     height_and_pitch = 2
height_and_revolution = 2  ⇒  height_and_revolution = 1
```
⚠ **如果没停下来查，这个错会直接进仓库** —— 而且它**不会**被任何门禁抓到
（门禁查"名字在不在官方清单里"，**不查"值对不对"**）。
★ ⇒ 这正是 `docs/orphan-functions-not-runnable.md` 的同类问题：
**静态检查能覆盖的只是"存在性"，覆盖不了"正确性"。**

## 三、等级为什么是 `stitched` 而不是 `verified`
本模块**只有静态证据**（签名两源互核 + 8 条契约测试），
**本机从未建过螺旋线** ⇒ 按五级枚举**不得标 `verified`**。
⚠ 且本轮**主动不做真机测试** —— 轮 98 的模态框事故表明，
「需要前置几何」的建模工具在未满足前置时**会卡住会话**。
⇒ 与其冒险跑一个准备不足的测试，不如**如实标 `stitched`**。

## 四、未查证
* **前置条件**：官方示例先 `SelectByID2` 选一个圆；未选圆时的行为**未实测**；
* `Pitch` / `TaperAngle` 的**单位官方没写** ⇒ 本模块按同类推断（已在 limitations 声明）；
* **变距螺旋线**（`IFeatureManager.InsertVariablePitchHelix`）**未实现**；
* 「真缺」档还有 **131 条**（本轮补了 1 条）。
"""

for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)
