# Plan — 门禁盲区探测器的漏网（spec 225）

**Feature**: `specs/225-blind-spot-claim-detector/`
**日期**: 2026-10-09
**规模**: 小（1 处正则 + 10 行声明 + 1 份新判据）。**WIP = 1**，一轮做完。

---

## 一、三源与冲突裁决顺序（本仓铁律 0 / 铁律 4）

| # | 源 | 路径 | 本轮用途 |
|---|---|---|---|
| ① | **官方 SDK 文档（swapi 解包）** | `C:\swapi\enums\*.md` · `C:\swapi\types\<Iface>\<Member>.md` | ★ 查了：`C:\swapi\enums\` **没有** `sws*` 页（142 个 `sws*` 页全是 `swS*`/`swSF*`/`swSM*` 等，非 Simulation 程序集）⇒ 本轮的 Simulation 枚举**只能靠 ②③** |
| ② | **CHM 解包** | `_raw/chm_cosworks/` · `_raw/cosworks_pages/` | ★ 交叉核对 Simulation 枚举的成员名与语义 |
| ③ | **出厂反射转储** | `_raw/enum_values_sldworks.txt` · `_raw/reflect/enum_cosworks.txt` | ★★ **本轮判据的值来源**（`enum_value_sets()` 读的就是它） |

**裁决顺序（冲突时）**：③ **出厂反射转储** > ② CHM 解包 > ① swapi 的 md。
依据 **铁律 4**（「冲突/不一致以**出厂类型库**为准」）——
转储是**纯元数据读取**（非实测、非人工转抄），比 md 页更接近真相。
★ 同族先例：`specs/224-.../acceptance.md` 记的 `swSketchChamfer_DistanceDistance`（反射 1 · md −1 ⇒ 取反射）。

**本轮三源核对的实际结果**：三张 `enum` 表的枚举名**逐条在 ③ 里查到**，值集**全部包含**（见 spec §二 FR-003）；
**无冲突** ⇒ 不需要动用裁决顺序。★ 这点必须写清楚：**不是「没查」**，是「查了、三源不冲突」。

---

## 二、改动清单（3 处，全部离线）

| # | 文件 | 改什么 | 为什么 |
|---|---|---|---|
| 1 | `scripts/check_enum_values_vs_reflection.py` | `CLAIM` 正则：`官方\|swapi\|sw[A-Z]\w+` → `官方\|swapi\|sws?[A-Z]\w+\|反射\|转储\|CHM\|_raw` | FR-001 / FR-002 —— 修**探测器自己**的漏网 |
| 2 | `scripts/sw_simulation.py` · `sw_topology.py` · `sw_costing.py` · `sw_featureworks.py` · `sw_pdm.py` · `sw_routing.py` · `sw_selection.py` · `sw_simulation_loads.py` | 各表起始行**正上方**插一行 `#: enum-gate: <code> <arg>`（共 **10 行**，**纯插入、零删除**） | FR-003 |
| 3 | `tests/test_gate_blind_spot_claim.py` | **新建**判据（4 类断言，含端到端负例） | FR-004 / FR-005 |

★ **不改** `#: enum-gate:` 的 code 词表与 `not-enum` 子类（FR-005）⇒ 224 的 54 条声明**零影响**。

---

## 三、施工顺序（★ 判据必须先红）

```
S1  写 tests/test_gate_blind_spot_claim.py（判据）
S2  ★ 跑它 ⇒ **必须至少 4 例红**（否则判据是空的，停下重写）
S3  改 CLAIM 正则（FR-001 / FR-002）
S4  跑判据 ⇒ 「探测器认得出」类转绿；「10 张表已表态」类**仍红**（还没声明）
S5  逐张插 10 行声明（FR-003）
S6  跑判据 ⇒ 全绿
S7  跑门禁本体 ⇒ 未表态 = 0 · exit 0
S8  回归 223 / 224 两份判据 ⇒ 仍绿
S9  scripts/sync_bundled_skill.py（打包副本同步）→ 跑打包新鲜度判据
S10 ★ scripts/release_check.py **用 3.14.7** ⇒ exit 0
S11 更新 ROADMAP §一 / .specify/feature.json / memory / 交接单 / AUTO_RUN
```

**为什么 S2 是硬门**：★ 本轮改的是**正则**，改前改后门禁都能 exit 0
（未覆盖本来就不判罪）⇒ 若不先造一棵「自称 `sws*` 却未表态」的合成树，
**没有任何可红的判据** ⇒ 就是 223 判过的「空判据」形态。
★ 同族纪律：`AGENTS.md` §十四「先写判据并确认它真的能红」。

---

## 四、风险与对策

| 风险 | 对策 |
|---|---|
| 放宽 `CLAIM` 后盲区从 44 涨到 54，**223 的判据** `test_gate_boundary_transparency.py` 按 `min(盲区,20)` 对明细行数 ⇒ 可能假红 | ★ 先读该判据：它算的是 `len(未覆盖：明细行) == min(未表态数, 20)`，而**未表态数改后仍为 0**（10 张全表态）⇒ 明细 0 行 ✓ **不假红**（S8 实测确认） |
| 放宽后 224 的 `BASELINE_BLIND = 44` 断言失败 | ★ 该断言是 `assertGreaterEqual(blind, 44)` ⇒ 54 ≥ 44 ✓ **不假红**（S8 实测确认） |
| `反射` 是**弱**自称词，可能误伤将来新写的表 | ★ 接受：误伤的代价是**插一行声明**（<1 分钟），漏网的代价是**伪造枚举复发**（223 的原病）。★ 在 spec §二 FR-002 写明这是**启发式**、不是证明 |
| 三张 `enum` 声明的枚举名写错 ⇒ 门禁判红 | ★ 名字**逐条从转储节头抄**（`grep -A6 "^## swsSolverType_e$"`），不靠记忆；S6/S7 会立刻抓 |
| 改了 `scripts/*.py` 但忘了同步打包副本 | S9 + 打包新鲜度判据 |
| `release_check` 假红 | ★ 必须用 **3.14.7**（受管 3.13.12 缺 comtypes ⇒ 交互式 COM 提示 ⇒ 假红 + 挂死） |

---

## 五、不做（同 spec §三）

不逐行补 `# swXxx` · 不把「未覆盖」判红 · 不改 code 词表 · 不修 223 的 8 条既有红 ·
不碰 `HEM_POSITIONS`（需授权 COM）· 不提交/部署/打 tag · **不删任何文件**。
