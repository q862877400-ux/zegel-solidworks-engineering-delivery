# vd50-A · drawing 域「能力 level 与真机证据」逐条核对

★ 域：`drawing`　★ 核的三件事：① `capabilities.yaml` 里 `level: verified` 的条目，它引的 evidence 文件**真不存在**吗；② 证据文件里的结论**与条目写的一致**吗；③ 有没有「**证据是否定、条目写成肯定**」。
★ 纪律：只读 + 只写本文件；每条结论给两段可搜索原文（仓内段 / 目标段）；给不出两段的不写；查不到就说查不到；宁少勿滥；不写行号。

---

## 〇 · 本片范围与总数

★ 域内 `level: verified` 的条目共 **5 条**（`id`/`label` 落在 drawing）：
`drawing_dimension_insertion` · `drawings_and_bom` · `drawing_current_sheet_query` · `drawing_views_and_summary` · `drawing_view_operations`。
★ 这 5 条共引 **8 份仓内证据文件**（含 3 个 pytest 与 2 个 tools 脚本）：

| 被引证据 | 存在 |
|---|---|
| `output/sheet-scale-evidence.json` · `output/drawing-query-evidence.json` · `output/drawing-object-routes.json` · `tools/capture_drawing_query_evidence.py` · `tools/probe_drawing_object_routes.py` | 全部存在 |
| `output/drawing-views-evidence.json` · `output/sheets-summary-probe.json` | 全部存在 |
| `output/set-view-scale-probe.json` · `output/scale-ratio-probe.json` · `output/drawing-view-evidence.json` | 全部存在 |
| `tests/test_delivery_compare.py` · `tests/test_drawing_subskill.py` · `tests/test_cad_reliability.py` | 全部存在 |

★ **第 1 问（文件在不在）：0 处缺失。** 下面 5 条都是第 2/3 问的问题。
★ 不在本片：`gtol_insert`（实现走 `scripts/sw_gtol.py`，非工程图脚本）、`export_delivery` 的跨域条目（其 `probe_pdf_on_drawing.py` 的产物文件未被条目点名，无可核对的 evidence 路径）。

---

## ★★★ 一 · `drawing_dimension_insertion`（label：SolidWorks 工程图模型尺寸自动插入）· level=verified

**判定：成立（★ 属第 3 问「证据支撑不住、条目却写肯定」那一类，最严重）**

**一句话依据**：它引的那个测试里，与本能力有关的**唯一**一行是断言清单自己那个 `level` 字段，而该测试文件自述「未在本机实测 SolidWorks」—— 全仓没有任何一行"尺寸插入回读"的断言。

**仓内原文（`tests/test_cad_reliability.py`）**
```
    assert index["drawing_dimension_insertion"]["level"] == "verified"
```
```
# ⚠ 未在本机实测 SolidWorks（见 AGENTS.md 铁律 2）。本次是清单形状与授权判据的迁移，
#   不改变任何 COM 调用；授权等价性由 tests/test_unattended_equivalence.py 对冻结基线守住。
```
★ 全文件里 `dimension` / `尺寸` / `note` / `generate_drawing` 的命中只有上面那一行 —— 该测试**只验清单形状**。

**目标原文（`capabilities.yaml` 的本条目）**
```
        "pytest tests/test_cad_reliability.py（工程图尺寸插入回读）"
```
```
⇒ ★★★ 所以本条**当前没有可挂的工具**（★ 实现层缺那一环）；★ 而它的 evidence 是
`pytest tests/test_cad_reliability.py（工程图尺寸插入回读）` ⇒ ★ **下一步：核那个测试到底验了什么**
```
★ 条目自己的 `limitations` 已经把疑点写下来了（"它可能验的是"尺寸能读回"而不是"能把模型尺寸插进工程图""），而 `level` 仍是 `verified`。

---

## ★★ 二 · `drawing_current_sheet_query`（图纸比例读/写）· level=verified

**判定：成立**

**一句话依据**：条目把 "PASS 5/5" 写成「正例 3 · **负例 3**（含「图纸名不存在」）」，而所引证据文件里只有 **2 个负例**，`图纸名不存在` 这一步在整个 JSON 里**不存在**。

