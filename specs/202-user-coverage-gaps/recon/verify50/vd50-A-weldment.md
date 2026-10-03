# vd50-A · weldment · 能力 level 与真机证据对账

**范围**：`capabilities.yaml` 里 weldment 域 `level=verified` 的 **3 条**：`weldments` · `weldment_cut_list` · `weldment_profile_and_curve`。
**只读核验**（未改仓内任何文件）；本文件是唯一写入。
**核了 10 处引用，对不上 4 处**（其中「条目肯定 / 证据否定或未验」方向 **1 处**）。

---

## 〇 · 逐条清点（10 处引用 → 存在性 + 内容一致性）

| # | 条目 | 引用 | 文件在？ | 内容与条目一致？ |
|---|---|---|---|---|
| 1 | `weldments` | `output/structural-member-evidence.json` | ✅ 在 | ✅ 一致 |
| 2 | `weldments` | `pytest tests/test_cad_reliability.py（焊件）` | ⚠ 文件在，但那两行是自证 | ❌ 见 V-2 |
| 3 | `weldment_cut_list` | `output/cut-list-chain-evidence.json` | ✅ 在 | ✅ 一致 |
| 4 | `weldment_cut_list` | `output/cut-list-chain.csv` | ✅ 在 | ✅ 一致（224 字节） |
| 5 | `weldment_cut_list` | `out-cut-list-property-names-evidence.json` | ❌ **无此名** | — 见 V-1 |
| 6 | `weldment_cut_list` | `output/weldment-tools-e2e-evidence.json` | ✅ 在 | ✅ 一致 |
| 7 | `weldment_cut_list` | `output/weldment-evidence.json`（条目自己点名的旧证据） | ✅ 在 | ✅ 条目已自行标注「过时的」并更正，**不判** |
| 8 | `weldment_profile_and_curve` | `output/weldment-profile-evidence.json` | ✅ 在 | ✅ 一致 |
| 9 | `weldment_profile_and_curve` | `output/structure-system-evidence.json`（limitations 里） | ✅ 在 | ✅ 一致（`verdict: partial`，条目照实写否定） |
| 10 | `weldments` | 「本机 … 有 **111 个** `.sldlfp`」 | ✅ 现场实测 **111** | ✅ 成立 |

★ **1/2/3/4/6/8/9/10 共 8 处查不出问题** —— 三条 `verified` 条目引的主证据全部**真实存在**，且**证据的结论方向与条目写的方向一致**（该 pass 的 pass、该说否定的说否定）。

---

## V-1 · 证据文件名对不上（`level=verified` 的 `weldment_cut_list` 引了一个仓内不存在的文件名）

**判定：成立**（轻微 —— 真文件在，只是名字差一个前缀）

**仓内那一段** —— `capabilities.yaml` 的 `weldment_cut_list` 条目 `evidence`：
> 而唯一没过的 `set_cut_list_properties` 真因是**本地化名**：英文名（`Description`/`Material`）报「回读失败」，而**中文名（`说明`/`材料`）写入并回读得到**（out-cut-list-property-names-evidence.json PASS）。

**目标那一段** —— 产出方的实际写盘路径，`tools/probe_cut_list_property_names.py`：
> OUT = Path(r"D:\AI\SW\output\cut-list-property-names-evidence.json")

**一句话依据**：条目逐字引的文件名 `out-cut-list-property-names-evidence.json` 全仓不存在，真实文件是同目录的 `cut-list-property-names-evidence.json` ⇒ 按铁律 3 记「查不到」，且该文件**内容是支持的**（`"trial": "chinese"` / `"ok": true` / `"verdict": "pass"`），故只判**文件名错**，不判结论错。

---

## V-2 · `weldments` 的 pytest 证据是**循环自证**（断言的就是被断言的那句话）

**判定：成立**

**仓内那一段** —— 条目 `evidence` 第二项：
> "pytest tests/test_cad_reliability.py（焊件）"

**目标那一段** —— 该测试里「焊件」的全部内容，`tests/test_cad_reliability.py`：
> assert index["weldments"]["level"] == "verified"
> assert index["weldments"]["verified_versions"] == ["2026"]

**一句话依据**：该测试只从 `capabilities.yaml` 读出 `level` 字段并断言它等于 `"verified"`，全程**不碰任何焊件代码、不开 SolidWorks** ⇒ 焊件能力整体回归，它仍会绿 ⇒ 拿它当 `verified` 的运行证据是**零信息量**的（与它同文件里真跑 `tools/verify_routing_e2e.py` 的那条 `routing` 注释形成对照）。

---

## V-3 · `weldments` 条目**内部自相矛盾**：`limitations` 说没挂，`mcp_tools`/`evidence` 说建成且已挂

**判定：成立**

