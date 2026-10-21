# text-to-cad 借鉴记录（已内化，原件已删除）

**状态**：内化完成。**`text-to-cad` 克隆与相关残留材料已全部删除**，本文件是唯一的追溯凭证。
**日期**：2026-10-19
**删除对象**：`D:\Agent-Studio\Deepseek-Harness\DSH-Oss-Research-and-Deployments\text-to-cad`（规模见 §六 表，实测命令：`Get-ChildItem <path> -Recurse -File -Force | Measure-Object Length -Sum`）及其同目录的两份对比报告。

> ⚠ **本文件不保留上游行号引用的可复核性**：原件已删，文中的「上游 `文件:行号`」**无法再回读核对**。保留它们只为说明「当时依据的是哪一段」，不构成可复查的证据链。若将来需要重新核验，须重新克隆 `earthtojake/text-to-cad` v0.7.22。

---

## 一、被借鉴的是什么

上游：`earthtojake/text-to-cad` v0.7.22（`VERSION` 文件内容），MIT。
它把 CAD 模型写成 Python（`@step` 装饰器返回 build123d Shape），并自带一整套「agent 写 CAD」的技能与门禁。

我们**没有**引入它的代码。借鉴的是**五条设计思路**。

## 二、五条经验的裁决与落点

完整裁决见 [`docs/text-to-cad-lessons-verdict.md`](text-to-cad-lessons-verdict.md)（含每条的上游原文证据、本仓现状核实、裁决理由）。此处只列结论与落点。

| # | 经验 | 裁决 | 落点 |
|---|---|---|---|
| ① | 事实/尺寸**来源分级** | **改造后采纳** | `scripts/check_fact_provenance.py` + `tests/test_fact_provenance_gate.py` |
| ② | 几何关系**断言化**（`check_spec()`） | 不采纳（本轮） | 无落点：本仓是能力仓库，不是零件仓库 |
| ③ | **强制视觉复核** + 反循环刹车 | 不采纳 | 本仓已有真机测量 + `tools/sw_guard.py` 护栏，更强 |
| ④ | **置信度进名字**（`__photogrammetric` 等） | 不采纳 | `capabilities.yaml` 的 `level` 五级枚举已结构化，再进名字会双写矛盾 |
| ⑤ | **不追问但记录**（假设台账） | **改造后采纳** | `docs/assumption-ledger.md` + `scripts/check_assumption_ledger.py` |

## 三、两条采纳项的「改造点」（为什么不是照搬）

### ① 来源分级

- **上游做法**：`models/falcon_heavy/PROVENANCE.md` 是**建模任务级**的五栏组件表
  （`Component group | Sources | Type | Confidence | Geometry status`），每个组件一行，
  低置信度行明写 `counts/positions invented`。
- **改造**：本仓是能力仓库，照搬会与 `capabilities.yaml` 的 `level`/`evidence` 语义重叠
  ⇒ **空转门禁**（`docs/known-facts.md` 事实 62）。收窄为「`docs/*.md` 增量行里的
  **量化断言**必须能追溯到出处」，且**只查增量**（沿用 `scripts/check_provenance.py:11-13`
  的 `git diff origin/main` 范式）。

### ⑤ 假设台账

- **上游做法**：`skills/sdf/references/llm-guardrails.md` 给出五档来源枚举
  （user-provided / upstream / target docs / measured / explicit assumption），
  并要求 `Do not hide guessed values`；ledger 是**建模任务内**的注释块。
- **改造**：本仓需要**跨任务**台账 ⇒ 新增 `docs/assumption-ledger.md`，与
  `known-facts.md`（已验证事实）/ `dead-ends.md`（已验证失败）互补，
  判据是「是否已验证」这个二值。
- **核心判据（真正价值）**：`open` 状态的假设**不得**出现在 `capabilities.yaml` 里
  `verified` 条目的 `evidence` 中 —— 把「假设」与「证据」在机器层面隔开。

## 四、三条不采纳的理由（留档，便于将来重开）

