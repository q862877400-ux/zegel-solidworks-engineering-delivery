# Tasks: B-Rep 证据绑定闭环

**Input**: [spec.md](spec.md) · [plan.md](plan.md)

**格式**：`[ID] [P?] [Story] 描述` —— 每个任务带 `→ 验收:`

**状态**：**全部完成**（轮 80）。

---

## Phase 0: 读契约（**不猜**）

- [x] **T-101** 定位 `brep_evidence` 的处理分支
  **✅** `Select-String scripts/dfm_review.py -Pattern 'brep_evidence|brepEvidence'` ⇒
  `_load_brep_evidence`（L284）/ `_brep_size`（L260）/ `_bounds`（L218）/ `build_dfm_report`（L858）。
  `→ 验收:` `Select-String scripts\dfm_review.py -Pattern '_load_brep_evidence'`

- [x] **T-102** 逐条读 `_load_brep_evidence` 的**每一条 `raise`**（那些 `raise` 就是契约）
  **✅** 8 条 `raise` ⇒ 落成 `spec.md §一` 的契约表：
  ```
  backend ∈ {solidworks_brep, headless_occt} · producedThisRun 必须 True ·
  sourceArtifact 必须存在且后缀匹配 · **sourceSha256 == 该文件的真实 sha256** ·
  路径不得逃出 allowed_root · 三轴包络必须有效 · OCCT 必须 topology.solids >= 1
  ```
  `→ 验收:` `Select-String scripts\dfm_review.py -Pattern 'raise ValueError\("B-Rep'`

- [x] **T-103** 读 `_brep_size` 拿到**包络字段名**
  **✅** 优先级：`envelope_mm{length,width,height}` → `bounds.size` → `bounds.{min,max}`。
  `→ 验收:` `Select-String scripts\dfm_review.py -Pattern 'envelope_mm'`

---

## Phase 1: 探针验证（**先探再改**）

- [x] **T-104** [P] 写探针 `probe_brep_evidence.py` 做四组对照
  **✅** ① 不给证据 ② 给"我认为对"的 ③ 篡改哈希 ④ 篡改产物。
  **实测结论**：**③④ 本来就成立**（实现是对的）· **② 失败**（我的形态错）。
  `→ 验收:` `python tools/probe_brep_evidence_contract.py`

- [x] **T-105** 顺 `ValueError: B-Rep 证据缺少有效的三轴包络` 追到真字段名
  **✅** 用 `envelope_mm{length,width,height}` 后 ⇒ **② 通过**
  （`available=True verifiedSource=True backend='headless_occt'`）。
  `→ 验收:` 同上探针的第 ② 组

---

## Phase 2: 改验收命令（**把弱判据换成强判据**）

- [x] **T-106** 把 SC-004 从「给证据时不崩」（**弱判据**）换成三条**强判据**
  **✅** SC-004a 合法被接受 · SC-004b **篡改 `sourceSha256` ⇒ 被拒** ·
  SC-004c **篡改产物内容 ⇒ 被拒**。**删掉弱判据，不留它凑数**。
  `→ 验收:` `python tools/verify_dfm_e2e.py`（13/13 · `verdict: pass`）

- [x] **T-107** 把契约写进代码注释（SC-105：**让下一个人不必再猜**）
  **✅** SC-004 段上方注明"真形态是读实现得到的（L284-365 + L260-281），不是猜的"，
  并列出五个必填项。
  `→ 验收:` `Select-String tools\verify_dfm_e2e.py -Pattern 'envelope_mm'`

- [x] **T-108** [P] 证据刷新
  **✅** `D:\AI\SW\output\dfm-evidence.json` 现含 13 条 `checks`。
  `→ 验收:` `Test-Path D:\AI\SW\output\dfm-evidence.json`

---

## Phase 3: 收工

- [x] **T-109** [P] 十二道硬门禁 + 生成物刷新
  `→ 验收:` `python scripts/release_check.py`（exit 0）

- [x] **T-110** 全量回归（**不得退化**）
  `→ 验收:` `python -m pytest tests -q`（970 passed / 17 skipped / 0 failed）

- [x] **T-111** 两仓库各自 commit
  `→ 验收:` `git -C . log --oneline -1` + `git -C D:\AI\SW log --oneline -1`

---

## 依赖关系

```
T-101 → T-102 → T-103 → T-104 → T-105 → T-106 → T-109 → T-110 → T-111
                                  └──→ T-107 · T-108 ┘
```