**仓内原文（`output/sheet-scale-evidence.json`）**
```
    "numerator=3": {
      "ok": true,
      "error": "本机 `ISheet.SetScale` 的 Numerator **只接受 1**（★ 真机三组：(1,5)→`1:5` · (3,7)→`1:7` · (2,1)→`1:1`）⇒ 图纸比例只能是 "
    },
    "negative": {
      "ok": true,
      "error": "比例的两个数都必须 > 0（★ 收到 -1.0:5.0）"
    }
```
```
  "passed": 5,
  "of": 5,
  "verdict": "pass"
```
★ 5 步 = `1:5` / `1:2` / `1:1` 三条写 + `numerator=3` 与 `-1:5` 两条负例；**没有**任何"图纸名不存在"的步骤。

**目标原文（`capabilities.yaml` 本条目）**
```
python 真机（轮 301）★ **PASS 5/5** —— 图纸比例读(1:1) · 写 1:5/1:2/1:1 三个都回读一致 · 负例(numerator=3 / -1:5 / 图纸名不存在)都显式拒绝 · 证据 output/sheet-scale-evidence.json
```
```
  · ★ 负例：★ `numerator=3` ⇒ **显式拒绝** ✓ · `-1:5` ⇒ **显式拒绝** ✓ · 图纸名不存在 ⇒ **如实报"现有：[…]"** ✓
```
★ 同一段「图纸名不存在 ✓」也被逐字复制进 `drawing_view_operations` 的 `limitations`（两处同源同错）。

---

## ★ 三 · `drawing_views_and_summary`（工程图视图与整图摘要）· level=verified

**判定：存疑**

**一句话依据**：条目声称 `current_sheet_info` 真机回了 `scale_num` / `scale_den`，而它引的两份证据都只记到 4 个 key、没有这两个 —— 这两个字段只在**另一条目**的 `output/drawing-query-evidence.json` 里出现，所以是**引错文件**而不是结论错。

**仓内原文（`output/drawing-views-evidence.json`，两个夹具都是同一组 key）**
```
        "current_sheet_info": {
          "keys": [
            "first_angle",
            "height_mm",
            "paper_size",
            "paper_size_code"
          ]
        },
```
★ 第二份被引证据 `output/sheets-summary-probe.json` 只有 `sheet_count` / `sheet_names` / `current_sheet_name` / `sheets_summary` 四项，**完全没有 `current_sheet_info`**。
★ 对照：`scale_num` / `scale_den` 确实存在于 `output/drawing-query-evidence.json` 的 `"scale_num": 1.0,` / `"scale_den": 1.0,` —— 那是 `drawing_current_sheet_query` 条目引的文件。

**目标原文（`capabilities.yaml` 本条目）**
```
另：`current_sheet_info` 真机回 `paper_size` / `scale_num` / `scale_den` / `first_angle` / `height_mm`。证据 output/drawing-views-evidence.json · sheets-summary-probe.json
```
★ 该条其余部分与证据一致：`"passed": 2, "of": 2, "verdict": "pass"`、`bolt-assembly.slddrw` → `list_views n=5`、`box.slddrw` → `list_views n=4`、两者 `sheets_summary` 均为 1 张 `Sheet1` —— 这几条都对得上。

---

## ★ 四 · `drawings_and_bom`（工程图、尺寸链与 BOM）· level=verified

**判定：成立（局部：只错在其中一条 evidence 上；整条由另一条 evidence 撑着）**

**一句话依据**：第一条 evidence 点的 `tests/test_delivery_compare.py` 里，`drawings_and_bom` 只是一个**字符串参数**，该文件两个测试断言的全是快照比较与再生请求，**没有一行**工程图或 BOM 断言。

**仓内原文（`tests/test_delivery_compare.py`，全文两个测试）**
```
def test_compare_snapshots_detects_added_removed_changed_and_unchanged(tmp_path):
    unchanged = tmp_path / "same.step"
```
```
    assert comparison["counts"] == {"added": 1, "removed": 1, "changed": 1, "unchanged": 1}
```
```
        capabilities=["drawings_and_bom", "export_delivery", "drawings_and_bom"],
```

