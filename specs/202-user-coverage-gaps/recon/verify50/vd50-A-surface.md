# vd50-A · surface 域「能力 level 与真机证据」逐条核对

★ 域：`surface`　★ 核的三件事：① `capabilities.yaml` 里 `level: verified` 的条目，它引的 evidence 文件**真的存在吗**；② 那个证据文件里的结论，**与条目写的一致吗**；③ 有没有「**证据里是否定、而条目写成肯定**」（最严重，单列）。
★ 纪律：只读 + 只写本文件；每条结论给两段可搜索原文（仓内段 / 目标段）；给不出两段的不写；查不到就说查不到；宁少勿滥；不写行号。

---

## 〇 · 本片范围与总数

★ 要读的四个实现文件：`scripts/sw_surface.py` · `sw_surface_features.py` · `sw_surface_edit_ops.py` · `sw_surface_ref_ops.py`。
★ 落在本域、`level: verified` 的条目共 **12 条**，逐条核过（下面表里「一致」= 三问都没问题）：

| # | 条目 `id` | 引的 evidence 文件 | 存在 | 与文件结论一致 |
|---|---|---|---|---|
| 1 | `surface_features` | `output/fill-surface-evidence.json` · `output/extend-surface-evidence.json` · `output/surface-knit-evidence.json` · `output/surface-feature-evidence.json` · `output/surface-feature-probe.json` | 5/5 存在 | ★ **不对上**（见 §一 §二） |
| 2 | `surface_edit_ops` | `output/b6a-surface-edit-evidence.json` | 存在 | 一致（`"passed": 5, "total": 5`） |
| 3 | `surface_ref_ops` | `output/b6b-surface-ref-evidence.json` | 存在 | 一致（放样成、旋转不成 —— 与 limitation 写的「旋转曲面本条不登记」相符） |
| 4 | `surface_offset` | `output/surface-oldstyle-three-evidence.json` | 存在 | 一致（`曲面-等距1` · 树 7→8 · `faces_selected: 4`） |
| 5 | `surface_planar_region` | `output/planar-replace-variants-evidence.json` | 存在 | 一致（`"tag": "T605 变体：选草图"` · `"returned": "True"` · `曲面-基准面1`） |
| 6 | `replace_face` | `output/planar-replace-variants-evidence.json` | 存在 | 一致（变体 B 成 `替换面1`、变体 A 0 增量） |
| 7 | `surface_revolve` | `output/revolve-oldstyle-evidence.json` | 存在 | 一致（两条入口都 `ok: true` · 无中心线那组 `ok: false`）★ 但 limitation 对代码的陈述有问题（见 §四） |
| 8 | `surface_flatten` | `output/flatten-with-anchor-evidence.json` | 存在 | 一致（四格里带锚点的两格成） |
| 9 | `surface_untrim` | `output/untrim-matrix-evidence.json` | 存在 | 一致（六格里只有 `Edge=2` 选边那格成） |
| 10 | `surface_delete_hole` | `output/delete-hole-for-surface-evidence.json` · `output/delete-hole-inner-loop-evidence.json` · `output/delete-hole-on-surface-evidence.json` | 3/3 存在 | ★★★ **不对上（最严重）**（见 §三） |
| 11 | `sketch_offset_on_surface` | `output/offset-on-surface-per-example-evidence.json` | 存在 | 一致（`segments: 0` 已在 limitations 里如实登记） |
| 12 | `coverage_gap_batch1`（含旋转曲面） | `output/coverage-gap-batch1-evidence.json` | 存在 | 一致（`"passed": 3, "total": 3` · `surface_bodies: [0, 1]`） |

★ **第 1 问（文件在不在）：核了 19 份被引证据文件，缺失 0 份。**（另核了同族但未被条目点名的 `output/planar-region-and-delete-hole-evidence.json`，见 §三。）
★ 另核了两条 `level: stitched` 的（本片只列不作结论）：`surface_thicken_silent_noop`（11 组真机全 `None`，写 `stitched` 而**不是** `verified` —— 等级诚实）；`surface_modeling`（`stitched` · `verified_versions: []`）。
★ 核过但**没报**的若干候选（避免含水）：`sketch_offset_on_surface` 证据里 `marked: [false,false,false,false]` 与条目「补设 mark=1」看着相反 —— 实为 `SetSelectedObjectMark` 的 **COM bool 返回值**，正是已知事实 8 说的不可信那一类，**不成立**；`coverage_gap_batch1` 写的「96/145 → 99/145」与今天 `docs/user-feature-coverage.md` 的 `119/145` 不同 —— 该句是**那一轮的前后增量**、文档天天重生成，**不成立**。

---

## ★★★ 一 · `surface_delete_hole` · level=verified · **属第 3 问「证据否定、条目肯定」**

**判定：成立（★★★ 最严重的一类）**

**一句话依据**：条目唯一以「★ **证据文件**」名义点名的三份文件，**三份的结论都是失败**（`passed: 0`），而条目写的是「真机建成」—— 真正支持「建成」的那份文件**条目从未点名**。

