# vd50-A · moldcosting · 能力 level 与真机证据对账

**范围**：`capabilities.yaml` 里 moldcosting 域（模具 + Costing）`level=verified` 的 **4 条**：`costing` · `costing_readback` · `mold_analysis` · `costing_templates_and_defaults`（同域另有 `mold_tools` · `mold_parting_geometry` 两条为 `stitched`，不在本片判定范围）。
**只读核验**（未改仓内任何文件）；本文件是唯一写入。
**核了 5 处引用，对不上 3 处**（其中「条目肯定 / 证据否定」方向 **1 处**）。

---

## 〇 · 逐条清点（4 条 verified → 5 处引用 = 4 个文件）

| # | 条目 | 引用的证据文件 | 文件在？ | 内容与条目一致？ |
|---|---|---|---|---|
| 1 | `costing` | `output/costing-evidence.json` | ✅ 在（869 B） | ❌ **见 V-1 + V-2** |
| 2 | `costing_readback` | `output/costing-evidence.json` | ✅ 在 | ✅ 一致（条目照实写「真机 5/6」+ `list_templates ✗`，与文件逐字对得上） |
| 3 | `mold_analysis` | `output/mold-evidence-smoke.json` | ✅ 在（1183 B） | ✅ 一致（`passed 5 / total 5 / verdict pass`；条目写的「键 6/6」「6 个为 0/空」与文件的 `detail` 逐字对得上） |
| 4 | `mold_analysis` | `output/mold-draft-analysis-owner.json` | ✅ 在（212 B） | ✅ 一致（`passed 4 / total 4 / verdict pass`；`on_feature_manager: "AttributeError"` · `on_model_doc2: "取到:method"` · `after_fix: "ok:bool"` 与条目一致） |
| 5 | `costing_templates_and_defaults` | `output/costing-templates-evidence.json` | ✅ 在（824 B） | ✅ 一致（三个 step 全 `ok: true`；`list_costing_templates_report` 回 `"count": 2`、两个 default 回真实模板路径，与条目「PASS 3/3 · count=2」一致） |

★ **存在性一关全过**：4 条 `verified` 引的 4 个证据文件**全部真实存在**（另两条 `stitched` 引的 3 个 mold 证据文件也都在，但等级不是 verified，不判）。

---

## ★★★ V-1 · 「条目写成肯定、而它自己引的证据文件写的是否定」——`costing` 条目把 `verdict: partial` 记成了 `verdict: pass`

**判定：成立**（★ 本片最重的一处；用户要求单列的那一类）

**仓内那一段** —— `capabilities.yaml` 的 `costing` 条目 `evidence`：

> "python tools/verify_costing_e2e.py（⇒ verdict: pass；证据 output/costing-evidence.json）"

同条 `limitations` 里同一句（写成「期望」，措辞略软，但指向同一个文件）：

> ⚑ **验收命令**（可复跑）：`python tools/verify_costing_e2e.py` ⇒ 期望 `verdict: pass`。

**目标那一段** —— 它所引的那个文件 `output/costing-evidence.json` 的结尾三行：

> ```
>   "captured_at": "2026-10-02T13:28:34",
>   "passed": 5,
>   "of": 6,
>   "verdict": "partial"
> ```

以及文件里唯一失败的那一步：

> ```
>     "list_templates": {
>       "ok": false,
>       "preview": "{'ok': False, 'error': 'AttributeError: <unknown>.GetTemplatePathnames'}"
>     },
> ```

**一句话依据**：条目把它引的证据文件写成已发生的 `verdict: pass`，而该文件记录的是 **`verdict: partial`（5/6）**，且 `list_templates` 明写 `ok: false` ——「肯定 / 否定」方向相反。

★★ **同仓交叉印证（两处，可独立复核）**：
① **同域的姊妹条目** `costing_readback` 引**同一个文件**，写的是如实的那一份：

> "python 真机（轮 274）：**5/6** —— 四个读数是**真的读到了数据** · 证据 output/costing-evidence.json"

> ★ **真机 5/6**：`get_costing_manager` ✓ · `costing_evidence` ✓（`{body_count: 1, has_cost_analysis: True}`）· `body_count` ✓ · `list_bodies` ✓ · **`read_analysis` ✓（读到真数据，含模板路径）**；⚠ `list_templates` ✗ —— 报 `<unknown>.GetTemplatePathnames`

