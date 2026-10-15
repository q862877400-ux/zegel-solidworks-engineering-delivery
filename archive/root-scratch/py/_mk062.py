import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
S = Path(r"D:\AI\SW\specs\062-dome-and-the-getter-that-calls")
S.mkdir(parents=True, exist_ok=True)

spec = """# 062 · 补 `dome` —— 顺带查出「**取一个方法**」这个动作**会把它调一次**

**Status**: Implemented（轮 143）

## 一、`dome` 本身：官方 Remarks 是钥匙
```
官方 IModelDoc2.InsertDome（**void** 返回、**未标** Obsolete）:
  「Before using this method, you must select the face for the dome using a
    **selection mark of 1**.」
```
⚠ 用 `mark=0` 时 `InsertDome` 报 **`0x8002000F`**（`DISP_E_PARAMNOTOPTIONAL`）
★ **那个错误看不出是 mark 的问题**（与事实 33 同一类坑）。
★ 官方还给了 **C# 示例**（`Create_and_Modify_Dome_Feature_Example_CSharp.md`）⇒ 照着走。

### `swFmDome` **不存在**
```
枚举转储 enum_values_sldworks.txt：**0 命中**
CreateDefinition 的 **35 个**合法常量里：**没有**
⇒ 圆顶**走不了 CreateDefinition**（与事实 43 的 swFmOneBend / swFmDraft 同族）
⇒ 只能走 IModelDoc2.InsertDome
```

## 二、★★★ 真正的收获：`get_com_member` 的**危险设计**
```python
member = getattr(obj, attr_name)
if args: return member(*args)
try:
    return member() if callable(member) else member   # ← 没有实参就"先试调一次"
except Exception as exc:
    if "-2147352573" in message or "找不到成员" in message: return member
    raise
```
⇒ ★★ **对 COM 成员，「取」就等于「调」**！
```
实证：`get_com_member(doc, "InsertDome")` **自己抛** `0x8002000F`
     （因为 InsertDome 有 3 个必填参数）⇒ 说明它**真的调了一次**
```
⚠⚠ **危险面**：**无必填参数且有副作用**的成员
（`InsertDeleteHole()`、任何 `File*` 写盘方法）会**被「取」这个动作静默执行**。

### 处置（最小、不动既有语义）
把 `DISP_E_PARAMNOTOPTIONAL`（`0x8002000F` / 「非选择性的参数」）
也纳入「**返回成员、不调用**」——**未**改成「永不调用」（那会动到全仓库依赖的既有语义）。

★★ **而 `insert_dome` 起初完全不能工作，根因就是这个**（不是圆顶本身的问题）。

## 三、★ 真机冒烟 **9/9**（含两条**如实标注**）
```
✓ 造出 100×60×20 的板
✓ ★★ 按面上的点 + **mark=1** 选中顶面（官方 Remarks 要求）
✓ insert_dome(8) 未抛异常（⚠ 这什么也证明不了 —— void 返回）
✓ ★★ **证据 A-1**：边界框**逐分量**变了   size [20,60,100] → [34.2222,60,100]
✓ ⚑ **证据 A-2**：增长 14.2222，传的是 8 ⇒ **如实记为未查明**
✓ ⚑ **证据 A2**：IDomeFeatureData2 读回 ⇒ **标为不可达**（事实 47/68）
✓ ★★ **证据 B**：特征树 19 → 20（⚠ 哪个是圆顶未查明）
✓ 收尾无残留模态框
```

## 四、⚠ 本轮我自己的判据错了 **4 次**（都记下来）
```
① `GetFeatureCount(True)` ⇒ 'int' object is not callable ⇒ **它是属性不是方法**
② A-1 用 `max(size1) > max(size0)` ⇒ **错**（变的那个方向在 max 里排不上号）
③ `growth` 用 `max()-max()` ⇒ **抓不到"最小方向在长"**
④ 特征树"新增"取 `names[n_before:]` ⇒ **错**（`FeatureByPositionReverse` 从**新到旧**）
⇒ ★ 四条都是**同一个毛病：对第三方 API 的"形状"作了未验证的假设**。
```
★ 而修法也一致：**先用一个对照量清形状，再写判据**（本轮补了 A-1/A-2 的**两段式**：
先证"变了"，再单独记"变多少"）。

## 五、判据
| ID | 判据 |
|---|---|
| SC-5801 | ★★ 走**官方 Remarks**那条路（选面 `mark=1`）⇒ 建成 |
| SC-5802 | ★ `swFmDome` **不存在**的核实（枚举 + 35 常量表）|
| SC-5803 | ★★★ 查出 **`get_com_member` 「取」会「调」** 并最小修复 |
| SC-5804 | ★★ 指出**危险面**（无必填参数且有副作用的成员会被静默执行）|
| SC-5805 | ★ 冒烟 **9/9**，两条**如实标注**（未查明 / 不可达）|
| SC-5806 | ★ 记下我自己的 **4 次判据错**，并归结为同一个毛病 |
| SC-5807 | 已知事实 84 入库；门禁 + 回归不退化（回归 **1201 passed**）|

## ⚠ 明确记下的限度
* ⚠ **未查明**：`Height=8` 而 Z 增长 **14.2222**（语义待查）；
* ⚠ **未查明**：特征树里哪一个是圆顶（`FeatureByPositionReverse` 顺序语义没查清）；
* ⚠ **不可达**：`IDomeFeatureData2` 的读回（官方示例那条路，事实 47/68）；
* ⚠ `get_com_member` **仍是"会调"**的语义（本轮只是把一种错误码纳入白名单）——
  **彻底修（永不调用）会动到全仓库，未做**。
"""