**仓内原文（`capabilities.yaml` · `id: surface_delete_hole` · `evidence[1]`）**
```
        "★ **证据文件**：`output/delete-hole-for-surface-evidence.json`（★ **同族的还有** `output/delete-hole-inner-loop-evidence.json`、`output/delete-hole-on-surface-evidence.json`）。"
```
★ 同条目 `evidence[0]` 写的正是肯定结论：
```
        "★★ 2026-10-03（轮 564）**真机建成**（零弹窗）：在**一张真正的带孔平面**（面 1 / 环 2）上选**孔那圈边** ⇒ `InsertDeleteHoleForSurface()` ⇒ **名 `删除孔1`**·**型 `DelHole`**·★ **环Δ = −1**（孔被填上）✓",
```

**目标原文（`output/delete-hole-for-surface-evidence.json` · 条目点名的那一份）**
```
  "verdict": "successor_also_fails"
```
```
  "passed": 0,
  "total": 3,
```
```
   {
    "tag": "★ **继任者** + 选孔的边",
    "entry": "InsertDeleteHoleForSurface",
    "pick": "edge",
    "ok": false,
```
★ 「同族的还有」那两份**同样是否定的**：一份 `"verdict": "inner_loop_still_fails"` + `"passed": 0, "total": 3`；一份 `"verdict": "delete_hole_still_noop_on_surface"` + `"passed": 0, "total": 4`。

**★ 能力本身不是假的 —— 缺陷只在「指错文件」**：真正带「建成」结论的是同一目录下的另一份，条目没写它：
```
  "at": "2026-10-03T16:32:09",
  "_": "**平面区域**造真正的带孔曲面 → 再在其上试**删除孔**",
```
```
    "del_name": "删除孔1",
    "del_type": "DelHole",
```
```
    "loop_delta": -1
  ],
  "verdict": "planar_region_and_delete_hole_work"
```
★ 本仓自己的知识文档也指向**那一份**而不是条目点名的那份（`docs/known-facts.md` 事实 443 的落款）：
```
★ **落地**：`capabilities.yaml` 新增 **`surface_delete_hole`**（level = **verified**，共 **99** 条）；台账「删除孔」补 `capability_id` ⇒ **已能 73**。|真机：`tools/prove_planar_region_then_delete_hole.py`；证据 `output/planar-region-and-delete-hole-evidence.json`；对照事实 441 / 442 · `surface_planar_region`（轮 517）|
```
⇒ ★★ **修法很小**：把 `evidence` 里那份「★ 证据文件」换成 `output/planar-region-and-delete-hole-evidence.json`，把三份失败记录降级成 limitations 里的「★ 前置不对时的对照」。★ 但**在换之前**，任何按 evidence 路径去复核这条能力的人，**拿到的全是 0/3 的失败记录**。

**★ 官方那一侧（说明被点的成员本身没问题，问题纯在证据指针）** —— `C:\swapi\types\IFeatureManager\InsertDeleteHoleForSurface.md`：
```
**Signature**: `Feature InsertDeleteHoleForSurface()`
```
```
Before calling this method, call [[IModelDocExtension::SelectByID2]] to select the hole edges to remove from the surface.
```

---

## ★★ 二 · `surface_features` · level=verified · **条目里的否定句被它自己引的证据推翻**

**判定：成立**

**一句话依据**：该条目的 `limitations` 仍写着「`InsertSewRefSurface` **不抛但特征树不变**」「其余（填充 / 缝合…）**都要先选中面或边**」—— 而**同一条目**的 `evidence` 与它引的证据文件都记着缝合与填充**都建成了**（那是轮 309 / 388，晚于写下这句的轮 308，**没回头更新**）。

**仓内原文（`capabilities.yaml` · `id: surface_features` · `limitations` 第三条）**
```
⚠ **本条**只包装了已验证的那一个：其余（填充 / 缝合 / 裁剪 / 加厚）**都要先选中面或边**
  —— 真机实测：`InsertSewRefSurface` **不抛但特征树不变**（它要求先选中要缝合的曲面）。
```
★ 同条目 `mcp_tools` 却列了四个：`solidworks_surface_create_extruded` / `solidworks_surface_knit` / `solidworks_surface_extend` / `solidworks_surface_fill`。

**目标原文（`output/surface-knit-evidence.json` · 条目自己引的那份缝合证据）**
```
  "steps": {
    "knit": {
      "ok": true,
      "new": [
        "曲面-缝合1"
      ],
      "faces": 8,
      "bodies": "2->1"
    },
```
```
  "verdict": "pass"
```
★ 填充那份同样是否定不掉的（`output/fill-surface-evidence.json`）：
```
    "fill_surface": {
     "ok": true,
     "feature_name": "曲面填充1",
```
```
  "verdict": "pass",
```
⇒ ★★ **同一条目里，「不抛但特征树不变」与「建成 `曲面-缝合1` · body 2→1」并排写着**。★ 本仓知识文档把两者的差别记得很清楚（`docs/known-facts.md` 事实 238 的定则）：**差别不是参数，而是「调用前那一步真的生效了没有」** —— 也就是说 limitations 那句**只对「没预选面」成立**，而条目把它写成了对 API 的否定结论。★ 后果：读者会以为「缝合这条路在本仓到不了」，而实际上 `solidworks_surface_knit` 已经是 verified 工具。

