# Tasks — 「两个后继都要」的宿主级先量

**Feature**: `specs/249-multi-successor-both-needed-census/`
**日期**: 2026-10-09
**规则**: ★ 每条带**可复制执行**的验收命令；★ **先写能红的判据**再下结论。

---

## T-001 先量：列出 15 条条目 + 全部站点的读写语义

- **动作**：`output/_probe249_both_successors.py`（★ 口径 **import** `_scan_all_modules` / `_called_names`）。
- **验收**（★ 复制执行）：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B output/_probe249_both_successors.py > output/_probe249_both_successors.txt 2>&1
  grep -c "^--- " output/_probe249_both_successors.txt
  ```
- **期望**：**15** 条条目。
- **状态**：☑ 完成（15）。

## T-002 ★★ 发现第一版有 **4 条假靶子**（裸名归集）

- **验收**：
  ```bash
  cd "D:/AI/SW" && awk '/^--- /{h=$0} /  write$/{print h "  ||  " $0}' output/_probe249_both_successors.txt
  ```
- **期望**：写站点归到 `KFactor` ×3 + `IView::Name` ×1 ⇒ ★ 裸名口径报 **4 条**「两个后继都要」。
- **★ 真象**：`KFactor` 的写站点宿主是 **`ICustomBendAllowance`**；`Name` 的写站点宿主是 `IMate2`/`IFeature`/`CWStudy`。
- **状态**：☑ 完成。

## T-003 口径下沉到宿主级：7 个写站点逐个判接口

- **动作**：读每个写站点的**赋值来源**，判宿主接口。
- **验收**：
  ```bash
  cd "D:/AI/SW" && grep -nE "^    \(\"sw_" tests/test_multi_successor_both_needed_census.py
  ```
- **期望**：**7** 条表态（`ICustomBendAllowance` ×2 · `IMate2` · `IFeature` ×3 · `CWStudy`）。
- **状态**：☑ 完成。

## T-004 先写判据并**证明它能红**

- **验收 A（红基线）**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B -c "
  import sys, importlib.util
  sys.path.insert(0,'D:/AI/SW'); sys.path.insert(0,'D:/AI/SW/scripts'); sys.path.insert(0,'D:/AI/SW/tests')
  s=importlib.util.spec_from_file_location('t','D:/AI/SW/tests/test_multi_successor_both_needed_census.py')
  m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
  e=m._multi_pair_entries()
  print('条目', len(e), '写站点', len(m._write_sites({x[\"member\"] for x in e})))
  print('正常:', m._both_needed_failures(e, m._WRITE_SITE_REVIEW))
  mut=dict(m._WRITE_SITE_REVIEW); mut[('sw_sheet_metal.py',257,'bend_allowance','KFactor')]=('IBendsFeatureData','变异')
  print('变异:', m._both_needed_failures(e, mut))
  "
  ```
- **期望**：`条目 15 写站点 7` · `正常: []` · `变异: [\"sw_sheet_metal.py:257 … 该条目**两个后继都要**\"]`。
- **状态**：☑ 完成。

## T-005 判据转绿

- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/test_multi_successor_both_needed_census.py -q 2>&1 | tail -2
  ```
- **期望**：`6 passed`。
- **状态**：☑ 完成（6/6）。

## T-006 相关族回归（248 + 249）

- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/test_obsolete_name_host_adjudication.py tests/test_multi_successor_both_needed_census.py -q 2>&1 | tail -2
  ```
- **期望**：`12 passed`。
- **状态**：☑ 完成（12 passed）。

## T-007 门禁全套（★ 后台跑）

- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B scripts/release_check.py > output/_gate249.log 2>&1; tail -4 output/_gate249.log
  ```
- **期望**：`EXIT=0` · `missing []`。
- **状态**：☐ 见 `acceptance.md`。

## T-008 回写四处状态

- **动作**：`docs/ROADMAP.md` §一 · `memory/2026-10-09.md`（append）· `output/AUTO_HANDOFF.md`（覆盖）·
  `output/AUTO_RUN_2026-10-09-*.md` · `.specify/feature.json`。
- **验收**：
  ```bash
  cd "D:/AI/SW" && cat .specify/feature.json && ls specs/249-multi-successor-both-needed-census/
  ```
- **状态**：☐

## T-009 未改动证明（★ 用 mtime，**不用 `git status`**）

- **验收**：
  ```bash
  cd "D:/AI/SW" && ls -l --time-style="+%m-%d %H:%M" tools/build_obsolete_index.py scripts/sw_com_traps.py scripts/release_check.py docs/gate-classification.json
  ```
- **期望**：mtime **全部早于** `10-09 22:38`（★ 本轮开工时刻）。
- **状态**：☑ 完成。
