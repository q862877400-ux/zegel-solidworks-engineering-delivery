# 完成报告：`pilot`→五级迁移（执行方 → 改 AGENTS.md 的对话）

> **迁移已完成、已提交、已回归。** 提交 `469064f`（代码副本 `C:\swprojects\sw-skill-fork`）。
> 裁断三条要求全部满足。**但过程中发现两条你没预料到的事，其中一条要你裁。**

---

## 一、裁断要求三说「`unattended_allowed()` 的全部调用点」—— 实际是 **4 条路径**

我上一份报告只报了 1 条（`unattended_allowed()` 自己），**那是不完整的**。
这次动手时被测试逼出了全部 4 条：

| # | 位置 | 迁移前 | 迁移后会怎样 |
|---|---|---|---|
| **1** | `scripts/capabilities.py` `unattended_allowed()` | `level == "verified"` | 唯一有名字的那个 |
| **2** | `apps/.../queue_worker.py:96` 任务门禁 | `if level == "verified": continue` | **静默解除那 13 条的复核要求** |
| **3** | `scripts/sw_capability_probe.py:142` | 内联 `ready_for_unattended_use = (level == "verified")` | **静默发授权给那 13 条** |
| **4** | `apps/.../engineering_orchestrator.py:331` `_normalise_level` | 不认识 `stitched`，靠 `fallback` 兜 | 靠**碰巧**得到正确结果，不是正确 |

**②③ 是测试逼出来的**：只改 ① 之后，
`test_job_is_blocked_for_reference_only_capability` 与 `test_sw_capability_probe`
**立刻变红** —— 正是它们在挡这次泄漏。**如果我只按上一份报告列的那 1 条去改，
这 13 条会在队列和探针里被静默解除复核要求，而测试是绿的。**

**⇒ 建议 R11 补一句**：授权判据的**真源是 `allowed_modes`**，
任何按 `level` 推断授权的写法都算违规；`check_union_conventions.py` 里可以加一条
「搜 `level == "verified"` 与授权词同现」的静态检查，比事后靠测试挡更早。

（这条我按「形态归你」留给你判要不要加；**代码侧我已经全改了**。）

---

## 二、新空档（**要你裁**）：`stitched` 必须有 `provenance`，但那 6 条填不出来

你的 B2：

> `level` 是 `source_verified` / `stitched` / `indexed` 之一时，`provenance` 必须非空。

**但那 6 条 `stitched` 是 `dfm_checks` / `surface_modeling` / `mold_tools` /
`autocad_headless_preview` / `dxf_preview_scene` / `routing` —— 全是我们自研的，
没有来源仓，`provenance{repo,license,files,upstream_verified}` 一个字段都填不出真值。**

**⇒ R6 一落地就会在这 6 条上红。** 三条路：

| | 做法 | 后果 |
|---|---|---|
| **A** | B2 加限定：**`provenance` 只在「来源派生」时必填**；自研但未运行的条目（`stitched` 且无外部来源）允许 `provenance` 为空 | ✅ 语义准；⚠ 要能判「是否来源派生」—— 我建议判据就是 `provenance` 本身，不自证 |
| **B** | 给它们填一个指向本仓库的 `provenance` | ❌ 「本项目自身是 MIT，不作为 provenance 来源」（你 B2 自己写的） |
| **C** | 这 6 条改回别的 level | ❌ 没有更贴切的：它们不是 `verified`（没跑）、不是 `indexed`（有实现） |

**我倾向 A，但这条是形状问题，归你。**
**现在我没给它们填任何 `provenance`**（填假值比空着坏），**R6 还没实现在代码里**，
所以门禁当前是绿的 —— **但 R6 一写就会红。**

---

## 三、迁移做了什么（供你对 R1–R10）

### 数据（`capabilities.yaml`，`schema_version` 1.0 → 2.0）

```
13 条 pilot 且有 verified_versions  → verified + evidence（每条都指向真实测试文件，已实跑确认）
 6 条 pilot 且无 verified_versions  → stitched
 原 8 条 verified                    → 补 evidence；补 unattended
 原 19 条 pilot（含迁 verified 的）  → 不补 unattended

结果: verified 21 / stitched 6 / not_implemented 1
      21 条带 evidence；8 条带 unattended
```

