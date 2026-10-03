# vd50-A · sheetmetal · 能力 level 与真机证据对账

**范围**：`capabilities.yaml` 里 sheetmetal（⑦ 钣金）域的条目，共 **2 条** —— `sheet_metal`（`level: verified`）· `sheet_metal_creation`（`level: stitched`）。
**域归属判据**：`docs/union-coverage-matrix.md` 把 `sheet_metal_*` 系列工具标为「⑦ 钣金」；`tools/build_union_map.py` 的 `DOMAIN_LABELS` 里 `"sheetmetal": "⑦ 钣金"`。台账里 `mcp_tools` 含 `solidworks_sheet_metal_*` 的**只有这两条**（逐条枚举核过，`dfm_checks` 的 `cadstudio_check_dfm` 不属本域）。
**只读核验**（未改仓内任何文件）；本文件是唯一写入。
**核了 9 处，对不上 5 处**（其中「★ 证据否定 / 条目写成肯定」方向 **3 处**）。

---

## 〇 · 逐条清点（9 处 → 存在性 + 内容一致性）

| # | 条目 | 被核的那一处 | 文件在？ | 内容与条目一致？ |
|---|---|---|---|---|
| 1 | `sheet_metal` | evidence #1 `pytest tests/test_sw_sheet_metal.py` | ✅ 在 | ❌ 见 **V-1** |
| 2 | `sheet_metal` | evidence #2 `pytest tests/solidworks_sheet_metal_regression.py（钣金）` | ✅ 在 | ❌ 见 **V-2** |
| 3 | `sheet_metal` | limitations 第 1 条「开放 U 型轮廓双折弯」 | — | ❌ 见 **V-3**（★ 最严重类） |
| 4 | `sheet_metal` | limitations 第 1 条「含折弯线 DXF」 | — | ❌ 见 **V-4**（★ 最严重类） |
| 5 | `sheet_metal` | limitations 第 1 条「板厚/半径/K 因子参数重开回读」 | — | ❌ 见 **V-5**（★ 最严重类） |
| 6 | `sheet_metal` | limitations 第 2 条「6 个创建入口里 2 个可跑」 | — | ✅ 一致 |
| 7 | `sheet_metal` | `level: verified` 挂在**建模能力**上 | — | ✅ 判定口径本身见 V-1/V-2 附注 |
| 8 | `sheet_metal_creation` | evidence「`create_base_flange` 真机验过…其余三条到不了」 | — | ✅ 一致（照实写否定） |
| 9 | `sheet_metal_creation` | `level: stitched` 而非 `verified` | — | ✅ 正确（与 V-1…V-5 互为对照） |

★ **#6 / #8 / #9 共 3 处查不出问题**：条目自己写否定的地方（4/6 入口到不了、`stitched` 不冒进）都写对了。

---

## V-1 · ★★ `verified` 的 evidence #1 **全程不碰 COM、也从不调 `create_base_flange`**

**判定：成立**

**仓内那一段** —— `capabilities.yaml` 的 `sheet_metal` 条目（`label` 与 `evidence` 逐字）：

> `"id": "sheet_metal",` … `"label": "钣金建模与展开",` … `"level": "verified",` … `"evidence": [` / `  "pytest tests/test_sw_sheet_metal.py",`

**目标那一段** —— 该测试文件里与钣金有关的**全部** import、替身类与三个用例名（逐字）：

> `"""原生钣金封装的离线契约测试。"""` … `from sw_sheet_metal import BaseFlangeSpec  # noqa: E402`
> `class FakePart:` / `    def ExportToDWG2(self, *args):` / `        self.args = args` / `        return True`
> `def test_flat_pattern_export_uses_alignment_array_and_option_bitmask(tmp_path):` / `def test_flat_pattern_export_requires_saved_model(tmp_path):` / `def test_base_flange_spec_rejects_invalid_manufacturing_values(spec, message):`

