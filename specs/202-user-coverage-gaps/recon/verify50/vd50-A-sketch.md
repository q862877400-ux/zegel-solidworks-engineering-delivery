# vd50-A · sketch 域 —— 「能力 level 与真机证据」逐条核对

**范围**：`capabilities.yaml` 里 `level: verified` 且属草图域的条目，及其 `evidence` 字段引用的每个产物。
**核的三件事**：① 引的 evidence 文件真的存在吗；② 该文件的结论与条目写的是否一致；③ 有没有「证据否定、条目肯定」。
**读的代码**：`scripts/sw_sketch.py` · `scripts/sw_sketch_edit.py` · `scripts/sw_sketch_modify_ops.py` · `scripts/sw_sketch_edit_ops.py`。

---

## 〇 · 结论速览

| 项 | 数 |
|---|---|
| 核的 `verified` 条目 | **16** 条 |
| 核的 evidence 引用处 | **29** 处 |
| **对不上** | **4** 处（F1–F4） |

**存在性（问题 ①）：18/18 引用的 evidence 产物全部存在**，外加反查到的 2 个派生产物（`output/sketch-edit-smoke-evidence.json` · `output/spline-forms.json`）也都在。
⇒ **本域没有「引用了不存在的证据文件」这一类问题**；所有 4 处对不上都出在**问题 ②/③（引用错文件或结论强度超框）**。

**逐条判定一览**

| 条目 | level | 存在 | 一致 | 判定 |
|---|---|---|---|---|
| `sketch_query` | verified | ✅ | ❌ 数字 | **不成立**（F4） |
| `sketch_chamfer` | verified | ✅ | ✅ | 成立 |
| `sketch_build` | verified | ✅ | ✅ | 成立 |
| `sketch_primitives_b1` | verified | ✅ | ✅ | 成立 |
| `sketch_edit_ops_b3` | verified | ✅ | ✅ | 成立 |
| `sketch_modify_ops` | verified | ✅ | ❌ | **不成立**（F1） |
| `sketch_dimension_horizontal` | verified | ✅ | ✅ | 成立 |
| `sketch_dimension_vertical` | verified | ✅ | ✅ | 成立 |
| `sketch_slot_types` | verified | ✅ | ✅ | 成立 |
| `sketch_line2` | verified | ✅ | ✅ | 成立 |
| `sketch_spline` | verified | ✅ | ❌ | **不成立**（F2 / F3） |
| `sketch_spline3_2d` | verified | ✅ | ✅ | 成立 |
| `sketch_rotate_or_copy_3d` | verified | ✅ | ✅ | 成立 |
| `sketch_equation_curve` | verified | ✅ | ✅ | 成立 |
| `sketch_offset_on_surface` | verified | ✅ | ❌ | **不成立**（F5） |
| `coverage_gap_batch1` | verified | ✅ | ✅ | 成立 |

> `sketch_edit_ops` 是 `level: stitched`，不在本次「verified」范围内，未计入上表。

---

## ★★★ 最严重的一类单列（问题 ③：证据否定 / 未覆盖，而条目写成肯定）

### F1 · `sketch_modify_ops` 引的证据文件里**一条草图工具都没有**，且它记的是 **1/5**

**判定：成立** —— 一句话依据：条目称该文件是 `solidworks_sketch_` 前缀「MCP 契约真机调用 **5/5**」的证据，而该文件记的是 `solidworks_insert_` 前缀、**passed = 1 / n_tools = 5**、5 项里 4 项写着「不能」。

**仓内那一段** —— `capabilities.yaml` · `sketch_modify_ops` · `evidence[1]`：

> ★ 2026-10-03（轮 472）**走 MCP 契约的真机调用 5/5**（★ 不手调内部实现，而按 `ToolSpec` 声明的 `inject` + `params` 装配）：`python tools/sw_guard.py --timeout 600 -- python tools/prove_tools_by_contract.py solidworks_sketch_`。证据 output/tools-by-contract-evidence.json。