**`evidence` 全是真跑过的测试文件**，不是编的：
`external_spur_gear_geometry`/`parameter_updates`/`custom_properties_and_bom`/`weldments`
→ `tests/test_cad_reliability.py`；`pack_and_go` → `tests/test_sw_delivery.py`；
`drawings_and_bom` → `tests/test_delivery_compare.py`；`headless_open_format_writing`
→ `tests/test_headless_cad_writer.py`；`simulation_and_fea` → `tests/test_fea_analysis.py`；
`autocad_*` → `tests/test_acad_*`；`requirements_planning` → `tests/test_engineering_orchestrator.py`。
**这 21 条对应的测试合起来实跑 158 passed / 1 failed（那 1 个是已知上游基线失败）。**

### 等价性验收（你的要求二）

```
tools/freeze_unattended_baseline.py    改动之前冻结 → tests/unattended_baseline.json
tests/test_unattended_equivalence.py   7 条测试
   · 路径 1（unattended_allowed）集合 == 基线
   · 路径 2（allowed_modes）集合 == 基线
   · 路径 1 与路径 2 必须互相一致
   · R11：allowed_modes 值域 + level != verified 不得带 unattended
   · 基线上的能力迁移后仍带 unattended（防收紧）

实测：迁移前 8 条 = 迁移后 8 条，逐条相同。
```

### 门禁与回归（实际跑过的命令）

```
python -m compileall -q scripts tools apps tests         exit 0
python scripts\check_member_names.py                     [PASS]
python scripts\check_provenance.py                       [PASS] 271 个合规来源块
python scripts\check_diff_markers.py                     [PASS] 241 个 .py
python scripts\check_union_conventions.py                exit 0（4 组全 PASS）
python -m pytest tests -q                                6 failed / 741 passed / 15 skipped
A7 核查                                                  stitched 带 evidence = 0；verified 缺 evidence = 0
```

---

## 四、一条关于基线的更正（我上一份报告写错了）

我上一份报告说基线是 `2 failed / 738 passed`。**那是错的。**

**用 `git stash` 做干净对照后实测：改动前的基线是 `6 failed / 734 passed / 15 skipped`：**

```
FAILED tests/test_cad_reliability.py::test_discover_installation_supports_injected_filesystem
FAILED tests/test_cad_studio_cli.py::test_check_dfm_cli_generates_report
FAILED tests/test_cad_studio_cli.py::test_cli_run_fea_convergence_rejects_invalid_request_without_output
FAILED tests/test_cad_studio_cli.py::test_cli_review_advanced_geometry_writes_report
FAILED tests/test_dfm_review.py::test_dfm_review_cli_accepts_profile_and_records_effective_limits
FAILED tests/test_release_check.py::test_release_check_passes_current_tree
```

**那 4 个 CLI 测试是「不稳定」的** —— 它们 `subprocess.run` 起子进程，
某些运行下红、某些下绿（我先后两次跑同一份未改动代码，得到 2 failed 与 6 failed）。

**⇒ 本次迁移的判据是「失败列表与基线逐条相同」，不是「失败数 = 2」。**
**迁移后失败 6 个，与上面 6 条完全一致；+7 passed = 我新增的等价性测试。**

**⚠ 提醒你那边**：如果体检或验收有「测试必须 N 绿」这类判据，**这个仓库的 N 是不稳的**。
不是本次引入的 —— 未改动时也会在 2 与 6 之间跳。

---

## 五、还没做的（等你裁完上面第二节）

| | 说明 |
|---|---|
| R6 的代码实现 | 卡在第二节那个空档；R1–R5、R7、R9、R10 可以随时落地 |
| 「生成器产 `union-level-audit.md`」（B3 / R8） | 未做。它要读 level 与来源覆盖，现在数据已就位，可以做 |
| `provenance` 字段本身 | 现有 28 条**一条都不需要**（全自研）—— 它是给 B 级并入的条目用的 |

**你要我接着做 R1–R5、R7–R10 的机判落地，还是先等第二节的裁断？**
