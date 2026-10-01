import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
S = Path(r"D:\AI\SW\specs\054-dead-guard-sweep-angle-half")
S.mkdir(parents=True, exist_ok=True)

spec = """# 054 · 系统扫一遍「死守卫」—— 规则 2 的**角度那一半**也是死的

**Status**: Implemented（轮 135）

## 一、方法（复用 `053` 的形状）
`tools/probe_dead_guards.py`：在 `mcp-server/` 与 `scripts/` 里找**模块级常量**，
名字像门禁（`*_RE` / `*_SUFFIX` / `*_NAMES` / `*_MARK` / `*_ALLOWED` …），
数它**在同一个文件里出现几次** —— **只出现 1 次**（只有赋值那行）⇒ 可疑。

结果：**扫过 21 个 · 只出现 1 次的 2 个**。

## 二、★ 逐条人工判（**这正是纪律要求的**）
| 可疑 | 判定 |
|---|---|
| `mcp-server/tool_registry.py:79` **`_ANGLE_SUFFIX`** | ✗ **真·死守卫** —— 它与 `_LEN_SUFFIX` **并排定义**（L77 注释写着「长度以 `_mm`、角度以 `_deg` 结尾」）而**两个都没被用过** |
| `scripts/sw_sketch_edit.py:67` `SKETCH_MIRROR_MARK` | ① **文档性常量** —— 注释明说「**不是参数**，是选实体时的 mark」⇒ **假阳性** |

⇒ 假阳性 **1/2 = 50%** ⇒ ★ **本探针同样不能单独当门禁**（输出清单，人工判）。

## 三、⚠⚠ 本轮真踩到的一个坑：**词表里的子串**
```
第一版 `_ANGLE_WORDS` 含 `rad` / `radians`
⇒ **子串命中 `radius`** ⇒ 把 `bend_radius_mm`（×4）与 `use_default_radius`（×3）
   共 **7 处**误判 ⇒ 扫出 9 处可疑，真违规只有 1 处
⇒ ★ 最终词表**刻意不含** `rad`：`_ANGLE_WORDS = ("angle", "degrees", "draft")`
```
★ 与事实 74 **同族**：**按名字的检查，连"词"的边界都得小心。**

## 四、接上角度那一半
```python
if p.kind is not bool and any(w in low for w in _ANGLE_WORDS) and not low.endswith("_deg"): ...
```
⇒ `check_specs(all_specs())` = **0 问题**；真实违规只有 **1 处**：
`solidworks_mold_parting_surface.angle`（文档写明「0.0 = 用文档默认」）
⇒ 与那 3 个长度例外**同一条理由** ⇒ 走**显式豁免 + 理由**。

## 五、判据
| ID | 判据 |
|---|---|
| SC-5001 | ★ 探针可跑，输出「只出现一次的像门禁的常量」清单 |
| SC-5002 | ★★ **2 个可疑逐条人工判**（1 真 · 1 假）|
| SC-5003 | ★★ **接上角度那一半**；`_ANGLE_SUFFIX` 不再是死常量（测试钉住）|
| SC-5004 | ★★ **`rad` 不许进角度词表**（子串会命中 `radius`）—— 测试钉住 |
| SC-5005 | ★ 对照组：`bend_radius_mm`（长度）**不该**被角度那条拦 |
| SC-5006 | ★ 角度豁免也是**显式表 + 每条理由** |
| SC-5007 | ★ 面积可量化：接上后 `check_specs(all_specs())` = **0 问题** |
| SC-5008 | 已知事实 76 入库；门禁 + 回归不退化（回归 **1176 passed**）|

## 六、★ 两轮合起来
```
规则 2 的**两半**（长度 `_mm` / 角度 `_deg`）此前**都是死的**：
  轮 134 接上长度那一半（`_LEN_SUFFIX`）
  轮 135 接上角度那一半（`_ANGLE_SUFFIX`）
⇒ ★ 两次用**同一个方法**：找"定义了却只出现一次"的常量。
⇒ 而这一次是**系统扫描**出来的，不是"顺手"发现的 —— 方法可复用。
```

## ⚠ 明确记下的限度
* 探针假阳性 **50%** ⇒ **只出清单、不做门禁**；
* 词表是**有界选的**（`rad` 故意不收；`size`/`w`/`h` 同样不收）；
* ⚠ **本轮只扫了"常量"形态的死守卫** —— 别的形态（例如**写好了却从没被调用的函数**、
  **注册了却没接进 dispatch 的表**）**未扫**；
* 角度豁免是**人工判**的 ⇒ 新出现同类要人工加。
"""

