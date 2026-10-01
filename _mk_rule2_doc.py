import subprocess
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

DOC = """# 规则 2 的**死守卫** —— `_LEN_SUFFIX` 定义了却从没用过

> 来源：`tests/test_rule2_length_suffix_is_enforced.py`（2026-10-01 轮 134，Spec Kit `053`）
> ⚠⚠ **结论：规则 2 的「长度参数必须以 `_mm` 结尾」这一半，从写下到 2026-10-01 从未生效。**

## 一、怎么发现的
`052`（轮 133）证明了「脚本层的单位无人守」。顺着这条线去看**工具层**那条守卫：
```
`mcp-server/tool_registry.py`
  L78:  _LEN_SUFFIX = "_mm"                   ← 定义了
  L251: if p.name in _BARE_COORD_NAMES:       ← 只有**裸坐标**那条在用
```
⇒ `_LEN_SUFFIX` **只在定义处出现一次** —— **死常量**。

★★ 这正是**已知事实 40** 那句：
> 「一个**存在但没人用**的守卫与没有守卫等价，**且更糟**（让人以为防住了）」

⚠ 而更糟的是：规则 2 **一直被算进「五统一门禁通过」**（A3 的判据之一）。

## 二、先证明它确实是死的（事实 62：负例是唯一的证明）
`tests/test_rule2_length_suffix_is_enforced.py` 造一个**故意违规**的声明
（参数名 `thickness`、**不以 `_mm` 结尾**）：
```python
#: 接上之前
assert not rejected        # ⇒ 3 passed：确实**不拒**
assert len(uses) == 1      # ⇒ `_LEN_SUFFIX` 只在定义处出现
```
★ 对照组：**同一段的裸坐标规则（规则 3）是生效的** ——
说明不是"整段都没实现"，而是**恰好少了长度那一半**。

## 三、接上它（`053`）
```python
_LEN_WORDS = ("radius", "diameter", "depth", "thickness", "distance",
              "width", "height", "length", "offset", "spacing", "pitch")
#: ⚠ 刻意**不含** size / w / h —— 它们在非几何语境同样常用（已知事实 74）
#: ⚠ `bool` 不是长度（`use_default_radius` / `reverse_thickness` 是**标志**）
if p.kind is not bool and any(w in low for w in _LEN_WORDS) and not low.endswith("_mm"):
    ...
```

### ⚑ 三个**真正的例外**走显式豁免（不是把它们改绿）
| 工具 | 参数 | 为什么 `_mm` 会说错话 |
|---|---|---|
| `solidworks_mold_core_cavity_split` | `thickness` | 文档写明「**0.0 = 用文档默认**」⇒ 是**交给 SolidWorks 的文档默认量** |
| 同上 | `offset` | 同上 |
| `solidworks_mold_parting_surface` | `distance` | 同上 |

⇒ 照 `check_interface_member_ownership.MANUAL_MAP` 的先例：**每条带理由**，没依据的不许进来。

## 四、★ 判据有效的证明（同样的负例，**换了方向**）
```
接上之前：assert not rejected   ⇒ 3 passed（证明"不生效"）
接上之后：with pytest.raises(GateError)   ⇒ 5 passed（证明"生效"）
```
★★ **这个"把断言翻过来"的动作本身，就是判据被接上的证据** ——
而它是我在轮 134 **写那条测试时就预留好的**（测试自己的 docstring 里写着
「一旦规则 2 被接上，这条会红，那时就该把它改成『必须被拒』」）。
⇒ ★ **判据的"死"与"活"都能被同一条负例表达** —— 只是断言方向不同。

## 五、影响面
```
接上之后：`check_specs(all_specs())` ⇒ **0 个问题**（41 条声明全部合规，3 个走豁免）
⇒ ★ 说明**没有"正在违规"的工具** —— 但**守卫从"没有"变成了"有"**。
⚠ 也就是说：这次修的不是"一个 bug"，而是**"以后再犯会被拦"**。
```

## 六、⚠ 与本项目其它同族记录的关系
```
事实 40  存在但没人用的守卫 ≡ 没有守卫（本条的**类**）
事实 62  门禁"写了"≠"有效"，负例是唯一的证明（本条的**方法**）
事实 74  按名字判语义的检查做不成门禁（本条的**边界**）
```
★ 三者合起来是一句话：
**守卫要能被负例证伪；而按名字判语义的那类，连负例都写不出有意义的来。**
"""

P = Path(r"C:\swprojects\sw-skill-fork\docs\rule-2-dead-guard.md")
P.write_text(DOC, encoding="utf-8")
print("  ok 已写 docs/rule-2-dead-guard.md（%d 行）" % len(DOC.splitlines()))

# 已知事实 75
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
ADD = """

| # | 事实 | 依据 |
|---|---|---|
| 75 | **「五统一门禁」的规则 2（长度参数必须以 `_mm` 结尾）曾长期是「死守卫」—— 常量 `_LEN_SUFFIX` 只在定义处出现过一次，从未被任何判据使用** —— 2026-10-01（轮 134）：`mcp-server/tool_registry.py` 里 `_LEN_SUFFIX = "_mm"` 定义了，但**只有裸坐标那条（规则 3）在判**。★ 而规则 2 **一直被算进「A3 五统一门禁通过」**。⚠ 这正是事实 40（「**存在但没人用的守卫与没有守卫等价，且更糟**」）的教科书例子。★ 证明方法（事实 62）：**负例** —— 造一个参数名 `thickness` 却不以 `_mm` 结尾的 `ToolSpec`，接上之前 `check_spec` **不拒**（断言"不生效"，3 passed）；接上之后**必须拒**（断言 `pytest.raises(GateError)`，5 passed）。★★ **"把断言翻过来"这个动作本身就是判据被接上的证据**，而那个方向是**写测试时就预留好的**。⚠ 面积：接上后 `check_specs(all_specs())` = **0 问题** ⇒ **没有正在违规的工具**，修的是"**以后再犯会被拦**"。⚠ 词表刻意不含 `size`/`w`/`h`（非几何语境同样常用，见事实 74）；`bool` **不算长度**（`use_default_radius`/`reverse_thickness` 是标志）；3 个**真例外**（`sw_mold` 的 `thickness`/`offset`/`distance`，文档写明「0.0 = 用文档默认」）走**显式豁免表 + 每条理由** | `mcp-server/tool_registry.py` 的 `_LEN_WORDS` / `_LEN_SUFFIX_EXEMPT`；`tests/test_rule2_length_suffix_is_enforced.py`（5 条，含翻转前后的同一负例）；`docs/rule-2-dead-guard.md` |
"""
if "死守卫" not in tk:
    K.write_text(tk.rstrip() + ADD, encoding="utf-8")
    print("  ok known-facts 已加 75")
else:
    print("  已有 75")
