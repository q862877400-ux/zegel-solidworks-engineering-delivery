import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
S = Path(r"D:\AI\SW\specs\034-convert-entities")
S.mkdir(parents=True, exist_ok=True)

spec = """# 034 · 从「真缺」再补一条：转换实体引用

**Status**: Implemented（轮 115）

## 背景
`023`/`024`/`028` 已从「真缺」档补了螺旋线 / 草图倒角镜像 / 方程式。本轮接着补
**`convert_entities`**（`022` 的核样确认它确实没有实现）。
⚠ 它**与已有的 `sw_sketch_edit.py` 同类**（都是草图编辑）⇒ **并进那个模块**，
**不新开文件**（"不重造"）。

## 选哪个入口（**先查废弃，再选**）
```
IModelDoc2.SketchUseEdge2(Boolean)      ⇒ 官方 md 明写 **Obsolete**
                                          （Superseded by ISketchManager::SketchUseEdge）
ISketchManager.ConvertEntities()        ⇒ **零参，未废弃**，也能用
ISketchManager.SketchUseEdge3(Boolean Chain, Boolean InnerLoops)  ⇒ **未废弃**
```
⇒ 取 **`SketchUseEdge3`**：两个参数**都有官方说明**（`Chain` 连整条链 / `InnerLoops` 带内环），
语义比零参的 `ConvertEntities()` 明确。⚠ 这一点**已写进来源块与 capability 的 limitations**。

## 判据
| ID | 判据 |
|---|---|
| SC-3001 | ★ 走 **`SketchUseEdge3`**，**不走**已废弃的 `SketchUseEdge2`（测试断言实现段里不出现后者）|
| SC-3002 | 参数按官方顺序 `(Chain, InnerLoops)`；默认 `True` / `False` |
| SC-3003 | ★ 官方返回 `False` ⇒ **抛带原因的错**（`False` 是假值，很容易被吞掉）|
| SC-3004 | 拿不到 `SketchManager` 时抛带原因的错 |
| SC-3005 | 扩 `sketch_edit_ops` 能力条目（34 条不变，**是扩不是新增**）|
| SC-3006 | 门禁 + 回归不退化（回归 **1091 passed**）|

## ⚠ 明确记下的限度
* **等级仍是 `stitched`** —— 只有静态证据，**本机从未做过转换实体引用**；
* **前置条件不代选**：官方写明投影的是「**selected** edges/loops/faces/curves/external contours」
  ⇒ 调用方要先选中并进入草图；
* 另有零参的 `ConvertEntities()`（未废弃）**未采用** —— 不是不能用，是语义更含糊；
* 本轮**主动不做真机测试**（轮 98 的模态框教训）。
"""

plan = """# 034 · Plan

## 步骤
1. 确认 `convert_entities` 确实没实现
2. ★ **先查废弃**：`SketchUseEdge2` 已 Obsolete ⇒ 在 `ConvertEntities()` 与
   `SketchUseEdge3` 之间选 ⇒ 取后者（两参都有官方说明）
3. **并进已有模块** `sw_sketch_edit.py`（不新开文件）
4. 写实现 + 6 条契约测试
5. ★ 扩 `sketch_edit_ops` 能力条目（**不新增条目**）
6. 重生成 + 门禁 + 回归 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 用了已废弃的 `SketchUseEdge2` | ★ 测试断言实现段里**不出现**该名字；来源块记下原因 |
| 把返回 `False` 吞掉 | ★ 单列一条测试（`False` 是假值，最容易被 `if not got: pass` 吞）|
| 为一条功能新开一个模块 | ★ **并进同类模块**（`sw_sketch_edit.py`）—— 不重造 |
| 顺手改别的 | 本轮**只加这一个函数** |
"""

tasks = """# 034 · Tasks（全部完成，轮 115）

- [x] T-3001 确认 `convert_entities` 没实现
- [x] T-3002 ★ 查废弃：`SketchUseEdge2` Obsolete ⇒ 取 `SketchUseEdge3`
- [x] T-3003 在 `scripts/sw_sketch_edit.py` 里加 `convert_entities`
- [x] T-3004 契约测试（**16 passed**，其中 6 条是本轮加的）
  `→ 验收:` `python -m pytest tests/test_sw_sketch_edit_contract.py -q`
- [x] T-3005 扩 `sketch_edit_ops` 能力条目
- [x] T-3006 重生成 + 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""

converge = """# 034 · Converge

**Converged**: 2026-10-01（轮 115）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-3001 走当前入口，不走废弃的 | ✅ 测试断言实现段不出现 `SketchUseEdge2` |
| SC-3002 参数顺序与默认值 | ✅ `(Chain=True, InnerLoops=False)` |
| SC-3003 返回 `False` 时抛错 | ✅ 单列一条测试 |
| SC-3004 拿不到 SketchManager 抛错 | ✅ |
| SC-3005 扩能力条目 | ✅ `sketch_edit_ops`（34 条不变）|
| SC-3006 门禁 + 回归 | ✅ `release_check` exit 0 · **1091 passed** |

## 二、★ 本轮的**取舍**是有据可查的
```
IModelDoc2.SketchUseEdge2      ⇒ **Obsolete**        ✗
ISketchManager.ConvertEntities()⇒ 未废弃，零参        ~ 可用，但语义含糊
ISketchManager.SketchUseEdge3  ⇒ 未废弃，两参都有说明  ✓ **采用**
```
★ **没有"哪个都行"就随便选一个** —— 选了之后把**为什么**写进来源块与能力条目。

## 三、⚠ 这一类错（返回假值被吞）在本轮被**专门**挡了一次
```
官方 SketchUseEdge3 失败时返回 **False**
⇒ `if not got: pass` 会把它**静默吞掉**（False 是假值，最容易被这么写）
⇒ 本函数对 False **抛带原因的错**，并单列一条测试钉住
```
★ 与 `028`（方程式的 `-1` 双重语义）同一族：**"失败信号长得像正常值"**。

## 四、「真缺」档的补录进度
```
023 螺旋线 · 024 草图倒角/镜像 · 028 方程式 · 034 转换实体引用
⇒ 共补 **4 条**（+ 本轮并入已有模块的一条，不新开文件）
⚠ 该档共 **132 条**（`022` 抽样估），**剩余仍很多**
```

## 五、未查证
* **本机从未做过转换实体引用**（等级 `stitched`）；
* **前置条件未实测**（官方要求先选中 + 在草图态）；
* 零参的 `ConvertEntities()` 与 `SketchUseEdge3` 的**行为差异未查**；
* 「真缺」档剩余条目**未逐条核**。
"""

for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)