**目标那一段** —— `output/tools-by-contract-evidence.json`（逐字）：

> ```json
>  "probe": "tools-by-contract",
>  "prefix": "solidworks_insert_",
> ```

> ```json
>   {
>    "tool": "solidworks_insert_offset_surface",
>    ...
>    "verdict": "不能",
> ```

> ```json
>  "n_tools": 5,
>  "passed": 1
> ```

**核到的事实**

1. 该文件的 `prefix` 是 **`solidworks_insert_`**，不是条目写的 `solidworks_sketch_`。
2. 该文件 5 个 `tool` 名逐个是 `solidworks_insert_planar_surface` / `_offset_surface` / `_ruled_surface` / `_delete_face` / `_replace_face` —— **0 个 `solidworks_sketch_*`**。
3. 该文件自己的统计是 **`"passed": 1`**（5 项中只有 `insert_planar_surface` 是 `"verdict": "能"`），与条目写的「5/5」直接相反。
4. 反查：`output/` 下另外两个带 `contract` 的证据（`link-tool-contract-evidence.json` · `core-chain-mcp-contract-evidence.json`）里**也没有** `solidworks_sketch_` 字样；`output/` 全目录 grep `solidworks_sketch_` 的命中里不含该文件。
   ⇒ **该结论在仓内现有产物中查不到支撑**（不猜是不是被覆盖）。

**注**：`sketch_modify_ops` 的 `evidence[0]`（`output/b4-sketch-modify-evidence.json`，`"passed": 5, "total": 5`）是**对得上的** —— 移动 `trans [-0.005,-0.005,0.0]`、旋转 `rot3x3 [0.866025,-0.5,0.0,…]`、镜像 `[-1.0,0.0,0.0,…]`、缩放 bbox `±20/±10 → ±30/±15`、伸展 `-19.997/20.003` 逐项与条目一致。
⇒ 本条的问题**只出在第二条 evidence**，不是整条被否。

---

### F2 · `sketch_spline` 的「三个条件缺一不可」，第三个条件在它自己引的证据里**没有对照格**

**判定：成立** —— 一句话依据：条目把「第二参 `SimulateNaturalEnds` 必须 `False`」写成四格对照定下的条件，而那四格里**没有任何一格传过 `True`**，条目自己的 limitations 也写着「未查」。

**仓内那一段** —— `capabilities.yaml` · `sketch_spline` · `label` + `evidence[1]` + `limitations[3]`：

> 样条曲线（`ISketchManager.CreateSpline2`）—— ★ **真机建成**·★★ **三个条件缺一不可**

> ③ ★ **第二个参数 = `False`**（`SimulateNaturalEnds`）
>        ⇒ ★★ **四格里只有一格成** ✓

> ⚠ 本包装未接进 MCP 工具层；⚠ 未查：`SimulateNaturalEnds = True` 的行为。

**目标那一段** —— `output/spline-with-variant-evidence.json`（逐字，四格全部）：

> ```json
>  {
>   "tag": "★★ **前人原样**：`CreateSpline2(data, False)`",
>   "form": "spline2",
>   "ok": true,
> ```

> ```json
>  {
>   "tag": "对照：`CreateSpline(data)`（不带 2）",
>   ...
>   "err": "TypeError: get_com_member(CDispatch, 'CreateSpline', *1 args)：取回来的成员**不可调用**（`getattr` 回了 `NoneType`，★ 而它通常是 `(None, None, None)`）—— ★ 这**多半是 pywin32 迟到绑定造不出该方法的",
> ```

> ```json
>  "passed": 1,
>  "total": 4,
>  "verdict": "spline_variant_works"
> ```

**核到的事实**

1. 四格里唯一成功的那一格，调用是 `CreateSpline2(data, False)`；另外三格的 `err` **逐字相同**，且点名的是 **`'CreateSpline'`**（不带 2）。
2. **没有任何一格把第二个参数换成 `True`** ⇒ 「`SimulateNaturalEnds` 必须 `False`」这条从未被对照过，它不是这次四格对照能「定下」的条件。
3. 条目 `limitations` 自己写「未查：`SimulateNaturalEnds = True` 的行为」，与 `label` 的「三个条件缺一不可」**正面冲突**。