**目标原文（`capabilities.yaml` 本条目）**
```
    "evidence": [
      "pytest tests/test_delivery_compare.py",
      "pytest tests/test_drawing_subskill.py（工程图与 BOM）"
    ],
```
```
  "label": "工程图、尺寸链与 BOM",
```
★ 第二条 evidence 是真的：`tests/test_drawing_subskill.py` 里有 `def test_general_table_cannot_satisfy_required_bom():`（`assert result["bom_evidence"]["tables"] == []`）与 `def test_assembly_bom_requires_a_real_template(tmp_path: Path):` ⇒ BOM 半边站得住；错的是把 `test_delivery_compare.py` 也算作本条的运行证据。

---

## ★ 五 · `drawing_view_operations`（工程图视图操作）· level=verified

**判定：存疑**

**一句话依据**：条目写「list/**collect** ok count=3」，而所引证据只有 `list_views` / `get_scale` / `set_scale` 三步，**没有 collect 那一步**；不过 `set` 的否定结果条目在 limitations 与 evidence 文本里都如实写了，**不构成**"否定写成肯定"。

**仓内原文（`output/drawing-view-evidence.json`）**
```
    "list_views": {
      "ok": true,
      "count": 3,
```
```
    "set_scale": {
      "ok": false,
      "before": null,
      "after": null,
      "asked": null
    }
  },
  "passed": 2,
  "of": 3,
  "verdict": "partial"
```
★ `steps` 下只有三个键，**无 `collect`**；`collect_view_evidence_report ⇒ {ok: true, count: 3}` 这句只出现在 `docs/known-facts.md` 的事实 226 里，不在本条引的证据里。

**目标原文（`capabilities.yaml` 本条目）**
```
python 真机（轮 293）：有视图的图（3 视图）—— list/collect ok count=3 · get_view_scale ok scale=0.002 · 证据 output/drawing-view-evidence.json
```
★ 前半段（轮 294 的「写不进」）与所引证据**完全一致**：
```
  "set_verified": {
    "ok": false,
    "before": [1.0, 500.0],
    "after": [1.0, 500.0],
```
对应 `set-view-scale-probe.json`；`scale-ratio-probe.json` 的 `"repr": "(1.0, 500.0)"` / `"scale_decimal": 0.002` 也与条目写的「ScaleRatio 回 (1.0,500.0)=1:500 · ScaleDecimal 回 0.002 · 写不进」逐字对得上。

---

## ★ 「证据里否定、条目写成肯定」的专项结论

★ 本域 **没有**这种最严重的形态。`drawing_view_operations` 与 `drawing_views_and_summary` 的否定项（视图比例写不进、绘制视图未验、多图纸未验）都在 `limitations` 与 evidence 文本里**如实保留**了否定词（`ok: false` / `写不进` / `未验`）。
★ 唯一的"肯定写过头"是第一条（`drawing_dimension_insertion`）：证据本身根本不构成验证，而条目仍标 `verified`。

## ★ 查不到（如实记，不顶替）

1. `output/drawing-views-evidence.json` 与 `output/sheet-scale-evidence.json` 的**采集脚本在仓内查不到** —— 在 `tools/` 下按这两个文件名检索无命中（仓内只出现在 `capabilities.yaml` / `docs/ROADMAP.md` / `docs/known-facts.md` 的引用里）⇒ **无法核对这两份 JSON 记录的字段是否被采集脚本截断**，第三条（`scale_num`/`scale_den` 缺失）因此只能判「存疑」而不是「成立」。
2. `drawing_*` 各条目所涉的官方成员（`ISheet.SetScale` / `ISheet.GetProperties` / `IView.ScaleRatio`）本次**没有**去 `C:\swapi\types\` 逐页重核 —— 本片只核 level 与证据的一致性，不做签名核对，故不出签名结论。
3. `sw_drawing_expose.py` / `sw_drawing_create_missing.py` 提供的 `solidworks_inspect_drawing` / `solidworks_generate_drawing` / `solidworks_review_drawing` 三个工具，在 `capabilities.yaml` 里**没有任何条目以 `mcp_tools` 认领**（按这三个工具名检索 `capabilities.yaml` 无命中）⇒ 这部分**没有条目可核**，故本片不写结论。