**一句话依据**：该文件从 `sw_sheet_metal` 只导入 **`BaseFlangeSpec`（一个纯 dataclass）**，三个用例分别测 `export_flat_pattern_dxf` 对 **`FakePart` 替身**的入参位掩码、以及 `BaseFlangeSpec.validate()` 的抛错 ⇒ 全程**不碰 COM、不调 `create_base_flange`、不调 `sheet_metal_evidence`** ⇒ 拿它当「钣金建模与展开」这条 `verified` 的运行证据是**零信息量**的。
★ 实跑复核（本机，2026-10-04）：`python -m pytest tests/test_sw_sheet_metal.py -q` ⇒ `6 passed in 0.18s` —— **它是绿的**，问题不在「跑不过」，在「跑的东西与被声明的能力无关」。
★ 对照（同域真跑机器的写法）：`tests/solidworks_sheet_metal_regression.py` 才 `from sw_connect import connect_solidworks, get_com_member, mm, new_document, open_document, save_document  # noqa: E402`。

---

## V-2 · ★★ 同一 `verified` 条目的 evidence #2 **按字面写法跑不起来**（pytest 收 0 个用例）

**判定：成立**

**仓内那一段** —— 同一条目的 `evidence` 第二项：

> `  "pytest tests/solidworks_sheet_metal_regression.py（钣金）"`

**目标那一段** —— 该文件的模块骨架（逐字，**全文没有任何 `def test_`**，只有 `_` 前缀的私有校验函数与一个命令行 `main`）：

> `"""SolidWorks 2026 原生钣金样件、展开 DXF 与重开回归。"""` … `def _validate_evidence(evidence: dict, *, stage: str) -> None:` … `def _validate_dxf(path: Path) -> dict:` … `def run_regression(output_dir: Path, *, visible: bool = True, wait_seconds: int = 12) -> dict:` … `def main() -> int:` … `if __name__ == "__main__":` / `    raise SystemExit(main())`

**一句话依据**：按证据原文「pytest \<该文件\>」执行，该文件 `def test_` 计数为 **0** ⇒ pytest **收集不到任何用例**，实际入口是 `__main__` 命令行（默认 `--output-dir` 指向 `%TEMP%\solidworks_sheet_metal_regression`）。
★ 实跑复核（本机，2026-10-04，两条命令同证）：
```
> python -m pytest tests/solidworks_sheet_metal_regression.py -q
no tests ran in 0.14s        EXIT=5
> python -m pytest tests/solidworks_sheet_metal_regression.py -q --collect-only
no tests collected in 0.14s  EXIT=5
```
★ **两条 evidence 合起来的净效果**：`sheet_metal` 挂在 `verified` 上的两条，一条**证明不了建模**（V-1），另一条**按字面跑不出用例**（V-2）⇒ 该 `level` 在本域**没有可执行的 pytest 支撑**。
★ 补充（只作背景，不作判据）：该脚本**跑过一次就会落盘一个结果文件** —— `result_path = output_dir / "sheet_metal_regression_result.json"`。本机核过三处**均查不到**：仓内递归搜 `sheet_metal_regression_result.json` 与 `u_channel*` **0 命中**，`%TEMP%\solidworks_sheet_metal_regression` **不存在** ⇒ 按铁律 3 记「**查不到**该回归跑过的落盘痕迹」，**不据此断言它没跑过**。

---

## V-3 · ★★★ 「开放 U 型轮廓双折弯」已真机验证 —— **证据明确否定，条目写成肯定**

**判定：成立（本片最严重的一类）**

**仓内那一段（条目写的）** —— `capabilities.yaml` 的 `sheet_metal` 条目 `limitations` 第 1 项，逐字：

> `SW2026 SP01.1 已真机验证现代 BaseFlange FeatureData、开放 U 型轮廓双折弯、板厚/半径/K 因子参数重开回读和含折弯线 DXF；边线法兰、放样折弯、转钣金、折弯表及多版本矩阵仍需后续真机回归`

**目标那一段（证据写的）** —— 同一仓、同一入口、**逐字相反**，`scripts/sw_sheet_metal.py` 的 `SHEET_METAL_RUNTIME_STATUS` 里 `create_base_flange` 的实测记录：