**⇒ 「真机建成」这半句站得住**（该文件 `"passed": 1`、成功格 `ok: true`、`seg_before 0 → seg_after 1`）；**不成立的是「三个条件缺一不可」这个结论强度**。

---

### F3 · `sketch_spline` 的「扁平 list / list of tuples 都回 `None`」，在它引的证据里是 `TypeError`、不是 `None`

**判定：成立** —— 一句话依据：条目把「回 `None`」归给 `output/spline-with-variant-evidence.json`，而那两格记的是 `TypeError`（成员名取不到），根本没走到数组形态那一步。

**仓内那一段** —— `capabilities.yaml` · `sketch_spline` · `evidence[1]`：

> ② ★ **数组形态 = `VARIANT(VT_ARRAY|VT_R8, 扁平 list)`** （★ 而**扁平 list / list of tuples 都回 `None`**）

**目标那一段** —— `output/spline-with-variant-evidence.json` 的对应两格（逐字）：

> ```json
>  {
>   "tag": "对照：第①种扁平 list（★ 我上一轮用的）",
>   "form": "flat_list",
>   "ok": false,
>   "seg_before": 0,
>   "err": "TypeError: get_com_member(CDispatch, 'CreateSpline', *1 args)：取回来的成员**不可调用**…",
>   "seg_after": 0,
> ```

> ```json
>  {
>   "tag": "对照：第④种 list of tuples",
>   "form": "tuples",
>   "ok": false,
>   "seg_before": 0,
>   "err": "TypeError: get_com_member(CDispatch, 'CreateSpline', *1 args)：取回来的成员**不可调用**…",
>   "seg_after": 0,
> ```

**核到的事实**

1. 这两格**没有 `returned` 字段、也没有 `"None"`**，只有 `TypeError`；报错里的成员名是 **`'CreateSpline'`（不带 2）**。
2. 探针代码坐实了因果：`tools/prove_spline_with_variant.py` 里
   `if form == "variant_r8": … ret = C.call_com_member(sm, "CreateSpline", data)` /
   `elif form == "flat_list": ret = C.call_com_member(sm, "CreateSpline", list(PTS))` /
   `else: … ret = C.call_com_member(sm, "CreateSpline", tuples)`
   ⇒ **三个对照格全部调用同一个不带 2 的成员名** ⇒ 三个 `TypeError` 是**同一个原因**，数组形态这一维根本没被单独测过。
3. 真正给出 `None` 的是**另一个未被本条目引用的文件** `output/spline-forms.json`：
   `{ "form": "① 扁平 list", "raised": null, "ret": "None", "before": 0, "after": 0, "changed": false }`
   —— 而它对应的 `tools/probe_spline_forms.py` 四格用的是 `CreateSpline2`（`sw_connect.call_com_member(skm, "CreateSpline2", data, False)`）。

**⇒ 该结论的实质（扁平 list ⇒ `None`）在 `output/spline-forms.json` 里成立**；**不成立的是它被挂在了 `spline-with-variant-evidence.json` 名下**，且那一格把「成员名」与「数组形态」两个变量混在了同一格里。

---

### F5 · `sketch_offset_on_surface` 的「三步缺一不可」，第 ② 步在所引证据里回读是**全 false**，且该文件只对照了第 ③ 步

**判定：成立** —— 一句话依据：条目把「补设 `Mark`」列为三步之一并打「✓」，而所引证据三个格子（含成功那一格）的 `marked` 全是 `false`，且三个格子的唯一变量是 `insert_sketch`。

**仓内那一段** —— `capabilities.yaml` · `sketch_offset_on_surface` · `label` + `evidence[1]` + `limitations[0]`：

> 曲面上偏移（`IModelDocExtension.SketchOffsetOnSurface`）—— ★ **真机建成**·★★ **三步缺一不可**