plan = """# 054 · Plan

## 步骤
1. 复用 `053` 的方法：**找"定义了却只出现一次"的常量**
2. 写 `tools/probe_dead_guards.py`（**有界词表** + 计数，输出清单）
3. 跑 ⇒ 21 个里 **2 个可疑**
4. ★★ **逐条人工判** ⇒ `_ANGLE_SUFFIX` **真**（与 `_LEN_SUFFIX` 并排定义、两个都没用过）；
   `SKETCH_MIRROR_MARK` **假**（文档性常量）
5. ★ 接上角度那一半
6. ⚠⚠ 中途踩坑：词表里的 `rad` **子串命中 `radius`** ⇒ 7 处假阳性 ⇒ **改词表**
7. 测试（负例 + `rad` 不许进词表 + 对照）+ 文档 + 事实 76 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 把"只出现一次"直接当"死守卫" | ★ **人工逐条判**（50% 是假阳性）|
| 词表收 `rad` | ★ 实测会**子串命中 `radius`** ⇒ 不收 |
| 接了判据不验 | ★ **负例**（`pytest.raises(GateError)`）+ 对照（`bend_radius_mm` 不该拦）|
| 顺手去扫别的形态 | **不做**（本轮只扫"常量"形态，限度里写明）|
"""

tasks = """# 054 · Tasks（全部完成，轮 135）

- [x] T-5001 写 `tools/probe_dead_guards.py`
  `→ 验收:` `python tools/probe_dead_guards.py`（21 扫过 / **2 可疑**）
- [x] T-5002 ★★ 逐条人工判 ⇒ **1 真（`_ANGLE_SUFFIX`）· 1 假（`SKETCH_MIRROR_MARK`）**
- [x] T-5003 ⚠ 发现并修我自己的**子串 bug**（`rad` 命中 `radius`，7 处假阳性）
- [x] T-5004 接上角度那一半 + 显式豁免（`solidworks_mold_parting_surface.angle`）
- [x] T-5005 测试扩到 **10 条**（含角度负例、`rad` 禁令、对照）
  `→ 验收:` `python -m pytest tests/test_rule2_length_suffix_is_enforced.py -q`（**10 passed**）
- [x] T-5006 文档 §七 + 已知事实 76
- [x] T-5007 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""

converge = """# 054 · Converge

**Converged**: 2026-10-01（轮 135）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-5001 探针可跑 | ✅ 21 扫过 / 2 可疑 |
| SC-5002 逐条人工判 | ✅ 1 真 1 假 |
| SC-5003 接上角度那一半 | ✅ 测试钉住 |
| SC-5004 `rad` 不许进词表 | ✅ 测试钉住 |
| SC-5005 对照（`bend_radius_mm` 不该拦） | ✅ |
| SC-5006 角度豁免显式 + 理由 | ✅ |
| SC-5007 面积 0 问题 | ✅ |
| SC-5008 事实 76 + 门禁 + 回归 | ✅ `release_check` exit 0 · **1176 passed** |

## 二、★★ 本轮的形状：**把上一轮的"顺手发现"变成"系统发现"**
```
053：顺着 052 的线**顺手**发现 `_LEN_SUFFIX` 是死的
054：把那个方法**写成探针** ⇒ 系统扫一遍 ⇒ 又扫出 `_ANGLE_SUFFIX`（**同一处、另一半**）
⇒ ★ 一次"顺手发现"的价值，在于它能不能变成**可重复的方法**。
```

## 三、★★ 而本轮**自己的词表**踩了同类坑
```
第一版 `_ANGLE_WORDS` 含 `rad` ⇒ **子串命中 `radius`** ⇒ 7 处假阳性
⇒ ★ 而 074（事实 74）刚刚说过"按名字判语义做不成" ——
  这次更细：**连"词"的边界都得小心**（`rad` ⊂ `radius`）
```
★ 这条值得单独记：**同一个"按名字"的坑，会以不同粒度反复出现**
（整句 → 词 → **子串**）。

## 四、★ 两轮合起来的完整性
```
规则 2 的两半：
  `_LEN_SUFFIX`（`_mm`）  ← 轮 134 接上
  `_ANGLE_SUFFIX`（`_deg`）← 轮 135 接上
⇒ ★ 而两半**并排写在同一个注释下面**（L77「长度以 `_mm`、角度以 `_deg` 结尾」）——
  即：**写在文档里的规则，两半都没实现**。
```
★ 这解释了一个容易发生的错觉：**规则的"文本"存在**会让人以为规则的"实现"存在。

## 五、未查证
* 探针假阳性 **50%** ⇒ 只出清单、不做门禁；
* ⚠ **只扫了「常量」形态的死守卫** —— 别的形态（**写好却从没被调用的函数**、
  **注册了却没接进 dispatch 的表**）**未扫**；
* 角度豁免是**人工判**的。
"""

for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)
