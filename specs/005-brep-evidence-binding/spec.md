# Feature Specification: B-Rep 证据绑定闭环（还清 004 的不符合项）

**Feature Branch**: `005-brep-evidence-binding`

**Created**: 2026-10-01 · **Status**: Implemented

**Input**: `specs/004-dfm-verified/converge.md §2.1` 记的**不符合项** ——
SC-004「**篡改证据必被拒**」当时**未达成**（我给的证据被当成 `available: false`）。
本特性把它**还清**，并把 `_load_brep_evidence` 的真实契约**写成可复跑的判据**。

---

## 背景：004 的欠账为什么值得单独成篇

004 的 converge 记下的是**真欠账**（不是笔误）：我当时**按自己的理解**造了一份 B-Rep 证据
（`{schemaVersion, kind, sourceSha256, measurements}`），报告却说「**未提供 B-Rep 证据**」。
⇒ 那意味着**我根本不知道这个机制的契约**，却写了一条"未达成"就收工。

本特性做的是**把契约读出来**（`dfm_review._load_brep_evidence` L284-365 +
`_brep_size` L260-281），并据此**补三条判据**：
* **合法证据必须被接受**（`verifiedSource is True`）；
* **篡改 `sourceSha256` ⇒ 被拒**；
* **篡改产物内容 ⇒ 被拒**。

---

## 一、真实契约（**逐条读实现得到，未臆造**）

```
backend           ∈ {"solidworks_brep", "headless_occt"}      ← 其它 ⇒ "后端未经认可"
  solidworks_brep ⇒ payload.measurements{units:"mm",
                      measurement_source 含 "solidworks api" 且含 "b-rep"}
                    sourceArtifact 后缀 == ".sldprt"
  headless_occt   ⇒ payload.geometryEvidence{units:"mm", topology.solids >= 1}
                    sourceArtifact 后缀 ∈ {".brep",".step",".stp"}
producedThisRun   必须 **True**（否则"不能用于本轮制造判断"）
sourceArtifact    必须存在；**相对路径不得逃出 allowed_root**
sourceSha256      **必须 == `_sha256_file(sourceArtifact)`**   ← ★ 本特性的核心
envelope          三轴包络取自 **`geometryEvidence.envelope_mm{length,width,height}`**
                  或 `bounds.size` / `bounds.{min,max}`
⇒ 任一不满足 ⇒ **`status="blocked"` + `error_code="dfm_invalid_brep_evidence"`**
  + `checks` 里 `dfm_brep_evidence` 为 `fail`（severity=critical）并带**具体原因**
```

---

## 二、验收判据（**每条可 grep / 可复跑**）

| ID | 判据 | 怎么验 |
|---|---|---|
| **SC-101** | 合法 OCCT 证据被接受：`brepEvidence.available is True` 且 `verifiedSource is True` 且 `backend == "headless_occt"` | `python tools/verify_dfm_e2e.py`（SC-004a）|
| **SC-102** | **篡改 `sourceSha256` ⇒ `error_code == "dfm_invalid_brep_evidence"`**，且 `checks.dfm_brep_evidence.message` 含「SHA-256 不匹配」 | 同上（SC-004b）|
| **SC-103** | **篡改产物文件内容 ⇒ 同样被拒**（改了文件，真实哈希就变）| 同上（SC-004c）|
| **SC-104** | 004 的其余 10 条判据**不退化**（总数 13/13）| 同上（`verdict: pass`）|
| **SC-105** | 契约**写进代码注释**（`verify_dfm_e2e.py` 的 SC-004 段），使下一个人**不必再猜** | `Select-String tools/verify_dfm_e2e.py -Pattern 'envelope_mm'` |

---

## 三、明确**不做**的

* **不改** `dfm_review.py` 的实现（契约本身没问题，**缺的是我的判据**）；
* **不删** 004 的任何制品（欠账**如实留在 converge 里**，本特性只是**加一条"已还清"的指向**）；
* **不引入**新依赖。

---

## 四、结果

见 [converge.md](converge.md)。