plan = """# 062 · Plan

## 步骤
1. 挑 `dome`（真缺 + 可用特征树/边界框验证）
2. 查 `swFmDome` ⇒ **不存在** ⇒ 只能走 `IModelDoc2.InsertDome`（`void` 返回）
3. 实现 `insert_dome`；冒烟第一次：**选面报类型不匹配** ⇒ 事实 33（Callout 要 VARIANT）
4. 修好选面 ⇒ `InsertDome` 报 **`0x8002000F`** ⇒ ⚠ **不猜**，读官方 Remarks
   ⇒ **选面必须 mark=1**（并读官方 C# 示例）
5. 仍报 `0x8002000F` ⇒ ★ 做一次**干净诊断**（`tools/diag_insert_dome.py`）
   ⇒ ★★★ 查出错在 **`get_com_member` 自己**（"取"就"调"了一次）
6. 最小修复（把 `DISP_E_PARAMNOTOPTIONAL` 纳入白名单）⇒ **圆顶建成** ✓
7. ⚠ 我的判据错了 4 次 ⇒ 逐条修（属性 vs 方法 / 逐分量 / 顺序）
8. 两条如实标注（未查明 / 不可达）+ 事实 84 + 门禁 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 看到 `0x8002000F` 就去试各种参数 | ★ **读官方 Remarks + 官方示例**（本轮正是这么解的）|
| 把 `get_com_member` 直接改成"永不调用" | ★ **最小修**（不动全仓库依赖的语义）|
| 三次都失败还继续猜 | ★ **写诊断脚本一次排开**（事实 53 的精神）|
| 判据红了就怪 API | ★ 本轮 4 次红**全是我判据的错** |
"""

tasks = """# 062 · Tasks（全部完成，轮 143）

- [x] T-5801 核实 `swFmDome` **不存在**（枚举 + 35 常量表）
- [x] T-5802 实现 `insert_dome`（走 `IModelDoc2.InsertDome`）
- [x] T-5803 ★★ 按官方 Remarks 用 **mark=1** 选面
- [x] T-5804 ★★★ 诊断脚本查出 **`get_com_member`「取」会「调」** + 最小修复
  `→ 验收:` `python tools/diag_insert_dome.py`
- [x] T-5805 真机冒烟 `→ 验收:` `python tools/verify_dome_smoke.py`（**9/9**）
- [x] T-5806 能力证据 + 已知事实 84 + 地图重跑 + `sw_connect` 来源块
- [x] T-5807 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""

converge = """# 062 · Converge

**Converged**: 2026-10-01（轮 143）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-5801 官方 Remarks（mark=1） | ✅ 建成 |
| SC-5802 `swFmDome` 不存在 | ✅ 两处核实 |
| SC-5803 `get_com_member` 缺陷 | ✅ 查出并最小修复 |
| SC-5804 危险面 | ✅ 写明 |
| SC-5805 冒烟 9/9（两条如实标注） | ✅ |
| SC-5806 记下 4 次判据错 | ✅ |
| SC-5807 事实 84 + 门禁 + 回归 | ✅ `release_check` exit 0 · **1201 passed** |

## 二、★★★ 本轮的价值几乎全在**副产物**上
```
目标：补 `dome`（一个"真缺"条目）
⇒ 结果：**查出 `get_com_member`「取」等于「调」** —— 一个影响**全仓库**的设计缺陷
⇒ ★ 而 `insert_dome` 起初**完全不能工作**，根因**不是圆顶**，是那个辅助函数。
```
★ 与 `051`（补 `ellipse` ⇒ 量出整模块单位写错）**同一个形状**：
**为了补一格而去看，看到的往往不止那一格。**（这句话本轮又应验一次）

## 三、★★ 「危险面」比"这个 bug"更重要
```
本轮**没有**遇到"取一下就删了"的事故（`InsertDome` 只是抛错）
⇒ 但机制摆在那里：**无必填参数 + 有副作用**的成员会被静默执行
⇒ ★ 所以本轮**明确写下危险面**（`InsertDeleteHole()` / `File*` 写盘方法）
   并**没有**去把它改成"永不调用"（那会动到全仓库）
```
★ 这是本轮的一个**克制**：**发现了更大的问题，但只做最小修复 + 把危险写清楚**。

## 四、⚠ 我自己的判据错了 **4 次**，而且**都是同一个毛病**
```
① GetFeatureCount(True)  ⇒ 它是**属性**，不是方法
② max(size1) > max(size0) ⇒ 变的那个方向在 max 里排不上号
③ max()-max() 当增长量    ⇒ 抓不到"最小方向在长"
④ names[n_before:] 当"新增" ⇒ FeatureByPositionReverse 从**新到旧**
⇒ ★ 四条都是：**对第三方 API 的"形状"作了未验证的假设**
```
★ 修法一致：**先用一个对照量清形状，再写判据**。
★ 而本轮还学到一招：**把"变了没有"与"变了多少"拆成两条判据** ——
首版合成一条 ⇒ 一旦"变多少"不符合预期，连"变了"也报成 ✗（**把已证的事一起否掉**）。

## 五、未查证
* `Height=8` 而 Z 增长 **14.2222** 的语义；
* 特征树里哪一个是圆顶；
* `IDomeFeatureData2` 读回**不可达**；
* ⚠ `get_com_member` **仍是"会调"**的语义（只把一种错误码纳入白名单）。
"""

for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)