> `"**闭轮廓**真机建成：特征树出现「钣金6 / 基体-法兰1 / 平展型式6」。"`
> `    "⚠ **开放折线（轮廓法兰）真机失败**：`CreateFeature(IBaseFlangeFeatureData) 创建失败`"`
> `    "（2026-10-01 补测，见 probe_gusset_with_bend.py）⇒ **`True` 仅对闭轮廓成立**"`

**目标那一段（补测脚本，证实那条否定是实测不是推断）** —— `probe_gusset_with_bend.py` 的建形与判定：

> `# 造一段**折弯**：先画一条开放折线（两段），做成轮廓法兰（profile flange）` … `get_com_member(sm, "CreateLine", -0.05, 0.0, 0.0, 0.05, 0.0, 0.0)` … `get_com_member(sm, "CreateLine", 0.05, 0.0, 0.0, 0.05, 0.05, 0.0)`
> `            SM.create_base_flange(model, "Sketch1",` … `            print("[2] base_flange 成功（开放折线 ⇒ 轮廓法兰，**应含折弯**）")` … `except Exception as exc:  # noqa: BLE001` / `            print("[2] ✗ base_flange 失败: %s" % str(exc)[:70])`

**一句话依据**：条目把「开放 U 型轮廓双折弯」写进**已真机验证**清单，而模块自己的运行期实测表逐字记「**开放折线真机失败**」并给出失败原文 `CreateFeature(IBaseFlangeFeatureData) 创建失败`、注明补测出处、且明写「`True` **仅对闭轮廓成立**」⇒ **条目肯定的那个形态，正是仓内证据否定的那个形态**。
★ **同一条目自己也知道这件事** —— 它的 `limitations` 第 2 项逐字写着同一结论：`✓ \`create_base_flange\`（但**只对闭轮廓成立**，开放折线的轮廓法兰实测失败）`。⇒ **同一条目内两条 limitations 互相打架**：第 1 条说开放已验证，第 2 条说开放实测失败。
★ 附带：`README.md` 也跟着写了 `SW2026 已验证开放 U 型轮廓双折弯` ⇒ 同一个未经证实的结论在仓内有两处肯定表述。
⚠ **不裁决版本先后**：本片**查不到**「开放 U 型轮廓」这条肯定结论出自哪一次真机运行（`git log -- <两文件>` 只返回一次合并提交 `914bf5e`，历史被压平）⇒ 按铁律 5 不猜「谁更新」，只判**证据与条目当前文本对不上**。

---

## V-4 · ★★★ 「含折弯线 DXF」已真机验证 —— **唯一在盘的 DXF 证据记的是 `ok: false`，条目写成肯定**

**判定：成立（本片最严重的一类）**

**仓内那一段（条目写的）** —— 同上 `limitations` 第 1 项里的这一段：

> `板厚/半径/K 因子参数重开回读和含折弯线 DXF`

**目标那一段（证据写的）** —— 仓内**唯一**那份钣金展开 DXF 的真机落盘证据 `output/flat-pattern-dxf-evidence.json`，逐字：

> `  "export_flat_pattern_dxf": {` / `   "ok": false,` / `   "values": {` / `    "format": "dxf_flat_pattern",` / `    "exists": false,` / `    "size_bytes": 0,` / `    "grew_or_created": false,` / `    "error": "ValueError: 导出展开 DXF 前必须先保存钣金零件"` … ` "verdict": "partial",`

**目标那一段（该结论在知识库里的定性，逐字）** —— `docs/known-facts.md` 第 322 条：

> `**\`export_flat_pattern_dxf\` 的真前置是「**已保存**的钣金件」—— 而"保存"是**硬约束⑦ 明禁**的** ⇒ ★ 这一条**在红线内验不了**（2026-10-03，轮 407）。` … `⇒ ★ 处置：★ **保持不注册**`

