import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
S = Path(r"D:\AI\SW\specs\035-equations-promoted-to-verified")
S.mkdir(parents=True, exist_ok=True)

spec = """# 035 · 方程式：由 `stitched` **升为 `verified`**（真机 5/5）

**Status**: Implemented（轮 116）

## 背景：这一轮**不再补新能力**
`023`/`024`/`028`/`034` 连着补了 **4 条 `stitched`** 能力 —— 都**只有静态证据**。
★ 再补只会**堆更多没验过的条目** —— 那正是我在 `014`/`015` 批评过的做法
（「孤立函数从没跑过」）。
⇒ **本轮转去给最安全的那条做真机冒烟。**

## 为什么挑 `equations`
| 候选 | 真机风险 |
|---|---|
| `sw_helix` | 需**先选中一个圆**（要先建草图、进编辑态）⇒ 前置复杂 |
| `sw_sketch_edit` | 需**草图编辑态 + 选中实体** ⇒ 同上 |
| **`sw_equation`** | ★ **只需一个新零件**，不建几何 ⇒ **风险最低** |

## 冒烟设计（轮 98 的模态框教训）
* **只在新零件上跑**，绝不碰用户文档；
* 只做**全局变量方程式**（官方示例里最简单的一种：`"SMOKE_B" = 2`），**不建几何**；
* 先置 `CommandInProgress = True`；
  ⚠ **已知事实 64**：它**不能**抑制所有模态框 ⇒ **收尾必查有没有残留模态框**（本轮新增的检查）；
* 收尾：关掉自己建的那个件（**不保存**）。

## 结果：**5/5 通过**
```
✓ 新建临时零件（零件15）
✓ add_equation('"SMOKE_B" = 2')      下标=0 · 0.16s
✓ list_equations                      1 条；首条='"SMOKE_B" = 2'
✓ evaluate_equations                  ok
✓ 收尾无残留模态框
（已关闭临时零件 零件15，不保存）
```
★★ **关键在"往返一致"**：写进去的字符串与读回来的**逐字相同** ⇒
**它真写进去了，不是空操作**。这一条比"没抛异常"强得多。

## 判据
| ID | 判据 |
|---|---|
| SC-3101 | ★ 真机冒烟 **5/5**，且**收尾无残留模态框**（已知事实 64 的检查）|
| SC-3102 | ★ **往返一致**（写入 == 读回）—— 证明不是空操作 |
| SC-3103 | 等级 `stitched` → **`verified`** + `verified_versions` + `evidence` |
| SC-3104 | ★ **等级不许往回降**：测试断言源码里必须写 `验证等级：`verified`` |
| SC-3105 | 证据落 `output/equation-smoke-evidence.json` |
| SC-3106 | 门禁 + 回归不退化（回归 **1091 passed**）|

## ⚠ 明确记下的限度
* **只验了「全局变量方程式」这一种**；**维度方程式**与含 VB `IIf` 的**都未测**；
* `delete_equation` **未在真机上调过**（冒烟覆盖 加 / 列 / 求解）；
* ⚠ **冒烟不证明"结果正确"** —— 例如 `evaluate_equations` 的**返回值语义未核**（只验了不抛）；
* `verified` 只表示「**有我们自己的运行证据**」，**不表示"代码是我们写的"**，也不表示"全部功能都验过"。
"""

plan = """# 035 · Plan

## 步骤
1. ★ 先决定**不补新能力** —— 4 条 `stitched` 已经堆着，再堆没有意义
2. 挑**真机风险最低**的那条 ⇒ `equations`（只需一个新零件）
3. 写冒烟：新零件 → 加 → 列 → 求解 → 关件不保存
   * 加 `CommandInProgress`
   * ★ **收尾查模态框**（已知事实 64 的产物）
4. 跑 ⇒ **5/5**，且**往返一致**
5. 升等级：`capabilities.yaml`（`level` + `verified_versions` + `evidence`）
   + 源码来源块 + 测试断言
6. 重生成 + 门禁 + 回归 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| **模态框卡住会话**（轮 98） | 只在新零件上、只做最简操作、**收尾查模态框** |
| 把"没抛异常"当成"能用" | ★ **要有往返一致**才算强证据（写进去 == 读回来）|
| 升了等级但没同步源码/测试 | ★ 测试断言源码里必须写 `verified`，**防止悄悄降回去** |
| 顺手把 `delete` 也测了 | **不做**（未测就写"未测"） |
"""

