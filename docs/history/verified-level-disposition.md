# `verified` 等级与证据不一致时的处置口径（**主线决定**）

> **背景**：支线（Bunny 批量）产出了 `docs/recon/verified-evidence-audit-2.md` ——
> 它**穷举**核对了 `capabilities.yaml` 里 110 条的 `evidence`，报出 **34 条**
> 「`level: verified` **而证据自己写着失败**」。
> ★★ 而它同时明写：**「判定权在主线：本表只报『证据自己写了什么』，不建议改 `level`」** ✓
>
> **本文件就是那个判定**：口径、已处置、待处置、以及不采用的做法（附理由）。

---

## 一 · ★★★ 口径（三条，写在最前面）

```
① ★ **先复读，再据它行动**：★ 那是**另一个 agent 的读数** ⇒
   我（主线）**自己打开它点名的每个 JSON**，只信我看到的 `verdict`/`passed`/`total` ✓
   ★ 实测：我的复核**证实了它的主要结论**（多数是 `partial` / `N of M`）✓
② ★★ **"证据自称未全过" ≠ "level 写错了"** —— ★ 这是**最容易被夸大**的一步：
   ★ FR-009 原文是「**本规格每一项都必须留下真机证据**，否则 `level` **不得**写 `verified`」，
   ★★ 而这些条目**有**真机证据、只是**证据显示部分变体未成**
   ⇒ ★ **一律降级会是另一种不诚实**（谎称测得比实际少，且会把已验证的部分也抹掉）✓
③ ★★★ **判据落在"是否披露"**：
   · ★ `limitations` **已披露**那次部分失败 ⇒ ★ `verified` **成立**，**一个字都不动**；
   · ★★ **没披露** ⇒ ★ **补一条 `limitations`**，引用该证据的**逐字值**
     （`verdict` / `passed`/`total` / 采集时间）—— ★ 读者要的正是"这条能力到底验到哪一步" ✓
   · ★★★ 只有当证据显示**能力本身没达成目的**（不是"某些变体没成"）时，才谈**降级** ✓
```

★ **为什么③是正解而不是"改 level"**：`level` 表达的是「**我们有没有自己的运行证据**」，
★ 而"验到哪一步"是**另一个维度** ⇒ ★★ 把它塞进 `level` 会丢掉信息（★ 五级枚举表达不了"1/3"）✓

---

## 二 · ★★ 已处置（12 条 · 2026-10-04 接手轮）

★ 判据：证据的 `verdict` 是 `partial*`/`fail`，**或** `passed < total`；
★ 且该条 `limitations` 里**没有任何地方提到这个比值**（多形态检查：比值 / 未成 / 失败 / 部分 / 只过 …）✓
★ 处置：**在 `limitations` 首位插一条**，逐字写 `verdict=… · passed=N/M`（采集时间）+ 出处文件名 ✓

| 条目 | 证据 | 自己写的读数 |
|---|---|---|
| `feature_cosmetic_thread` | `output/cosmetic-thread-evidence.json` | `verdict=cosmetic_thread_works` · **1/3** |
| `sketch_spline` | `output/spline-with-variant-evidence.json` | `verdict=spline_variant_works` · **1/4** |
| `sketch_line2` | `output/createline2-and-createspline-evidence.json` | `verdict=partial_1` · **1/3** |
| `sketch_rotate_or_copy_3d` | `output/rotate-or-copy-3d-evidence.json` | `verdict=rotate_or_copy_works` · **1/2** |
| `sketch_dimension_horizontal` | `output/hv-dimension-with-selection-evidence.json` | `verdict=hv_dimension_works` · **2/3** |
| `sketch_dimension_vertical` | （同上） | `verdict=hv_dimension_works` · **2/3** |
| `surface_flatten` | `output/flatten-with-anchor-evidence.json` | `verdict=flatten_with_marks_works` · **2/4** |
| `surface_planar_region` | `output/planar-replace-variants-evidence.json` | `passed` · **2/3**（无 verdict） |
| `replace_face` | （同上） | `passed` · **2/3**（无 verdict） |
| `surface_ref_ops` | `output/b6b-surface-ref-evidence.json` | `passed` · **1/2**（无 verdict） |
| `loft_and_sweep` | `output/sweep-evidence.json` | `verdict=partial` · 2/未记 |
| `parameter_updates` | `output/a4-runtime-evidence.json` | `verdict=partial` · 未记/未记 |

