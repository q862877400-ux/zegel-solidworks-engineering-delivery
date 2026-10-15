import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ① 文档：把「死守卫」的扫描结果与两半的处置写全
P = Path(r"C:\swprojects\sw-skill-fork\docs\rule-2-dead-guard.md")
t = P.read_text(encoding="utf-8")
ADD = """

---

## 七、★ 系统扫一遍（2026-10-01 轮 135，Spec Kit `054`）

### 方法（复用轮 134 的形状）
`tools/probe_dead_guards.py`：在 `mcp-server/` 与 `scripts/` 里找**模块级常量**，
名字像门禁（`*_RE` / `*_SUFFIX` / `*_NAMES` / `*_MARK` / `*_ALLOWED` …），
数它**在同一个文件里出现几次**：
```python
if len(hits) <= 1:      # 只有赋值那一行
    suspects.append(...)
```
结果：**扫过 21 个 · 只出现 1 次的 2 个**。

### 逐条人工判（**这正是纪律要求的**）
| 可疑 | 判定 |
|---|---|
| `mcp-server/tool_registry.py:79` `_ANGLE_SUFFIX` | ✗ **真·死守卫** —— 它与 `_LEN_SUFFIX` **并排定义**（L77 注释写着「长度以 `_mm`、角度以 `_deg` 结尾」）而**两个都没被用过** ⇒ **规则 2 的角度那一半也从未生效** |
| `scripts/sw_sketch_edit.py:67` `SKETCH_MIRROR_MARK` | ① **文档性常量** —— 注释明说「**不是参数**，是选实体时的 mark」⇒ **假阳性** |

⇒ 假阳性 **1/2 = 50%** ⇒ ★ **本探针同样不能单独当门禁**（输出清单，人工判）。

### 角度那一半：接上
```python
_ANGLE_WORDS = ("angle", "degrees", "draft")
#: ⚠ 刻意**不含** `rad` —— 它会**子串命中 `radius`**
```
⚠⚠ **这个 `rad` 的坑是本轮真踩到的**：第一版词表含 `radians`/`rad`，
扫出 **9 处**可疑，其中 **7 处**是 `bend_radius_mm`（×4）与 `use_default_radius`（×3）
——**全是 `rad` 子串命中 `radius`**。
⇒ ★ 与事实 74 同一族：**按名字的检查，连"词"的边界都得小心。**

### 影响面与豁免
```
角度那一半接上后：`check_specs(all_specs())` ⇒ **0 问题**
⇒ 真实违规只有 **1 处**：`solidworks_mold_parting_surface.angle`
   ⇒ 文档写明「0.0 = 用文档默认」⇒ 与那 3 个长度例外**同一条理由** ⇒ 走**显式豁免**
```

### 结论
```
规则 2 的**两半**（长度 `_mm` / 角度 `_deg`）此前**都是死的**，
  2026-10-01 轮 134 接上长度、轮 135 接上角度。
⇒ ★ 而这两次都是**同一个方法**：找"定义了却只出现一次"的常量。
```
"""
if "系统扫一遍（2026-10-01 轮 135" not in t:
    P.write_text(t.rstrip() + ADD, encoding="utf-8")
    print("  ok 已补文档 §七")
else:
    print("  已有 §七")

# ② 已知事实 76
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
ADDF = """

| # | 事实 | 依据 |
|---|---|---|
| 76 | **规则 2 的「角度那一半」也是死守卫；且「按名字找死守卫」这个探针本身有 50% 假阳性** —— 2026-10-01（轮 135）用 `tools/probe_dead_guards.py`（找**定义了却只出现一次**的、名字像门禁的模块级常量）扫 `mcp-server/` + `scripts/`：**21 个里 2 个可疑** ⇒ 人工判：`_ANGLE_SUFFIX`（`tool_registry.py:79`，与 `_LEN_SUFFIX` **并排定义**、**两个都没被用过**）是**真·死守卫**；`SKETCH_MIRROR_MARK`（`sw_sketch_edit.py:67`）是**文档性常量**（注释明说"不是参数，是选实体时的 mark"）⇒ **假阳性 1/2 = 50%** ⇒ 探针**同样不能单独当门禁**。⚠⚠ 另一处真踩到的坑：第一版角度词表含 `rad`/`radians` ⇒ **子串命中 `radius`**，把 `bend_radius_mm`（×4）与 `use_default_radius`（×3）**共 7 处**误判 ⇒ ★ **按名字的检查，连"词"的边界都得小心**（与事实 74 同族）。⇒ 接上角度那一半后 `check_specs(all_specs())` = **0 问题**；真实违规只有 **1 处**（`solidworks_mold_parting_surface.angle`，文档写明「0.0 = 用文档默认」）⇒ 走**显式豁免 + 理由** | `tools/probe_dead_guards.py`；`mcp-server/tool_registry.py` 的 `_ANGLE_WORDS` / `_ANGLE_SUFFIX_EXEMPT`；`tests/test_rule2_length_suffix_is_enforced.py`（**10 条**，含角度那半的负例与"`rad` 不许进词表"）；`docs/rule-2-dead-guard.md` §七 |
"""
if "角度那一半」也是死守卫" not in tk:
    K.write_text(tk.rstrip() + ADDF, encoding="utf-8")
    print("  ok known-facts 已加 76")
else:
    print("  已有 76")
