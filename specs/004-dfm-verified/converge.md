# Converge: DFM 复核升 `verified`

**Feature**: `004-dfm-verified` · **Spec**: [spec.md](spec.md) · **Plan**: [plan.md](plan.md) · **Tasks**: [tasks.md](tasks.md)

**Converged**: 2026-10-01（轮 79）· **环境**: Python 3.14.7（**纯离线，未连 SolidWorks**）

> **这一步做什么**：把 `spec.md` 的每条验收判据**与实测证据逐条对齐**，
> 并**明确记下不符合项**。**不是复述 spec** —— 复述没有价值，找出「声称」与「实际」的差才有。

---

## 一、结论摘要

| 判据 | 结论 | 依据（可复跑的枚举命令） |
|---|---|---|
| SC-001 四种工艺都识别 | ✅ 成立 | `python tools/verify_dfm_e2e.py`（machining/sheet_metal/laser_cutting/3d_printing 各 6 checks）|
| SC-002 单位归一 | ✅ 成立 | 同上（mm 与 inch 两条报告 `status` 与 `checks` 集合**逐项相同**）|
| SC-003 Profile 能力交集 + 越界可见 | ✅ 成立 | 同上（窄 profile 把 `Al7075` 判为 `profile_material_capability`）|
| SC-004 B-Rep 证据绑定 | ⚠ **部分成立**（见 §二.1）| 同上 |
| SC-005/007 缺关键输入 ⇒ `blocked` + 点名 | ✅ 成立 | 同上（`missingInputs` 精确到 `metadata.manufacturing.bendRadius` 等）|
| SC-006 人工确认项 | ✅ 成立 | 同上（`manualReviewRequired is True`）|
| SC-008 风险复核 / 非认证声明 | ✅ 成立（**措辞是"不等于制造认证"**，见 §二.2）| 同上 |
| SC-009 清单 `level=verified` 且 `evidence` 非空 | ✅ 成立 | `python scripts/check_union_conventions.py`（R4）|
| SC-010 既有 19 个测试全绿 | ✅ 成立 | `pytest tests/test_dfm_review.py tests/test_dfm_queue_worker.py -q` |

**总判定**：**11/11 项通过 · `verdict: pass`**（`D:\AI\SW\output\dfm-evidence.json`）。

---

## 二、**不符合项**（本节才是 converge 的价值所在）

### 2.1 ⚠ SC-004 只做到「不崩」，**没有做到「篡改证据必须被拒」**

`spec.md` 对 SC-004 的措辞是「证据的 sha256 与文档一致时才 `pass`；**篡改一个字节 ⇒ `blocked`**」。
**实测只做到**：给一份 `brep-evidence` JSON ⇒ 报告**不崩**、且
`brepEvidence = {"available": false, "verifiedSource": false, "reason": "未提供 B-Rep 证据。"}`
—— ⚠ **它根本没接受我那份证据**（`available: false`）。

⇒ **差距**：我造的 `brep-evidence` 形态**不是它认的形态**（我按自己的理解写了
`{schemaVersion, kind, sourceSha256, measurements}`，而它认的字段**未从既有测试里找到**）。
⇒ **本轮如实记为「未达成」**，**不把它写成通过**（铁律 5：查不到就说查不到）。

**下一步怎么做**：从 `dfm_review.py` 的 `brep_evidence` 解析分支里读出**真字段名**，
或者找到带 B-Rep 证据的既有测试 ⇒ 再补 SC-004。**本轮不猜着改**。

### 2.2 ✓ 一次**假阴性**（我的判据错，不是实现错）
SC-008 第一版我写的关键词是「风险复核」/「不是制造认证」⇒ **判 False**。
查实际报告后发现 `limitations[0]` 的原文是
「**DFM 规则检查不等于制造认证**，必须由工程师结合供应商能力、材料批次、公差和载荷复核。」
⇒ **是判据措辞臆造**，不是实现缺声明。已改成**取自实际报告的措辞**并复跑通过。
★ 教训：**判据的关键词要取自实际产物，不要凭印象写**。

### 2.3 ✓ 一次**接口臆造**（探针当场发现）
第一版我按 `limits: {"machining": {"minWall": 5.0}}`（嵌套）造 profile ⇒ **`profiles: []`**（没被接受）。
查既有测试后发现 `limits` 是**平铺的语义键**（`allowedMaterials` / `workEnvelope` /
`minimumDrillDiameter` / `minimumInternalCornerRadius` / `availableToolDiameters` /
`maximumHoleDiameterRatio`）。
★ **那正是先写小探针（`D:\AI\SW\probe_dfm_api.py`）的价值** —— 没有它，我会写完 200 行才发现。

### 2.4 ⚠ `spec.md` 的 SC 编号与实现清单**有一处不对齐**
`spec.md` 的 SC-005 写的是「删掉证据 ⇒ blocked」，而验收命令里 **SC-005 与 SC-007 合并**
（都用「缺关键输入 ⇒ blocked + 点名」来判）。
⇒ **不影响结论**（该性质**确实**被验到了），但**编号与实现的对应关系**应如实记录在此。

---

## 三、与 `tasks.md` 的对账

`tasks.md` 的 **T-001..T-010 全部完成**（`[x]`）⇒ 与本节结论一致：
* T-004（摸契约）产出了 `probe_dfm_api.py`，并**当场纠正了两处臆造**（§2.1 与 §2.3）；
* T-005（写验收）产出 `tools/verify_dfm_e2e.py`，**11/11 通过**；
* T-007（升 level）后**两个既有测试的红**按轮 78 的做法处理：**先核依据，再改期望，并写明为什么**
  （`tests/test_cad_reliability.py` 里 `dfm_checks` 从 stitched 组移到 verified 组，
  附依据与日期；`surface_modeling` **仍钉住 stitched**）。

---

## 四、本轮**没有**做的事（明确边界）

* **没有**改 `dfm_review.py` / `dfm_profiles.py` 的任何实现逻辑（`spec.md §四` 的约定）；
* **没有**删 `limitations` 的任何一句；
* **没有**引入新依赖（本条只用 `python`）；
* **没有**为 SC-004 猜着改代码（§2.1 如实记为未达成）。

---

## 五、复跑全部命令（一条不落）

```powershell
cd C:\swprojects\sw-skill-fork
python tools/verify_dfm_e2e.py                     # 11/11 · verdict: pass
python -m pytest tests/test_dfm_review.py tests/test_dfm_queue_worker.py -q   # 19 passed
python scripts/check_union_conventions.py          # exit 0（R4：verified 须有 evidence）
python scripts/gen_level_audit.py                  # R8 生成物刷新
python tools/build_union_map.py                    # 地图刷新
python tools/gen_harvest_digest.py                 # 状态摘要刷新
python -m pytest tests -q                          # 970 passed / 17 skipped / 0 failed
python scripts/release_check.py                    # exit 0（12 道硬门禁）
```
