# Tasks — `Name` 的逐宿主表达式表态

**Feature**: `specs/248-name-host-adjudication/`
**日期**: 2026-10-09
**规则**: ★ 每条任务带**可复制执行**的验收命令；★ **先写能红的判据**再改实现。

---

## T-001 先量：导出 `Name` 的 51 处站点 + 上下文

- **动作**：写一次性探针 `output/_probe248_name_sites.py`（★ 口径 **import** 245 的 `_hit_sites`，不重写）。
- **验收**（★ 复制执行）：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B output/_probe248_name_sites.py > output/_probe248_name_sites.txt 2>&1
  head -3 output/_probe248_name_sites.txt
  ```
- **期望**：`=== Name 站点总数: 51 ===`；宿主表达式分组 **16** 行。
- **状态**：☑ 完成（读数 51 / 16）。

## T-002 先写判据并**证明它能红**

- **动作**：新建 `tests/test_obsolete_name_host_adjudication.py`（含纯函数 `_adjudication_failures` + 三组合成负例）。
- **验收 A（红基线，★ 改实现前必须先红）**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B -c "
  import sys, importlib.util
  sys.path.insert(0,'D:/AI/SW'); sys.path.insert(0,'D:/AI/SW/scripts'); sys.path.insert(0,'D:/AI/SW/tests')
  s=importlib.util.spec_from_file_location('t','D:/AI/SW/tests/test_obsolete_name_host_adjudication.py')
  m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
  h=m._host_sites()
  print('清空表 =>', len(m._adjudication_failures(h, {})), '条未表态')
  print('删 av   =>', m._adjudication_failures(h, {k:v for k,v in m._NAME_HOST_REVIEW.items() if k!='av'}))
  "
  ```
- **期望**：`清空表 => 16 条未表态`；`删 av => ["宿主 'av' 未表态（真树上有 1 处）"]`。
- **状态**：☑ 完成（16 / 1，且翻 `view` ⇒ 「表态与接口矛盾」）。

## T-003 逐宿主表达式判读（16 个）

- **动作**：读每个宿主表达式的**赋值来源**（同函数内向上找 `=`），由官方 Returns 定接口。
- **验收**：
  ```bash
  cd "D:/AI/SW" && grep -nE "^    \"" tests/test_obsolete_name_host_adjudication.py | head -20
  ```
- **期望**：16 个宿主表达式，`view` / `av` 为 `REAL_HIT`（IView），其余 14 个为 `FALSE_HIT`。
- **状态**：☑ 完成。

## T-004 判据转绿

- **验收**（★ 复制执行）：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/test_obsolete_name_host_adjudication.py -q 2>&1 | tail -2
  ```
- **期望**：`6 passed`。
- **状态**：☑ 完成（6/6）。

## T-005 补 245 的登记（`_HOST_REVIEW["Name"]`）

- **动作**：证据站点 2 → 5（4 真 + 1 假示例）；依据改写为「51 处 / 16 宿主 / 真 4 假 47」。
- **验收**：
  ```bash
  cd "D:/AI/SW" && sed -n '/^    "Name": (/,/^    ),/p' tests/test_obsolete_multi_successor_impact.py
  ```
- **期望**：证据含 `sw_drawing_query.py:194` / `:264` / `sw_drawing_view.py:436` / `sw_review.py:637`。
- **状态**：☑ 完成。

## T-006 相关族回归

- **验收**（★ 复制执行）：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/test_obsolete_name_host_adjudication.py tests/test_obsolete_multi_successor_impact.py tests/test_obsolete_multi_successor.py tests/test_deprecated_multi_successor_adjudication.py tests/test_deprecated_table_admission.py tests/test_deprecated_entry_interlock.py -q 2>&1 | tail -2
  ```
- **期望**：`46 passed`。
- **状态**：☑ 完成（46 passed）。

## T-007 门禁全套（★ 后台跑，前台 120s 会 SIGTERM）

- **验收**（★ 复制执行）：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B scripts/release_check.py > output/_gate248.log 2>&1; tail -6 output/_gate248.log
  ```
- **期望**：`EXIT=0` · `missing []`。
- **状态**：☐ 见 `acceptance.md`。

## T-008 回写四处状态

- **动作**：`docs/ROADMAP.md` §一 游标 · `.workbuddy-ai/memory/2026-10-09.md`（append）·
  `output/AUTO_HANDOFF.md`（覆盖）· `output/AUTO_RUN_2026-10-09-*.md`（新增）· `.specify/feature.json`。
- **验收**：
  ```bash
  cd "D:/AI/SW" && cat .specify/feature.json && ls specs/248-name-host-adjudication/
  ```
- **期望**：`feature_directory` = `specs/248-name-host-adjudication`；四件齐。
- **状态**：☐

## T-009 未改动的证明

- **★ 口径**：本仓工作树是「**已 staged 的整树基线**」⇒ `git status --short` 里绝大多数是 `A`/`M`，
  ★ **不能用它核「我这轮改了什么」**。用 **mtime** 核（★ 本轮开工时刻 = `2026-10-09 22:38`）。
- **验收**（★ 复制执行）：
  ```bash
  cd "D:/AI/SW" && ls -l --time-style="+%m-%d %H:%M" tools/build_obsolete_index.py scripts/sw_com_traps.py scripts/release_check.py docs/gate-classification.json && echo "--- 本轮改过的文件 ---" && find . -maxdepth 2 -newermt "2026-10-09 22:38" -type f -not -path "./.git/*" -not -name "*.pyc" -not -path "./__pycache__/*"
  ```
- **期望**：四个文件的 mtime **全部早于** `10-09 22:38`（`build_obsolete_index.py` 是 `10-03`、
  `release_check.py` / `gate-classification.json` 是 `10-09 14:41`、`sw_com_traps.py` 是 `10-09 19:46`）；
  ★ 「本轮改过的文件」里**只有** `tests/test_obsolete_*` 两个 + `output/_probe248_*` / `_gate248.log`。
- **状态**：☑ 完成（读数见 `acceptance.md` §三）。