**一句话依据**：条目把「含折弯线 DXF」列进「已真机验证」，而**唯一**在盘的该功能真机证据 `output/flat-pattern-dxf-evidence.json` 记的是 `ok: false` / `exists: false` / `size_bytes: 0` / `grew_or_created: false`、`verdict: "partial"`；知识库第 322 条进一步把它定性为「**在红线内验不了**、**保持不注册**」⇒ 条目这一项**没有正例支撑**。
★ 附一条**方向相反、要一并看清**的证据（不判为问题）：`output/dwg-magic.json` 记 `  "dxf": {` / `   "exists": true,` / `   "bytes": 20209,` / `   "head_ascii": "  0\\r\\nSECTION\\r\\n  ",` / `   "kind": "DXF"` —— 即**文件本身**确实存在过（2026-10-01 轮 156，`tools/probe_dwg_magic.py` 先 `sw_connect.save_document` 再导出，与第 322 条「必须先保存」的定性一致）。⚠ 但那份证据**只判文件头与字节数，不含折弯线**（`kind: DXF` 之外无任何 `bend` 字样，脚本 `magic()` 也只 `read_bytes()[:16]` 读头）⇒ 「**含折弯线**」这一层**查不到**落盘证据。

---

## V-5 · ★★★ 「板厚/半径/K 因子参数重开回读」已真机验证 —— **在盘产物里查不到任何重开记录**

**判定：成立（本片最严重的一类）**

**仓内那一段（条目写的）** —— 同上 `limitations` 第 1 项里的这一段：

> `板厚/半径/K 因子参数重开回读`

**目标那一段（唯一声称做重开回读的代码，逐字）** —— `tests/solidworks_sheet_metal_regression.py::run_regression` 的重开段与判据段：

> `    reopened = open_document(sw, str(part_path), silent=True, raise_on_error=True)` / `    reopened_evidence = sheet_metal_evidence(reopened)` / `    _validate_evidence(reopened_evidence, stage="重开后")` … `    for key, expected in (("thickness_m", mm(2.0)), ("bend_radius_m", mm(2.5)), ("depth_m", mm(100.0))):` / `        if abs(float(reopened_parameters[key]) - expected) > 1e-7:` / `            raise RuntimeError(f"重开参数不一致: {key}={reopened_parameters[key]}")`

**目标那一段（查不到的那一侧，逐字给出搜的范围与结果）** —— 该脚本跑过必落盘：`result_path = output_dir / "sheet_metal_regression_result.json"`，而该文件的返回体里含 `"reopened_evidence": reopened_evidence,` 与 `"parameter_roundtrip": {"created": created_parameters, "reopened": reopened_parameters},`。本机三处检索**均 0 命中**：仓内递归搜 `sheet_metal_regression_result.json` **0 命中**、搜 `u_channel*`（该脚本写死的 `part_path = output_dir / "u_channel_sheet_metal.SLDPRT"`）**0 命中**、`%TEMP%\solidworks_sheet_metal_regression` 目录**不存在**；另对 `output/` 全目录 JSON 检索 `reopen|重开|reopened` 只有 `add-view-two-trials-evidence.json` 与 `official-enum-scale.json` 两个**与钣金无关**的文件命中。

**一句话依据**：条目把「板厚/半径/K 因子参数重开回读」写进已真机验证清单，而声称做这件事的代码在仓内**唯一一处**、其产物**在盘上完全查不到**（按铁律 3 记「查不到」，**不据此断言它没跑过**）⇒ 该子项**没有落盘证据支撑**。
★ ★ **这三条（V-3/V-4/V-5）指向同一个机制**：条目 `limitations` 第 1 项那句「已真机验证 …」是一次**打包断言**，把「BaseFlange FeatureData 走通了（这部分成立）」与「开放轮廓 / 含折弯线 DXF / 重开回读（这三部分查不到正例或被证据否定）」并列成了一句肯定陈述 ⇒ **读者无法从条目分辨哪几项真有正例**。

---

## 附 · 核过但**查不出问题**的 3 处（不判为问题，供对照）

