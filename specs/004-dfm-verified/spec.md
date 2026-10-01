# Feature Specification: DFM 复核升 `verified`（真机可跑的证据链）

**Feature Branch**: `004-dfm-verified`

**Created**: 2026-10-01

**Status**: Implemented（本机可跑，无外部依赖）

**Input**: 用户诉求「让 AI 会自己设计制作…一切 SolidWorks 功能」中的 **DFM 可制造性复核**一项；
本条服务 `AGENTS.md §一 A4`（`verified` 必须有**我们自己的运行证据**）与 §五 第 5 步（门禁与实测）。

---

## 背景：这条特性为什么必须单独成篇

`capabilities.yaml` 的 `dfm_checks` 长期停在 **`stitched`**（代码已并入、**缺我们自己的运行证据**）。
它此前被笼统归入「需 B-Rep 证据」而**搁置** —— 但 **轮 79 的前提核查推翻了那个归类**：

```
dependencies: ["python"]          ← **只依赖 python**
实现: scripts/dfm_review.py + scripts/dfm_profiles.py
测试: tests/test_dfm_review.py + tests/test_dfm_queue_worker.py ⇒ **19 passed**
```

★ **关键区分**：`limitations ①` 里的「**SolidWorks/OCCT B-Rep 证据绑定**」指的是
**它的输入是"外部给的 B-Rep 证据"**，**不是"它自己要去跑 OCP"**。
⇒ 本机虽缺 `OCP` / `trimesh`，但**本条不需要它们** ⇒ **本机可跑** ⇒ 该特性成立。

⚠ 这正是**轮 77 教训的正面应用**：**升 level 前先核「证据依赖的东西在不在本机」** ——
上轮那条 `verified` 的证据指向了**本机根本不存在的 OCP**；本条则相反，**核查后发现它不依赖那些**。

---

## 一、必做的三件事（`dfm_checks` 的 limitations 逐条）

`limitations` 是三句**承诺** ⇒ 本特性的验收**必须逐条覆盖**（不是"跑通就算"）：

| # | limitations 原文（节选） | 本特性的对应判据 |
|---|---|---|
| L1 | 「支持供应商 DFM Profile **能力交集**、**单位归一**和 SolidWorks/OCCT **B-Rep 证据绑定**；**缺失或伪造关键证据会返回 `blocked`**」 | SC-003 / SC-004 / SC-005 |
| L2 | 「机器规则全部通过**仍必须人工确认**材料、公差、载荷、装配、刀具/模具、打印方向和供应商能力」 | SC-006 |
| L3 | 「DFM 报告是**风险复核，不是制造认证**；缺少材料、壁厚、K 因子、割缝或成型空间等关键输入时返回 `blocked`」 | SC-007 |

---

## 二、用户场景（三个）

### US-1 · 供应商能力交集（P1）
**作为**使用者，我给出多个供应商 profile，**希望**报告只保留**它们共同支持**的工艺能力，
**以便**不会按某一家能做、另一家做不了的规则误判。

### US-2 · 缺关键输入必须 `blocked`，不许"猜着过"（P1）
**作为**使用者，我给出缺材料 / 缺壁厚 / 缺 K 因子的文档，**希望**报告返回 `blocked`
并**点名缺什么**，**以便**不会拿着一个基于默认值的结论去开模。

### US-3 · 伪造证据必须被拒（P1）
**作为**使用者，我给出**哈希对不上**的 B-Rep 证据，**希望**报告返回 `blocked`，
**以便**「伪造关键证据」这条路**根本不成立**（这是 L1 末句的实质）。

---

## 三、验收判据（**每条都可 grep / 可复跑**）

| ID | 判据 | 怎么验（可复跑的枚举命令） |
|---|---|---|
| **SC-001** | 四种工艺都被支持且别名归一 | `python tools/verify_dfm_e2e.py` 输出含 `machining` / `sheet_metal` / `laser_cutting` / `3d_printing` 四行 ✓ |
| **SC-002** | **单位归一**：`inch` 输入与 `mm` 输入得到**同一**几何结论 | 验收脚本对同一零件分别以 `mm` / `inch` 建文档，断言两条报告的**规则判定一致** |
| **SC-003** | **Profile 能力交集**生效：两个 profile 的交集**窄于**任一单profile | 验收脚本建 3 份 profile（宽 / 宽 / 窄），断言交集 = 窄者 |
| **SC-004** | **B-Rep 证据绑定**：证据的 sha256 与文档一致时才 `pass` | 验收脚本造一致证据 ⇒ 非 blocked；篡改一个字节 ⇒ `blocked` |
| **SC-005** | **缺失关键证据 ⇒ `blocked`**（不是"默认通过"） | 验收脚本删掉证据 ⇒ `status == "blocked"` 且 `error_code` 点名缺失项 |
| **SC-006** | **人工确认项**必须出现在报告里（`manual` / 人工） | 验收脚本断言报告含人工确认清单字段，且**非空** |
| **SC-007** | **缺材料 / 壁厚 / K 因子 ⇒ `blocked`** | 验收脚本逐项删一个关键输入，各断言 `blocked` |
| **SC-008** | 报告自称**风险复核、非认证** | 验收脚本断言报告里那句免责声明存在 |
| **SC-009** | `capabilities.yaml` 的 `dfm_checks.level == "verified"` 且 `evidence` 非空 | `python scripts/check_union_conventions.py`（R4：`verified` 必须有 `evidence`）|
| **SC-010** | **既有 19 个测试全绿** | `python -m pytest tests/test_dfm_review.py tests/test_dfm_queue_worker.py -q` |

---

## 四、明确**不做**的（守住边界）

* **不做**任何"制造认证"的表述（L3 明确：**风险复核**）；
* **不引入** `OCP` / `trimesh` 等新依赖 —— 本条**只用 `python`**（`dependencies` 原文如此）；
* **不改** `dfm_review.py` / `dfm_profiles.py` 的实现逻辑：本特性**只补运行证据**
  （若验收发现缺陷，**另开特性**修，不混在"补证据"里）；
* **不删** `limitations` 的任何一句。

---

## 五、依赖与前提（**先核，再动手**）

| 项 | 本机状态 | 结论 |
|---|---|---|
| `python` | ✅ `3.14.7` | 满足 |
| `numpy` | ✅ | 满足 |
| `ezdxf` | ✅ | 满足 |
| `OCP` / `trimesh` | ❌ 不可用 | **本条不需要**（见「背景」的区分）|
| SolidWorks | ✅ 在跑（PID 20456） | **本条不需要**（纯离线）|

---

## 六、结果

见 [converge.md](converge.md)（逐条对齐实测证据与**不符合项**）。