② `docs/ROADMAP.md`（及仓内 `_roadmap_163.txt`）也把同一个文件记成否定：

> ② ★ 真机 `output/costing-evidence.json` = **PARTIAL（5/6）**，★ 唯一的失败已定性 ✓

⇒ **一个文件被三条仓内文字描述成了两种结论**；`costing_readback` 与 ROADMAP 的写法（partial / 5/6）与文件一致，`costing` 的写法（pass）与文件不一致。

---

## V-2 · `costing` 用同一个文件背书「完整闭环 + 具体成本数值」，而该文件里既没有闭环步骤、也没有那个数值

**判定：成立**

**仓内那一段** —— `capabilities.yaml` 的 `costing` 条目 `limitations`：

> ⚑ **2026-10-01（轮 61）完整闭环真机跑通**（SW 2026 SP4.1）：自建 100×60×20 mm 单实体板 → `Extension.GetCostingManager()` 拿到 CostManager → 两个类别共 **4 条模板路径**（`.sldctc` / `.sldcts`） → 默认材质 **`普通碳钢`** / 材质类 **`钢`** → `CostingModel`＝`CostPart`（**1 个 body**） → `GetCostAnalysis()` 非空 → **`total_to_manufacture = 3.2714499345031918`（USD）**。证据文件：`D:\AI\SW\output\costing-evidence.json`（含时间戳与版本）。

**目标那一段** —— 该文件 `output/costing-evidence.json` 的全部内容（31 行，逐字）：

> ```
> {
>   "steps": {
>     "get_costing_manager": { "ok": true },
>     "evidence": { "ok": true, "preview": "{'ok': True, 'readback': {'body_count': 1, 'has_cost_analysis': True}}" },
>     "body_count": { "ok": true, "preview": "{'ok': True, 'body_count': 1}" },
>     "list_bodies": { "ok": true, "preview": "{'ok': True, 'count': 1, 'names': ['?']}" },
>     "list_templates": { "ok": false, "preview": "{'ok': False, 'error': 'AttributeError: <unknown>.GetTemplatePathnames'}" },
>     "read_analysis": { "ok": true, "preview": "{'ok': True, 'readback': {'template': 'c:\\programdata\\…\\costing t" }
>   },
>   "captured_at": "2026-10-02T13:28:34",
>   "passed": 5,
>   "of": 6,
>   "verdict": "partial"
> }
> ```

**一句话依据**：条目列出的闭环四要素（模板路径 / 默认材质 / `CostingModel` / `GetCostAnalysis` 成本数值）**在该文件里一个都没有** —— 它的 `steps` 只有 6 个**读数**步，没有 `templates` / `defaults` / `cost_analysis` 这三步，也**没有任何成本数字**、没有 `普通碳钢`、没有版本字段（只有 `captured_at`）。

★ **补强（同为仓内，可复核）**：条目点名的那条验收命令 `tools/verify_costing_e2e.py` 自己写的键与该文件**对不上**——脚本落盘的结构是：

> `evidence: dict = { "started": …, "solidworks_revision": …, "verdict": "unknown", "steps": {} }` … `evidence["steps"]["cost_analysis"] = costs` … `evidence["assertions"] = { "total_to_manufacture_gt_0": total > 0, … }`

而文件里**没有** `started` / `solidworks_revision` / `assertions` / `cost_analysis` / `build_part` / `templates` / `defaults` 这些键，**多出** `captured_at` / `passed` / `of`；且脚本里 `verdict` 只可能是 `"unknown"` / `"pass"` / `"fail: …"`，**不可能是 `"partial"`** ⇒ **当前这条验收命令写不出这个文件**。

★ **数值来源已查清**：`total_to_manufacture = 3.2714499345031918` 全仓只出现在**散文与测试固件**里（`capabilities.yaml` 自身 · `docs/ROADMAP.md` · `commit-messages/_msg_costing.txt` · `promote_costing.py` · `tests/test_sw_costing_contract.py` 的 `GetMaterialCost=3.2714499345031918` 等）——**没有任何证据文件含这个数值**（按铁律 3：仓内证据里查不到，不拿测试固件当真机证据顶替）。

---