**仓内那一段** —— 同一条目的 `limitations`：
> ⚠ **没挂的 4 个及原因**：configure_member_profile / configure_split_member（★ 要宿主对象，需新注入键）· **create_structural_member（★ segment_groups 是嵌套结构）**· iter_features_recursive（★ 内部辅助，非工具候选）

**目标那一段** —— 同一条目的 `mcp_tools` 与 `evidence`：
> "solidworks_weldment_create_structural_member"
> 真机 … ⇒ **建成 `square-rods (1)`**，★ 判据是**特征树**（不是计数）：`new_type_names` = **["WeldMemberFeat", "WeldmentFeature"]**。证据 output/structural-member-evidence.json。

**一句话依据**：`limitations` 说 `create_structural_member` 因入参表达不了而「没挂」，而同一 `verified` 条目的工具清单列了它、证据文件 `structural-member-evidence.json` 也确有 `"ok": true` / `"verdict": "pass"` ⇒ 两段必有一段是轮 270 的**过期残留**，未随轮 428/498 更新。
⚠ 方向说明：这是**「条目里写否定、而实际肯定」**（与 V-4 相反），且已有一条现成证据正面推翻它 ⇒ 结论上以 evidence 为准，但**同一条 verified 条目内不该留着反向陈述**。

---

## ★★★ V-4 · 「条目写成肯定、而仓内自己写着未验」——`verified` 条目把两个自述未验的工具挂了出去

**判定：成立**（★ 本片最重的一处；这是用户要求单列的那一类）

**目标那一段** —— `weldments` 条目把它标成 `verified` 并挂上这两个工具：
> "id": "weldments",
> "level": "verified",
> …
> "solidworks_weldment_read_property_manager",
> …
> "solidworks_weldment_create_profile_center_mate",

**仓内那一段** —— 仓里另两条 `weldment_*` 条目**逐字说这两个工具没验**：

`weldment_cut_list` 的 `limitations`：
> 而 `read_property_manager` 那条本轮**未验**（它读的是 PM 页，与本链无关）。

`weldment_profile_and_curve` 的 `limitations`：
> ⚠ **未验**：`create_profile_center_mate`（★ 需**装配体 + 两个实体**，本轮未准备）。

**一句话依据**：`weldments` 的 `evidence` 里唯一带真机运行的只有 `create_structural_member` 一项，11 个 `mcp_tools` 里的 `read_property_manager` / `create_profile_center_mate` 既无证据文件、又被仓内条目**明文标注「未验」**，而承载它们的条目等级是 **`verified`** ⇒ 这两个工具的实际等级至多 `stitched`，却被一条 `verified` 条目背书。
★ 补充（只读复算，供交叉印证）：`weldments` 11 个工具中，`create_cut_list`/`set_cut_list_properties`/`export_cut_list_csv`/`weldment_evidence`/`ensure_cut_list`/`update_cut_list` 6 个由 `weldment_cut_list` 的证据覆盖，`create_weldment_profile` 1 个由 `weldment_profile_and_curve` 的证据覆盖，`create_structural_member` 1 个由本条目证据覆盖 ⇒ **余下 3 个（含上述 2 个）全无真机证据**，其中 2 个被明文标「未验」。

---

## 附 · 三条 `verified` 里「否定被照实写出」的正确样本（不判为问题，供对照）

★ 用户要求的第三类（证据否定 / 条目肯定）在本域**只找到 V-4 这一处**；其余的否定证据都被**照实写进 `limitations`**，是反过来的正确做法：

- `output/structure-system-evidence.json` 是 `"verdict": "partial"`、`"tree_before": 19` / `"tree_after": 19` / `"new_features": []`（**没建成**）⇒ `weldment_profile_and_curve` 的 `limitations` 逐字写「**结构系统（Structure System）那条链在 pywin32 上到不了「建成」**」——**证据否定、条目也否定**，方向一致。
- `output/weldment-evidence.json` 是 `"verdict": "partial"` / `"passed": 1, "of": 3`，`create_cut_list` 明写 `ok: false` ⇒ `weldment_cut_list` 的 `evidence` **主动点名它是过时的**并给出更正（`dispid = 174`、4/4 全调通），**没有把否定证据悄悄留着当正面**。
- 同一条 `limitations` 里仍留着的 `⚠ **真机 1/3**：… create_cut_list ⚠ **接口不可达**` 已被上述更正推翻 ⇒ 与 V-3 同型的**过期残留**，但因同条目已有正面更正，**不单列为问题**。

---

**计数**：核了 **10** 处（3 条 `verified` 条目引的证据文件 / 断言 / 文件内数字全部逐个查证到文件内容），**对不上 4 处**（V-1 文件名 · V-2 循环自证 · V-3 条目内自相矛盾 · V-4 未验工具挂在 verified 下）。
**查不到、不顶替的**：`out-cut-list-property-names-evidence.json`（按铁律 3 直接记「无此名」，未拿 `cut-list-property-names-evidence.json` 顶替为「存在」）。
