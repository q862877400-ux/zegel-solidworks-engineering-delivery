# 规则 2 的**死守卫** —— `_LEN_SUFFIX` 定义了却从没用过

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
