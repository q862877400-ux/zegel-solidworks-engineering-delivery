# 规格 216 · T-216-07：B 型 / D 型的**声明式选区**改造（★ 真机读数 + 顺带发现）

> **跑法**：★ `python tools/sw_guard.py --timeout 900 -- python output/_t216_bd_verify.py`
> （★ 读数抄在这里 —— ★ `output/` 被 gitignore）✓

## 一、★★ 真机读数（2026-10-07）

| 用例 | ★ 读数 |
|---|---|
| ★ ① `measure_selection_report(doc, arc_option=1, **selection="index:0"**, selection_kind="FACE")` | ★ `ok=True` · ★ `selected_count=1` · ★ `applicable=['area','perimeter']` · `area=0.0012` ✓ |
| ★ ① 反例 `selection="index:99"` | ★ `ok=False` · ★ 「选区未建立：EntitySelectionError: FACE 序号 99 越界（体 0 上共 6 个）（★ 前置未成立、★ 与「量不出来」是两件事）」✓ |
| ★ ② `create_axis_report(doc, reverse=True, **selection="index:0"**, selection_kind="FACE")`（★ 圆柱件）| ★ `ok=True` · ★★ **特征树增量 `['基准轴1']`** ✓ |
| ★ ② 附带查明 | ★ 该圆柱件的**圆柱面就是 `index:0`** ✓（★ 可作轴参照的几何：圆柱面 / 圆锥面 / 两点 —— ★ 官方）|

## 二、★ 修法（★ 两条同形，但**语义上不许照抄圆顶那次**）

```
① 加**声明式入参**：`selection`（`index:<n>` / `__current_selection__`）+ `selection_kind`（FACE/EDGE/VERTEX）
   ★ 规则 3：**工具不收裸坐标** ✓
② 在**读选区计数之前**由函数自己 `resolve_selection(...)`  **重建**选区
   ★ 因为注入解析器**会清空选区**（事实 503）✓
③ 后面那段「计数 0 就报错」**原样保留** —— ★ 它现在就成了一条**真实的回读判据** ✓
```

★★ **与 `insert_dome` 那次的区别（★ 这条很要紧）**：
  ★ 圆顶的「给哪个面加」**可以随便定**（★ 第一张面就是一张合法的面）；
  ★★ 而 **「量什么」「用哪个几何建轴」是调用方的意图** ⇒ ★ **绝不能由函数乱造** ✗
    （★ 造了的话，量出来的/建出来的**不是你要的那个**，★ 而且**看不出来**）✓
  ⇒ ★ 所以这六条（B/D 型）**一律"让调用方声明"**，★ 而不是"函数自己挑一个" ✓

## 四、★★ 第二批（★ 2026-10-07 · 同一形状再两条）

★ 跑法：★ `python tools/sw_guard.py --timeout 900 -- python output/_t216_bd2_verify.py` ✓
★ 试件：★ **100×60×20 mm** 板（★ 建法照本模块自己的 docstring：**`with sw_part.sketch(...)` + 毫米数**）✓

| 用例 | ★ 读数 |
|---|---|
| ★ `selection_point(doc, **selection="index:0"**, selection_kind="FACE")` | ★ `ok=True` · `selection_count=1` · ★ **`point_mm = (-50.0, 0.0, -10.0)`** ✓ |
| ★ `selection_point(… selection="index:99")` | ★ `ok=False` · ★ 「选区未建立：FACE 序号 99 越界（体 0 上共 6 个）（★ 前置未成立、★ 与「取不到点」是两件事）」✓ |
| ★ `section_properties(doc, **selection="index:0"**, selection_kind="FACE")` | ★ `ok=True` · `status=0.0` · ★★ **`area = 1200.0`** · `entry_used = GetSectionProperties2(property)` · `units_verified=False`（★ 单位存疑**如实带在返回里**）✓ |
| ★ `section_properties(… selection="index:99")` | ★ `ok=False` · ★ 「选区未建立：…（★ 前置未成立、★ 与「求不出截面属性」是两件事）」✓ |

★★ **一个精确的交叉验证**：★ `area = 1200.0` **恰是 60×20 的端面面积** ✓
  ⇒ ★ 一方面说明**选区确实建对了**（★ 选中的是那张端面）；
  ★ 另一方面**顺带证明**：★ 用 `with sw_part.sketch(...)` + **毫米数**建出来的**正是 100×60×20 的板** ✓
  （★ 与第三节那个"待查项"互为对照：★ 不按 docstring 写法建，★ 到底建出什么，★ 仍未测）✓

★★ **一条本批特有的顺序约束**：★ `section_properties` **自己**有"**清空并重写选择集**"的副作用
  （★ 官方 `## Remarks` 逐字）⇒ ★★ 所以「**选一次、读一次**」这个配对**不能被打断** ——
  ★ 代码里选择那一行就**紧贴**在读取之前 ✓（★ 这不是风格问题，★ 是语义要求）

