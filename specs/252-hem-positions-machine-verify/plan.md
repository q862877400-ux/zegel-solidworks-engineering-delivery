# Plan — `HEM_POSITIONS` 的真机类型库复核

**Feature**: `specs/252-hem-positions-machine-verify/`
**日期**: 2026-10-09

---

## 一、三源与冲突裁决顺序

| 序 | 源 | 路径 | 用途 | 权威度 |
|---|---|---|---|---|
| 1 | ★★ **真机类型库** | `D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\swconst.tlb` | 读 `swHemPositionType*` 常量 | ★★★ **最高**（★ 本轮新增这一层） |
| 2 | **出厂反射转储** | `_raw/**`（离线文件） | 原判据用的源 | ★★ 派生自 1（★ 但**从未核过**） |
| 3 | **官方 md** | `C:/swapi/enums/swHemPositionTypes_e.md` | 另一侧（★ 实测**错**） | ★ |

**冲突裁决顺序**：1 > 2 > 3。★ 铁律 4 的原文就是「以出厂类型库为准」—— ★ 本轮**首次把它落到实处**。

---

## 二、口径

| 口径 | 真源 | 怎么用 |
|---|---|---|
| 代码表 | `scripts/sw_sheet_metal.HEM_POSITIONS` | ★ **import**，不重写 |
| 真机常量 | `comtypes.client.GetModule(swconst.tlb)` → `comtypes.gen.<模块>` | ★ 只收 **`isinstance(val, int)`** 的 `swHemPositionType*` |
| 负例（md） | `C:/swapi/enums/swHemPositionTypes_e.md` | ★ 硬编码 1/2 + 断言它**不等于**真机值 |

★★ **教训（本轮踩的）**：`swHemPositionTypes_e`（枚举**类型本身**）也匹配前缀 ⇒ ★ 必须过滤非 `int`。

---

## 三、实现步骤

1. **先量**：`output/_probe252_hem_tlb.py`（走护栏）⇒ 找 tlb → 加载 → 搜常量 → 三源对照。
2. **先写能红的判据**：`tests/test_hem_positions_machine_verified.py`
   ⇒ 纯函数 `_failures` + 三组负例（变异 / 空库 / 正常）。
3. **证明它红**：代码表改成 md 值 ⇒ **2 条**不一致；类型库为空 ⇒ 「读取器太窄」。
4. **写证据**：`output/hem-positions-tlb-evidence.json`。
5. **回写四处**：ROADMAP §一 · memory · `output/AUTO_HANDOFF.md` · `output/AUTO_RUN_*.md`。

---

## 四、改动面

| 文件 | 动作 |
|---|---|
| `tests/test_hem_positions_machine_verified.py` | ★ **新增**（4 例） |
| `output/hem-positions-tlb-evidence.json` | ★ **新增**（真机证据） |
| `specs/252-hem-positions-machine-verify/*.md` | ★ **新增**（四件齐） |
| `docs/ROADMAP.md` · memory · `AUTO_HANDOFF.md` · `.specify/feature.json` | 回写 |

★ **不改**：`scripts/sw_sheet_metal.py`（★ 真机证明它**已经是对的**）· `tests/test_pattern_enum_alignment.py`（★ 它核的是反射侧，与本文件互补）· `tools/build_obsolete_index.py` · 索引 · `mcp-server/**`。
★ **不跑生成器链**（★ 没改 `scripts/`）。

---

## 五、风险与对策

| 风险 | 对策 |
|---|---|
| 真机命令被模态框冻死 | ★★ **一律走 `sw_guard`**；★ 先 `--scan` 确认 0 个残留弹窗 |
| 3.13.12 缺 COM ⇒ 交互式提问挂死 | ★★ 真机**只用 3.14.7** |
| 误碰用户文档 | ★ 护栏预检「读到文档 0 个」才放行；★ 本探针**不调用任何建模 API** |
| 本机没装 SW ⇒ 判据红 | ★ `pytest.skip`（★ 缺数据源 ≠ 检查失败） |
| 读取器太窄 ⇒ 假绿 | ★ 下界：必须读到 ≥2 个整数常量；★ 且要核的成员必须在读数里 |
| `release_check` 约 2m40s | ★ 后台跑 + 落盘日志 |