| # | 核了什么 | 结论 |
|---|---|---|
| A-1 | `sheet_metal` `limitations` 第 2 项「6 个创建入口里 2 个可跑」 | ✅ 与 `SHEET_METAL_RUNTIME_STATUS` 逐项对上：✓ `create_base_flange`（限闭轮廓）· ✓ `sheet_metal_evidence` · ✗ `create_one_bend` / `create_edge_flange` / `create_gusset` / `create_draft` |
| A-2 | `sheet_metal_creation` 的 evidence「`create_base_flange` 真机验过（SW 2026 SP4.1 ⇒ 特征树出现钣金特征）· ⚠ 其余三条到不了」 | ✅ 与状态表一致，且**如实写否定**；在盘证据 `output/flat-pattern-dxf-evidence.json` 里 `features` 段确有 `"name": "基体-法兰1",` / `"type": "SMBaseFlange",` 与 `"has_base_flange": true` |
| A-3 | `sheet_metal_creation` 的 `level` 取值 | ✅ 它是 `stitched` 而不是 `verified` —— 与 V-1…V-5 的证据状态**相符**（同一批能力，拆出的那一条没有冒进） |

★ 另附一条**做对了的诚实写法**（不判为问题）：`sheet_metal_creation` 的 `source_evidence` 逐字写 `scripts/sw_sheet_metal.py 的 6 个 create_*`，`limitations` 里也逐字标注 `★ 其余三条到不了（known-facts 47/43）` ⇒ 它没有把「4/6 不可用」写成「6 个都能跑」。

---

## 查不到、不顶替的（铁律 5）

| 想查的 | 结果 |
|---|---|
| 「开放 U 型轮廓」那条肯定结论出自哪一次真机运行 | **查不到** —— `git log --oneline -- <capabilities.yaml> <scripts/sw_sheet_metal.py>` 只返回一次合并提交 `914bf5e merge: 把代码仓 sw-skill-fork 并进工作区，两仓合一`，历史被压成单次，先后判不了 |
| `tests/solidworks_sheet_metal_regression.py` 是否真在真机跑过 | **查不到** —— 产物路径（`%TEMP%\solidworks_sheet_metal_regression\sheet_metal_regression_result.json`、仓内 `u_channel_sheet_metal.SLDPRT`）三处检索全部 0 命中；**不据此断言「没跑过」**，只判「落盘证据不存在」 |
| 「含折弯线 DXF」在文件内容层面的证据 | **查不到** —— `output/dwg-magic.json` 只记文件头与字节数（`"kind": "DXF"`），脚本 `probe_dwg_magic.py` 的 `magic()` 只 `read_bytes()[:16]`；全仓无任何解析折弯线图层的证据文件 |
| 域归属是否有权威字段 | **查不到** —— `capabilities.yaml` 的条目**没有 `domain` 字段**（全文检索 `"domain"` / `domains:` 均 0 命中）；本片的域归属按 `tools/build_union_map.py` 的 `DOMAIN_LABELS` 里 `"sheetmetal": "⑦ 钣金"` + `docs/union-coverage-matrix.md` 的工具标注推定，并已用「`mcp_tools` 含 `solidworks_sheet_metal_*` 的条目只有这两条」交叉确认 |

---

**计数**：核了 **9** 处（2 条条目 × 证据存在性 / 证据内容一致性 / 结论方向），**对不上 5** 处：
V-1 `verified` 的 evidence #1 不碰 COM · V-2 evidence #2 按字面收 0 个用例 · ★★ V-3 「开放 U 型轮廓双折弯」证据否定、条目肯定 · ★★ V-4 「含折弯线 DXF」在盘证据为 `ok:false / verdict:partial`、条目肯定 · ★★ V-5 「参数重开回读」在盘查不到任何落盘证据、条目肯定。
**3 处查不出问题**（A-1 入口计数一致 · A-2 `sheet_metal_creation` 的 evidence 如实写否定 · A-3 `stitched` 未冒进）。