★ 门禁自动跟着变：★ 「命中 8 · 基线 8」⇒ ★ 「**命中 6 · 基线 6**」✓

---

## 五、★★ 第三批（★ 2026-10-07 · `sketch_stretch` —— ★ **只修好"前置"那一半**）

★ 机制与前面几条**不同**：★ 草图段**既不是** `FACE`/`EDGE`/`VERTEX`、**也没有名字**（事实 32）
  ⇒ ★ 用不了 `resolve_selection` ⇒ ★ 换官方 **`ISketch::GetSketchSegments()`**（零参）+
  **`ISketchSegment::Select4(Append, Data)`**（★ 官方页有：`Select4.md` 逐字
  「`System.bool Select4( System.bool Append, SelectData Data )`」）✓
★ 修法：★ 新增 `select_active_sketch_segments(model, indices=None)`（★ 复用本仓
  `sw_selection_spec.select_object` ⇒ ★ callout 与回读它都处理了）+ ★ `sketch_stretch(…, select_all=True)`
  ⇒ ★ 缺省**自己把活动草图的段全选上**（★ = "伸展整张草图"）✓

| 用例 | ★ 读数 |
|---|---|
| ★ `sketch_stretch(doc, 0,0, 30,0, keep_relations=False, select_all=True)`（★ 40×20 矩形）| ★★ **`selected_count = 4`**（★ 四条段**全选上**）· `sketch_before → after` = `草图1 → 草图1` ✓ |
| ⚠ 效果读数 | ★★ **取不到** —— `bbox_before_mm` / `bbox_after_mm` / `transform_before` / `transform_after` **全 `None`** ⇒ ★ **`ok = None`**（★ 工具**如实报"量不到"**、★ **不报成功**）✗ |

★★ **所以本轮只确证了"前置"那一半**（★ 选区**建起来了**），★ **没有**确证"伸展真的改了几何" ⇒
  ★★ **列为新的待查项**：★ 该工具的两个几何判据（★ 草图段端点 bbox · `ModelToSketchTransform.ArrayData`
  平移分量）**在本机都取不到值** ⇒ ★ 原因未查（★ 本轮**不声称**效果成立）✓
★ 门禁仍收掉本条 —— ★ 因为**本道的判据是"函数有没有选区入口"**，★ 而那一条**确实修好了** ✓
  （★ 两件事分开记：★ **入口修好** ≠ **效果验证** —— ★ 本仓既有纪律正是"注册 ≠ 能跑"）✓

---

## 六、★★ 顺带发现（★ 与本次改造无直接因果，但**值得记**）

★ 我的复验脚本**第一版失败**了，★ 错误逐字：
```
RuntimeError: sketch_circle() 被调用时**没有活动草图** ⇒ 画几何会**静默无效**（几何画到不存在的地方）。
★ 先调 `sketch_start(model, plane_name=...)` 再画。
```
★ 查明两条（★ 都在 `scripts/sw_part.py` 自己的 docstring 里）：

1. ★★ **`sw_part.sketch()` 是上下文管理器** —— ★ 必须
   `with sw_part.sketch(doc, "Front Plane") as sk:` ✓（★ 直接调用**不会**进入它 ⇒ 草图没开）✓
2. ★★ **本模块的长度单位就是毫米** —— ★ 它的 docstring 逐字：
   「⚠ 上面是**裸数字**，因为**本模块的长度单位就是毫米**（本机实测，见已知事实 73）。
     ★ 这里**不要**写 `mm(25)` —— `mm()` 是「毫米→米」的换算，用在本模块会得到 `0.025`，
       也就是画出 **0.025 毫米**的圆（少了 1000 倍，且**不报错**）」✓

⚠ **由此引出一个待查项（★ 本轮未动）**：★ 仓库自己的 `tools/verify_costing_e2e.py` 里写的是
```python
sk = sw_part.sketch(model, "Front Plane")          # ★ 没有 with
sw_part.sketch_corner_rectangle(model, -0.05, -0.03, 0.05, 0.03)   # ★ 并且用的是"米"口径的数
sw_part.extrude_boss(model, sk, 0.02)
```
★ 而它**跑得出真结果**（`total_to_manufacture = 3.2714499345031918` 与台账一致）⇒
★★ 说明**有些助手容忍这种写法、有些不容忍**（`sketch_circle` 有"无活动草图"守卫、`sketch_corner_rectangle` 没有）✓
⇒ ★ **列入待查**：★ 那到底是"容忍"还是"恰好也画对了"，★ 要单独实测（★ 本轮**不改**它 ——
★ 它现在**通过**，★ 而"改一个通过的验收脚本"要先有证据）✓