| # | 上游确实有 | 为什么不采纳 | 何时应重开 |
|---|---|---|---|
| ② | `models/radial/src/lib/spec.py` 的 `check_spec()`：模块级无条件执行几何断言（齿数闭合、点火间隔、装配条件） | 需要一个「几何常量单一真相源」；本仓没有。硬建会得到一个没人 import 的常量模块（等于没有守卫）或与现有 `tests/` 重复 | `output/` 下出现 ≥3 个 `check_spec()` 同类脚本，或 `known-facts.md` 新增「常量漂移」类事实 |
| ③ | `skills/cad/references/snapshot-review.md`：每次可见改动必须看一张图，`Passing geometry checks does not waive this visual review` | 上游这条面向**无特征树、无法静态验证几何**的建模者；本仓有 SolidWorks 真机测量 + 静态比对 + `sw_guard.py` 弹窗护栏，两条线都比「看图」强。反循环刹车本仓已有等价物（事实 53：连续修补 ≥3 次就停） | 本仓出现「静态检查全绿但肉眼可见错误」的实际事故 |
| ④ | `PROVENANCE.md`：状态嵌进几何对象名字（`__schematic` / `__placeholder` …） | 上游这样做是因为 STEP 是纯几何、无处挂元数据（其 `packages/cadgen/README.md` 第 4 条法律 `Zero metadata in written artifacts`）。本仓 `capabilities.yaml` 是结构化清单，状态有专门字段与门禁；再复制到名字里会产生双写不一致（`check_union_conventions.py` 的 R13 已在查这类矛盾） | 本仓出现「字段对了但对象本身说不清可信度」的实际需要 |

## 五、明确**没有**借鉴的东西

以下上游能力我们看了但**不采纳**，理由是路线差异而非能力差异：

1. **「模型即代码」的 git 可 diff / 可测试优势** —— 来自根本不碰 SolidWorks。本仓走 COM 路线，
   拿不到它，除非走「Python 生成 STEP → 导入 SW」的桥，而那会丢掉特征树。
2. **无约束求解器的纯前向运动学**（`kinematics.py` 的 `Closed loops are out of scope by design`）
   —— 这是它的**能力边界**，不是优点。本仓的 SolidWorks 有真约束求解器。
3. **从几何反推可编辑特征** —— 它明确**不做**（`packages/ui/docs/feature-detection.md`：
   `A recognized feature is a group of existing canonical faces and edges, not a new kind of reference`，
   且 `It never reads model source`）。它做的是 UI 侧面/边分组导航，不是特征树重建。

## 六、被删除的残留清单

| 对象 | 规模 | 说明 |
|---|---|---|
| `text-to-cad/`（整个克隆） | 3,021 文件 / 45.2 MB | 上游 v0.7.22 本地克隆 |
| `text-to-cad-vs-SolidWorks.md` | 10,114 字节 | 旧对比报告；**其中两条是错的**（说没有干涉检查、漏了 `dfam-check`），推翻记录见下 |
| `分析-text-to-cad对比SolidWorks.md` | 10,114 字节 | 与上一份 **SHA-256 完全相同**（同一份报告两个文件名） |
| `SW/.rea-scratch/`（4 份逆向笔记） | 252 KB / 5,461 行 | 四个分支的原始证据底稿（`A-gate` / `B-criteria` / `C-model-as-code` / `D-layers`） |

### 旧报告被推翻的两条（留档）

1. **「没有干涉检查，全仓 `interference` 零命中」是事实错误** —— 实测 **63 个文件**命中，
   含 `models/radial/src/lib/gate.py`（1,634 行运动学+静态干涉门）与
   `models/tendon_hand/validation/` 下 **126 个 `check_*.py`**。
2. **漏掉 `dfam-check` skill** —— 旧报告全文 `dfam` 命中 0 次，而被它引用的
   `skills/dfm/SKILL.md` 自己就写着 `For additive manufacturing, use $dfam-check`。
   更要紧的是旧报告把「不下判定」读成了「不测量」——`dfam-check` 有 399 行真测量脚本。

---

## 七、如果将来要重新核验

```bash
git clone https://github.com/earthtojake/text-to-cad.git
cd text-to-cad && cat VERSION    # 应为本记录所依据的 0.7.22
```

然后按 `docs/text-to-cad-lessons-verdict.md` 里逐条给出的 `路径:行号` 回读。
**注意**：上游若已升级版本，行号会漂移，须按内容而非行号重新定位。