★★ **同批发现的一个**证据侧**缺口**（已写进每一条的披露行）：
```
★ 这些 JSON 的 `cases` 只记 `{"ok": true|false}`、**没记是哪个变体失败** ⇒
  ★ 读者无法从证据里知道"哪一步没成" ⇒ ★ 要追问就得回到产它的探针**重跑** ✓
⇒ ★ **可复用定则**：★ 判据式证据的每一项都要带**可辨认的身份**（名字/参数），
  否则"1/3"只是一个**不可追问的数字** ✓
```

## 三 · ★ 待处置（其余 22 条）

★ 口径已定（§一③）⇒ ★ 逐条按同一判据走即可；★ 我**没有**一次性扫完，理由：**③ 需要读 `limitations` 的语义**，
★ 而**关键字判据判不准** —— 实测：第一版用"含 `1/3` 或 失败/部分 之类词"当判据，
★★ **把已经披露过的条目误判成"没披露"**（例如 `sketch_spline3_2d` 的 `limitations` 里逐字写着
「**曲面上的样条（on-surface）本轮未成**」）⇒ ★★ **那正是审计自己 §二·一 警告的"必须看清，否则会夸大"** ✓
⇒ ★ 故剩余条目按**人工逐条**处置，不自动化（★ 与事实 53 同族：**启发式连续修补就该停下**）✓
⚠ ★ **另有两处判据的假阳性被我当场清掉**（★ 留档以示口径）：
`curve_through_xyz`（`xyz_curve_2_of_2` ⇒ **2/2 全过**）与 `select_by_ray`（`ray_select_1_of_1` ⇒ **1/1**）
★ 它们名字里有 `_of_`，★ **而 `N == M`** ⇒ ★ 判据必须是 **`N < M`**，不是"名字里带 `_of_`" ✓

---

## 四 · ★★ 顺带定掉支线留下的那条"待主线决断"（指针判据）

★ 支线 `docs/recon/README.md` 里报：指针标记**不一定出现在 `## Returns` 段** ——
  实测 `ISetBodies` 的 `ref Body2 BodyArray` 标记在 **`## Parameters`** 段上，
  按"只看 `## Returns`"的判据**判不出来**（报 45，全文含标记的是 46）✓

★★★ **主线决定：放宽成「全文任何段落出现该标记」**（★ 数字 **45 → 46**）。理由：
```
★ 那条判据的**目的**是「这个成员在 pywin32 这条后端上**到不到得了**」——
  ★★ 而标记出现在哪一段**与可达性无关**（事实 47：那一族是**进程内非托管 C++ 指针**，
  在 `## Returns` 还是 `## Parameters` 都到不了）⇒ ★ 按**目的**放宽，不按字面 ✓
★ 代价：已发布的 `iview-read-members.md` 等表里的指针数要 +1 —— ★ 那属于支线产物，
  ★ **不由我改动**（支线目录"只读结论表"）；★ 本条决定记在这里，供它们下次重跑时采用 ✓
```

---

## 五 · ★ 依据与出处
★ 支线产物（**不是我的**，我只读）：`docs/recon/verified-evidence-audit-2.md`（34 条穷举 ·
60+50 路 Bunny · 两道闸）· `docs/recon/README.md`（判据与已知洞）✓
★ 我的复核脚本：`output/_recheck_audit34.py`（自己开每个 JSON 读顶层）·
`output/_recheck_batch2.py`（逐条看 `limitations` 有没有披露）·
`output/_disclose_partial.py`（幂等回填，含"改判据 ⇒ 先撤回上一版标记行"）✓
★ 规则原文：`specs/202-user-coverage-gaps/spec.md` 的 **FR-009**（★ 逐字引在 §一②）✓