---

## ★ 三 · `surface_features` · 同一条目的延伸曲面证据：结论所依赖的那一格，**被点的文件里根本没有**

**判定：成立**

**一句话依据**：条目声称「真机推翻了『不选面』当负例的假设 —— 不选面它也能成」，并把它当作「所以负例换成参数校验」的理由；而它引的那份文件**没有「不选面」这一格**，且 `note` 写的还是相反的期待。

**仓内原文（`capabilities.yaml` · `id: surface_features` · `evidence[1]` 结尾）**
```
★ ⚠ 真机推翻了「不选面」当负例的假设 —— **不选面它也能成**（它自己会找面），故负例换成参数校验（距离 ≤ 0）。
```

**目标原文（`output/extend-surface-evidence.json`）**
```
  "note": "★ `extend_surface` 是 objective② 重核后确认的**真缺**；★ 官方 `IModelDoc2.InsertExtendSurface` 3 参、回 void ⇒ 判据只能是特征树。★ 负例（不选面）必须失败 —— 那证明判据不是恒真。"
```
★ 该文件里唯一的负例是**参数校验**那一格，没有 `faces_selected: 0` 的对照：
```
  "negative_zero_distance": {
   "ok": true,
   "returned_ok": false,
   "error": "distance_mm 必须 > 0（★ 收到 0.0）"
  },
```
⇒ ★ **这条不是编造**（同一结论在本仓知识文档里另有落点，`docs/known-facts.md` 事实 303 的标题）：
```
objective② 补第一个真缺：`extend_surface` 真机 PASS**（`IModelDoc2.InsertExtendSurface` 3 参 ⇒ 特征 `曲面-延伸1` · tree 7→8）；★ 而"不选面"**不是**负例（它自己会找面）
```
⇒ ★★ **缺陷是「引的证据撑不起这句话」**：要么补一份记录 `faces_selected = 0` 那格的证据文件，要么把这句从 evidence 里挪走（它现在属于 limitation 的内容，而 limitations 里**已经**有一份几乎同义的写法，两处重复）。

---

## 四 · `surface_revolve` · level=verified · limitation 对「本包装 docstring」的陈述与代码不符

**判定：存疑**（不是铁的，但值得单列，因为它是**调用方唯一能看到的说明书**）

**一句话依据**：条目写「★ 本包装的 docstring 已明写这一点（蓝图里必须有一条中心线）」—— docstring 里 `centerline` 只出现在**引用官方描述**的那一句，其「前置」段**只写了「调用前要选好轮廓」**，没有把中心线列成前置。

**仓内原文（`capabilities.yaml` · `id: surface_revolve` · `limitations` 第一条）**
```
★★ **前置：蓝图里必须有一条中心线**（官方原话的 centerline）—— ★ 本包装的 docstring 已明写这一点。★ 另官方给的 mark **没写** ⇒ ★ 本模块**不假定 mark**（真机用 mark=0 成）。
```

**目标原文（`scripts/sw_surface_ref_ops.py` · `insert_revolved_ref_surface` 的 docstring）**
```
    ★★★ 官方原话：「Creates a **revolved reference surface** by revolving a profile around a
      centerline.」⇒ ★ 与实体版 `sw_part.revolve_boss` 同形，★ 只是产出**曲面**。
```
```
    ⚠ **调用前要选好轮廓**（★ 官方 Remarks 逐字："Make the selections using
      `IModelDocExtension::SelectByID2` before calling this method"）。
      ★★ 而官方**没给 mark** ⇒ ★ 本模块**不假定 mark**，把这一点写进返回值 ✓
```
★ **为什么标存疑而不是成立**：那句 docstring **确实含 `centerline` 这个词**，若按「提到过」读法，条目的陈述字面为真；按「前置已显式写成前置」读法则不成立。★ **为什么仍要列出**：这一条的中心线前置是**轮 501 判「不成」、轮 529 才翻案**的唯一根因（条目自己写着「本仓此前对它的『不成』（轮 501，5 组全试过）真因是前置缺中心线」），而**调用方读到的说明书里看不到它** —— 复现轮 501 只需要照 docstring 做。

---

## 五 · 合计

★ 核了 **12 条** `level: verified` 的 surface 条目 / **19 份**被引证据文件。
★ 第 1 问（文件在不在）：**缺失 0**。
★ **对不上 3 处**（§一 `surface_delete_hole` 最严重、§二 `surface_features` 的 limitations、§三 `surface_features` 的延伸证据）+ **存疑 1 处**（§四 `surface_revolve` 对代码的陈述）。
★ 三处里**只有一处是能力本身的问题**（§三：结论有据、但被点的文件不含那一格）；**§一**是能力真成立、**证据指针指错**；**§二**是条目内部自相矛盾的陈旧文字。
★ **未写**的：任何「看起来可能有问题」「建议检查」类无两段原文的猜测，按铁律一律不落笔。