> ② ★ **`Select4` 没有 mark 参数** ⇒ 用 **`ISelectionMgr.SetSelectedObjectMark(i, mark, -1)`** 补设 ✓

> ★★ **三步缺一不可**：① **按对象选边**（★ `Select4`，**不是** `SelectByID2`）；② 补设 **`Mark`**；③ 收尾 **`ISketchManager.InsertSketch(True)`**。

**目标那一段** —— `output/offset-on-surface-per-example-evidence.json`（逐字，成功那一格）：

> ```json
>    "tag": "★ 官方参数 + **收尾 InsertSketch**",
>    ...
>    "insert_sketch": true,
>    "ok": true,
> ```

> ```json
>    "sel": {
>     "n_edges_on_body": 12,
>     "counts": [1, 2, 3, 4],
>     "selected": 4,
>     "marked": [false, false, false, false]
>    },
> ```

> ```json
>  "passed": 2,
>  "total": 3,
>  "verdict": "offset_on_surface_per_example_2_of_3"
> ```

**核到的事实**

1. 该文件三格的 `sel` 块**逐字相同**，都是 `"marked": [false, false, false, false]` —— 包括 `"ok": true` 的成功那一格。
2. 探针代码说明 `marked` 就是那个调用的布尔回读：`tools/prove_offset_on_surface_per_example.py` 里
   `marked.append(bool(C.get_com_member(mgr, "SetSelectedObjectMark", i, int(mark), -1)))`
   ⇒ 条目写的「补设 `Mark` ✓」，在它自己引的证据里回读是**四条全 false**。
3. 该文件的**唯一变量是 `insert_sketch`**（`"insert_sketch": true` vs `"insert_sketch": false`，对照格 `"new_features": []`、`"ok": false`）⇒ **只有第 ③ 步被对照过**，第 ① 步（`Select4` vs `SelectByID2`）与第 ② 步在本文件里**没有对照格**。
   ⇒ 「三步**缺一不可**」的强度超出这份证据能支撑的范围。

**⇒ 「真机建成」这半句站得住**：`"before": 7` + `"new_features": ["基准面1", "草图2"]` 与条目「特征 7 → 9，新增 `基准面1` + `草图2`」逐项对上，对照格「7 → 7、新增 []」也如实记了。

**附（不计入 4 处，供参考）**：更早的 `output/sketch-offset-on-surface-evidence.json` 里 `by_point` 格 `"picked_edges": 0`（支持第 ① 步的说法），但同一文件 `by_object` 格 `"picked_edges": 2` 仍 `"ok": false` —— 即那份文件**也没有**把第 ① 步单独定成「真因」。该文件同样未被本条目引用。

---

## F4 · `sketch_query` 写的「17/17 通过」，证据文件记的是 **18/18**（数字级）

**判定：成立** —— 一句话依据：条目引的证据文件自己统计 `"passed": 18, "total": 18`，与条目写的「17/17 通过」差一格。

**仓内那一段** —— `capabilities.yaml` · `sketch_query` · `evidence[1]`：

> python tools/verify_sketch_getters_smoke.py（**真机**，SW 2026 SP4.1 / 34.4.1：新零件 → 进草图 → 画 1 条线 + 1 段弧 → 逐个调取法 → 退草图 → 关件不保存，**17/17 通过**，证据落 output/sketch-getters-smoke-evidence.json）

**目标那一段** —— `output/sketch-getters-smoke-evidence.json`（逐字）：

> ```json
>  "passed": 18,
>  "total": 18,
>  "verdict": "pass",
> ```