## V-3 · `mold_analysis` 以 `verified` 挂出 `mold_undercut_detect`，而它引的两份证据文件对该工具零命中，条目自己写着「仍未查证」

**判定：成立**（★ 与 V-1 **不同类**：这里是**证据根本没覆盖**，不是「否定被写成肯定」；条目 `limitations` 有如实披露，故属覆盖缺口）

**仓内那一段** —— `capabilities.yaml` 的 `mold_analysis` 条目：

> "id": "mold_analysis",
> "level": "verified",
> …
> "solidworks_mold_draft_analysis",
> "solidworks_mold_undercut_detect"

**目标那一段** —— 同条目 `limitations` 逐字写着该工具未查证：

> ⚠ **仍未查证**：`MoldUndercutDetect` 官方是 `Void`，而 `MoldUndercutDetect2` 有 **5 个 `Col*` 颜色参数** ⇒ ★ **结果是用颜色标在面上**；★ 两份官方文档**都没有 Remarks**，枚举目录里也**只有** `swPartingSurfaceMoldParmType_e` ⇒ ★ **「怎么把颜色读回来」仍是未知**（铁律 5）。

**一句话依据**：该条目两份证据文件的 `steps` / `cases` **一个 `undercut` 字样都没有**（`mold-evidence-smoke.json` 五项全部是 `mold_evidence()` 只读入口，`mold-draft-analysis-owner.json` 四项全部是 `MoldDraftAnalysis` 的**归属接口**排查）⇒ `solidworks_mold_undercut_detect` 在**本条目自己的证据里零覆盖**，却被一条 `verified` 条目背书；承载它的实现 `scripts/sw_mold.py::mold_undercut_detect` 确实存在（不是「没做」，是「没验」）。

★ **同类但较软的一处（只作记录，不单列为问题）**：`costing_readback`（`verified`）挂 **8** 个工具，而它那条证据只覆盖 6 步读数（`get_costing_manager` · `costing_evidence` · `body_count` · `list_bodies` · `list_templates` · `read_analysis`），`solidworks_costing_read_body` 与 `solidworks_costing_method_value`（实现为 `sw_costing.py` 的 `read_cost_body_report` / `get_costing_method_report`）**未被该证据覆盖**；但条目未对这两个作任何肯定声明（其 `limitations` 反而写了「按名字读那条路在本机走不通」），方向未反转，故不判。

---

## 附 · 本域「否定被照实写出 / 方向一致」的正确样本（不判为问题，供对照）

★ 用户要求的第三类（证据否定 / 条目肯定）在本域**只找到 V-1 这一处**；其余两处否定证据都被**照实写进了条目**，是反过来的正确做法：

- `costing_readback` 引 `output/costing-evidence.json`（`partial` / 5/6、`list_templates ✗`），条目 `limitations` 逐字写「★ **真机 5/6** … ⚠ `list_templates` ✗ —— 报 `<unknown>.GetTemplatePathnames`」⇒ **证据否定、条目也否定**。
- `costing_templates_and_defaults` 引 `output/costing-templates-evidence.json`（`verdict: pass`，3 步全 `ok: true`），条目写「PASS 3/3 … `count=2`」⇒ 方向一致。
- `mold_analysis` 引的两份文件（5/5 + 4/4 `pass`）与条目写的「冒烟 5/5 · 探针 4/4」「`IFeatureManager` ⇒ AttributeError · `IModelDoc2` ⇒ 能取到」逐字对得上 ⇒ 方向一致。

---

**计数**：核了 **5** 处引用（4 条 `verified` 条目引的 4 个证据文件，逐个打开读到内容并与条目原文对读），**对不上 3** 处（V-1 `verdict: pass` vs 文件 `partial` · V-2 闭环与成本数值在证据文件里查不到 · V-3 `undercut_detect` 无证据却挂在 `verified` 下）。
**查不到、不顶替的**：条目声称的 `total_to_manufacture = 3.2714499345031918` 与「4 条模板路径（`.sldctc` / `.sldcts`）」在**任何**证据文件里均查不到（按铁律 3 记「查不到」，未拿 `tests/test_sw_costing_contract.py` 的固件值当真机证据）；`output/costing-evidence.json` 的真实产出方**查不到**（当前 `tools/verify_costing_e2e.py` 写不出它的键形状，未用相似文件顶替）。