tasks = """# 035 · Tasks（全部完成，轮 116）

- [x] T-3101 决定**不补新能力**，改给已有 `stitched` 条做真机验证
- [x] T-3102 挑风险最低的 ⇒ `equations`
- [x] T-3103 写 `tools/verify_equation_smoke.py`（新零件 + 收尾查模态框）
  `→ 验收:` `python tools/verify_equation_smoke.py`（**5/5**）
- [x] T-3104 ★ 核对**往返一致**（写入 == 读回）
- [x] T-3105 升等级：`capabilities.yaml` + 源码来源块 + 测试断言
  `→ 验收:` `python -m pytest tests/test_sw_equation_contract.py -q`（10 passed）
- [x] T-3106 重生成 + 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""

converge = """# 035 · Converge

**Converged**: 2026-10-01（轮 116）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-3101 真机 5/5 + 无残留模态框 | ✅ |
| SC-3102 往返一致 | ✅ `'"SMOKE_B" = 2'` 进出一致 |
| SC-3103 升为 `verified` + 三个字段 | ✅ `verified_versions: ["2026"]` + `evidence` 两条 |
| SC-3104 禁止降级 | ✅ 测试断言源码里必须写 `verified` |
| SC-3105 证据落盘 | ✅ `output/equation-smoke-evidence.json` |
| SC-3106 门禁 + 回归 | ✅ `release_check` exit 0 · **1091 passed** |

**能力分布**：`verified 27 → **28**` · `stitched 6 → 5`

## 二、★ 本轮的**方向**变了：从"补新的"改成"验旧的"
```
023/024/028/034 —— 连着补 4 条 stitched，**都只有静态证据**
⇒ 再生产只会**堆更多没验过的条目**
★ 那正是我在 014/015 批评过的：「孤立函数从没跑过」
⇒ **与其再堆一条，不如把已有的一条验实。**
```
⚠ 这**不是**说前四轮白做 —— 它们的**查证**是真的（枚举冲突、废弃入口、`-1` 双语义）。
但那四条**仍然都没有运行证据**。

## 三、★ 什么才算"强证据"：**往返一致**
```
弱证据：「调用没抛异常」          —— 空操作也能满足
强证据：「写进去的 == 读回来的」  —— 空操作满足不了
```
★ 本轮刻意把**读回内容**打出来比对（`'"SMOKE_B" = 2'`），而不是只报"列到 1 条"。
⚠ 这与 `012` 的教训一致：那时 `list_render_materials` 返回 **0 个材质**，
「没报错」**什么都没证明**。

## 四、⚠ 但**这不等于"方程式功能全验过了"**
```
只验了：全局变量方程式（"SMOKE_B" = 2）
未验：  维度方程式 · 含 VB IIf 的 · delete_equation · evaluate 的返回值语义
```
★ `verified` 的定义是「**有我们自己的运行证据**」——
**不是**「代码是我们写的」，**也不是**「全部功能都验过」。
⇒ 边界已写进该条目的 `limitations`。

## 五、未查证
* **维度方程式**与**含 VB `IIf` 的**方程式**未测**；
* `delete_equation` **未在真机上调过**；
* `evaluate_equations` 的**返回值语义未核**（只验了不抛）；
* 另 3 条 `stitched`（螺旋线 / 草图编辑 / 转换实体引用）**仍需前置条件**才能冒烟 ——
  ⚠ **未做**，且**已知它们会需要进草图编辑态**（轮 98 的模态框正是那样触发的）。
"""

for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)