**核到的事实**：该文件 `checks` 字典逐条数得 **18 项**（`新建临时零件` / `start_sketch` / `sketch_line` / `sketch_arc` / `取到 ActiveSketch` / 6 个取法 / `画了线 ⇒ get_lines 非空` / `定量` / `get_sketch_segments` / `get_splines` / `get_polylines` / `end_sketch` / `收尾无残留模态框`），与 `"passed": 18, "total": 18` 一致。
⇒ 条目的 **17** 与证据的 **18** 对不上。**属数字抄录偏差，不影响该条目的实质结论**（`limitations` 里逐条记的 `get_lines 12 / get_arcs 16 / get_sketch_points 5 / get_ellipses 0 / get_parabolas 0 / get_user_points 0` 与文件 `getters` 段**逐个对上**）。

---

## 对得上的部分（列出，避免只报负面造成误读）

以下条目的「条目结论 ↔ 所引证据」逐项核对一致，**成立**：

- **`sketch_chamfer`**（verified）—— 条目「**10/10** `verdict: pass`」↔ `output/sketch-edit-smoke-evidence.json` 的 `"passed": 10, "total": 10, "verdict": "pass"`；条目「选中两条（选区计数 **2**）… 线段数 2 → 3」↔ 该文件 `"选区计数 = 2"`、`"倒角前 2 → 倒角后 3"`；条目 limitations「`type=0`/`type=1` 实测都不做事」↔ 同一文件之外由 `tools/probe_chamfer_forms.py` 记录且条目如实标了 `⚠`。
  ⚠ 附注（**不计入 4 处**）：同一条目的**兄弟条目** `sketch_edit_ops`（`level: stitched`）在同一脚本上写的是「**8/10** —— 选中前置成立，但倒角报错」，而该脚本的产物现值是 10/10 —— 那是 `stitched` 条目，不在本片「verified」范围，仅提示。
- **`sketch_build`**（verified）—— 条目「arc [0→1] · ellipse [0→1] · polygon [0→7] · slot [0→5] · centerline [0→1]」↔ `output/sketch-primitives-evidence.json` 的 `"segments": [0,1] / [0,1] / [0,7] / [0,5] / [0,1]`；条目「线后 count_lines=1 · 圆后 count_arcs=1 · 矩形后 count_lines=5 · 关掉草图后仍读到 5」↔ `output/sketch-build-evidence.json` 的 `after_line/after_circle/after_rectangle/after_end_sketch` 四个读数；条目 limitations「不 start 就画线 = 静默 · 坏基准面名 = ValueError」↔ 同一文件的 `"**没有抛错**（静默）"` 与 `"抛了 ValueError"`。
- **`sketch_primitives_b1`**（verified）—— 条目「9/9 pass，判据是草图实体段数增量」↔ `output/b1-sketch-primitives-evidence.json` 的 `"can": 9, "total": 9, "verdict": "pass"` 与 9 个 `items[].built: true`。
- **`sketch_edit_ops_b3`**（verified）—— 条目「6/7 真机建成…剪裁会让段数下降（2→1）、延伸不改段数而改几何（35→60）」↔ `output/b3-sketch-edit-evidence.json` 的 `"can": 6, "total": 7, "verdict": "partial"`、`"zh": "剪裁-最近"` 的 `"seg": [2, 1]`、`"zh": "延伸实体"` 的 `"len": [35.0, 60.0]`；条目 limitations「交叉曲线未验成」↔ 同文件 `"zh": "交叉曲线", "verdict": "不能", "built": false`。
- **`sketch_dimension_horizontal` / `sketch_dimension_vertical`**（verified）—— 条目「草图尺寸 0 → H:1 → V:1」与「不选那组 尺寸 0 → H:0 → V:0」↔ `output/hv-dimension-with-selection-evidence.json` 两个 `"ok": true` 格的 `"dim_after_h": 1, "dim_after_v": 1` 与 `"对照：**不选**"` 格的 `"dim_after_h": 0, "dim_after_v": 0`。
- **`sketch_slot_types`**（verified）—— 条目「四个 type 均令草图段数 0 → 5」↔ `output/sketch-slot-four-types-evidence.json` 四格 `"seg_before": 0` / `"seg_after": 5` / `"returned": "CDispatch"`。
- **`sketch_line2`**（verified）—— 条目「无活动草图时调它 ⇒ 回 `None`、草图段数**不可读（-1）**」↔ `output/createline2-and-createspline-evidence.json` 负例格的 `"returned": "None", "seg_before": -1, "seg_after": -1`；条目「段数 0 → 1 · 返回 `CDispatch`」↔ 成功格的 `"seg_before": 0, "seg_after": 1, "returned": "CDispatch"`。
- **`sketch_spline3_2d`**（verified）—— 条目「2D 成（0 → 1）· 只给一个点不成」↔ `output/createspline3-evidence.json` 的 `"mode": "2d", "ok": true, "seg_after": 1` 与 `"mode": "bad", "ok": false, "returned": "None"`；条目 limitations「曲面上的样条本轮未成」↔ 同文件 `"mode": "on_surface", "ok": false`（如实记了否定）。
- **`sketch_rotate_or_copy_3d`**（verified）—— 条目「`Copy=True` ⇒ 段 1 → 2 · 回 `True`」「`Copy=False` ⇒ 段 1 → 1 · 也回 `True`」↔ `output/rotate-or-copy-3d-evidence.json` 两格的 `"seg_before": 1` / `"seg_after": 2` 与 `"seg_after": 1`、两格 `"returned": "True"`。
- **`sketch_equation_curve`**（verified）—— 条目三格（显式成 0→1 · 参数式 0→0 但回 `CDispatch` · 坏表达式 0→0 回 `None`）↔ `output/equation-driven-curve-evidence.json` 三格逐字一致。
- **`coverage_gap_batch1`**（verified）—— 条目「旋转曲面 ⇒ 树新增 `曲面-旋转1` · 曲面体 0→1」「孔向导 ⇒ 树新增 `异型孔向导`（`M8`）」「欠定义回 **2**、加 `sgFIXED` 后回 **3**」↔ `output/coverage-gap-batch1-evidence.json` 的 `"tree_new": ["曲面-旋转1"]` / `"surface_bodies": [0, 1]`、`"feature_name": "异型孔向导", "size": "M8"`、`"status_under_defined": 2` → `"status_after_fixed": 3`。

