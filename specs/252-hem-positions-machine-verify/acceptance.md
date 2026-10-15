# Acceptance — `HEM_POSITIONS` 的真机类型库复核

**Feature**: `specs/252-hem-positions-machine-verify/`
**日期**: 2026-10-09
**结论**: ✅ **四件齐 · 判据 4/4 绿 · 红基线成立 · 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★ 业务结论**: **真机类型库 == 代码** ⇒ `HEM_POSITIONS` **正确**；★ **官方 md 的 1/2 是错的**（★ 铁律 4 的**首次真机实证**）。

---

## 一、逐条验收（对应 `spec.md` 的 FR）

| # | 需求 | 判据 | 读数 |
|---|---|---|---|
| FR-001 | 直读本机类型库核代码表 | `test_hem_positions_match_machine_type_library` | ✅ **真机 0/1 == 代码 0/1** |
| FR-002 | ★ 永久负例：md 的 1/2 必须**不通过** | `test_official_md_values_are_rejected_by_machine_type_library` | ✅ md 值 **≠** 真机值 |
| FR-003 | ★★ 读取器不许太窄 | `test_type_library_reader_is_not_too_narrow` | ✅ 读到 **2** 个**整数**常量（★ 不是 3 —— 枚举类型本身已过滤） |
| FR-004 | ★★ 判据必须能红 | `test_pure_function_is_red_able` | ✅ 变异 ⇒ **2 条**；空库 ⇒ 「读取器太窄」 |
| FR-005 | 缺数据源 ≠ 检查失败 | 三个真机判据的 `skip` 分支 | ✅ 本机有类型库 ⇒ 实测 **4 passed**（★ 不是 4 skipped） |
| FR-006 | ★ 只读 | 护栏预检 + 代码 grep | ✅ 「读到文档 **0** 个」· `SaveAs\|Insert[A-Z]\|Create[A-Z]` 命中 **0** |

---

## 二、★★ 红基线（★ 本仓纪律：不能红的判据 = 空判据）

| 变异 | 期望 | 实测 |
|---|---|---|
| 代码表改成 **md 的值**（`inside=1` / `outside=2`） | 报 2 条不一致 | ✅ **`['★ swHemPositionTypeInside：代码 1 · 真机类型库 0 ⇒ 不一致', '★ swHemPositionTypeOutside：代码 2 · 真机类型库 1 ⇒ 不一致']`** |
| 类型库读数置空 `{}` | 报「读取器太窄」 | ✅ **`['类型库里只读到 0 个 swHemPositionType* ⇒ 读取器太窄']`** |
| 正常表 | 0 条 | ✅ **`0`** |

★ 命令（★ 可复制）：
```bash
cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B -c "
import sys, importlib.util
sys.path[:0]=['D:/AI/SW','D:/AI/SW/scripts','D:/AI/SW/tests']
s=importlib.util.spec_from_file_location('t','D:/AI/SW/tests/test_hem_positions_machine_verified.py')
m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
tlb=m._tlb_enum(); print('真机:', tlb)
print('正常:', len(m._failures(m.HEM_POSITIONS, tlb)))
print('变异:', m._failures({'inside':1,'outside':2}, tlb))
print('空库:', m._failures(m.HEM_POSITIONS, {}))
"
```

---

## 三、★★★ 真机证据

**探针**：`output/_probe252_hem_tlb.py` · **走护栏** `tools/sw_guard.py --timeout 240 -- python <探针>`

★ 护栏预检：`启动之前（窗口标题路）⇒ 放行 · 读到文档 0 个 · 非我方 0 个 · 未保存 0 个`
· `连上之后（COM 路）⇒ 放行 · 读到文档 0 个`。

| 源 | `swHemPositionTypeInside` | `swHemPositionTypeOutside` |
|---|---|---|
| 代码 `HEM_POSITIONS` | **0** | **1** |
| 官方 **md**（`C:/swapi/enums/swHemPositionTypes_e.md`） | 1 | 2 |
| ★★ **真机类型库**（`D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\swconst.tlb`） | **0** | **1** |

★ 落盘：`output/hem-positions-tlb-evidence.json`。

---

## 四、★ 未改动证明（★ 用 mtime）

| 文件 | 本轮是否改 |
|---|---|
| `scripts/sw_sheet_metal.py` | ❌ **未改**（★ 真机证明它**已经是对的**） |
| `tests/test_pattern_enum_alignment.py` | ❌ **未改**（★ 它核**反射侧**，与本文件互补） |
| `tools/build_obsolete_index.py` | ❌ 未改（★ 251 改的） |
| `specs/202-.../recon/official-obsolete-index.json` | ❌ 未改（★ 251 重生成的） |

★ **本轮改过**：`tests/test_hem_positions_machine_verified.py`（新）· `output/hem-positions-tlb-evidence.json`（新）·
`output/_probe252_hem_tlb.py`（新）· `output/GOAL.md`（新）· `specs/252-*/`（新）· `docs/ROADMAP.md` ·
`.workbuddy-ai/memory/2026-10-09.md` · `output/AUTO_HANDOFF.md` · `output/AUTO_RUN_2026-10-09-2319.md` · `.specify/feature.json`。
⇒ ★ **`scripts/` 与 `tools/` 一个文件都没动**（★ 251 除外，那是上一轮）。

---

## 五、门禁全套 @3.14.7

| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| `gate_details` 条数 | **47**（★ 未新增门禁） |

★ **生成器链未跑**（★ 没改 `scripts/`）。

---

## 六、★★★ 核心发现

### 发现一：**「反射转储」不等于「真机」**

★ 原判据（`test_pattern_enum_alignment.py`）核的是**离线反射文件** —— ★ 那只是**两个转储之间的比对**。
★ 本轮**第一次直读本机类型库**，把这条线**真正落地**。

### 发现二：真机类型库证明 **md 错、代码对**

★ 官方 md 写 1/2，真机 `swconst.tlb` 写 0/1 ⇒ ★ **铁律 4（冲突以出厂类型库为准）首次有了真机证据**。

### 发现三：三个环境坑（★ 见 ③ 第 69~73 条）

① 枚举在 **`swconst.tlb`**（常量库）不在 `sldworks.tlb`（接口库）· ② 类型库在 **D 盘**
· ③ **枚举类型本身也匹配前缀** ⇒ 必须 `isinstance(val, int)` 过滤。

---

## 七、未过门（如实登记）

1. **`create_hem` 的行为证据仍拿不到** —— ★ 五种形态全回 `None`（事实 34/53）；
   ★ 本轮是**类型库证据**，★ **不是**「调通 `create_hem`」。
2. **16 条 arity 定罪** —— ★ 下一个切片（`specs/253-*`）。
3. **换路由 7 类** —— ★ 需逐条真机验。
4. **高危写盘**（`SaveAs3` · `create_draft` · `create_profile_center_mate`）。
5. **223 的 8 条 `HEAD` 即红既有失败未修**；**未提交 / 未部署**。
6. **未删任何文件**；★ 未 create 或 update 除「SW 施工 · 跨会话持续（每小时）」以外的任何自动任务。