---

## 附：另记两处「代码自述 vs 条目」的不一致（**不是 evidence 文件的问题**，故不计入 4 处）

只记原文，不下断言，供下一片决定要不要单独立条：

1. `scripts/sw_sketch.py` 模块 docstring 仍写「⚠ 本模块为静态签名比对后新写，**未在本机实测**（见 AGENTS.md 铁律 2）。」（同文件另有两处「⚠ 本组为照官方签名新写，未在本机实测」），
   而 `sketch_query` 条目已是 `level: verified` 并引了两份真机证据产物。
2. `scripts/sw_sketch_edit.py` 的**模块头**仍保留轮 122 的旧定性：「⚠⚠ **验证等级：`stitched`，且其中一半已确认「到不了」**」「`create_sketch_chamfer` ❌ **到不了**」「⇒ **`CreateChamfer` 在本后端到不了**」，
   而同一文件函数体内已写更正：「⚠⚠⚠ **2026-10-01（轮 164）更正上一段那段定性** —— 它是**误判**」「⇒ ★★★ **`type=2` 的倒角其实建成了**」。
   ⇒ 同一文件内部两处定性相反；`capabilities.yaml` 侧已采用轮 164 的结论（`sketch_chamfer` = verified）。

---

## 交付自述

- 本片**只读**了 `capabilities.yaml` · `output/*.json` · `tools/probe_*.py` · `tools/prove_*.py` · `scripts/sw_sketch*.py`，**未改动仓内任何文件**。
- 唯一交付物即本文件：`D:/AI/SW/specs/202-user-coverage-gaps/recon/verify50/vd50-A-sketch.md`。
- 「查不到」的两处已如实标注，未用相似名字顶替：① `solidworks_sketch_` 前缀的 MCP 契约证据在 `output/` 下**查不到**；② `SimulateNaturalEnds = True` 的任何一格在**两个**样条产物里都**查不到**。
