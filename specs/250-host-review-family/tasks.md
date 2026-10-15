# Tasks — 245 其余 13 条命中名的宿主表达式级表态

**Feature**: `specs/250-host-review-family/`
**日期**: 2026-10-09
**规则**: ★ 每条带**可复制执行**的验收命令；★ **先写能红的判据**。

---

## T-001 先量：13 个名 + 全部站点 + 上下文

- **验收**（★ 复制执行）：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B output/_probe250_family_sites.py > output/_probe250_family_sites.txt 2>&1
  grep -c "^########## " output/_probe250_family_sites.txt
  ```
- **期望**：**13** 个名。
- **状态**：☑ 完成。

## T-002 列出每个名的**全部条目接口**（★ 一名可跨多接口）

- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B -c "
  import sys; sys.path[:0]=['D:/AI/SW','D:/AI/SW/scripts','D:/AI/SW/tests']
  from tests.test_obsolete_multi_successor import _multi
  from collections import defaultdict
  d=defaultdict(set)
  [d[e['member']].add(e['interface']) for e in _multi()]
  for k in ('GetMassProperties','GetSplines','KFactor','SketchTrim'): print(k, sorted(d[k]))
  "
  ```
- **期望**：`GetMassProperties ['IModelDoc2','ISldWorks']` · `GetSplines ['ISketchBlockDefinition','IView']` ·
  `KFactor ['IBendsFeatureData','IOneBendFeatureData','ISheetMetalFeatureData']` · `SketchTrim ['IModelDoc2']`。
- **状态**：☑ 完成。

## T-003 判读 14 处站点的宿主接口

- **验收**：
  ```bash
  cd "D:/AI/SW" && grep -nE "^    \"" tests/test_obsolete_host_review_family.py | head -20
  ```
- **期望**：13 个名，`real-hit` 6 个名（7 处站点）、`false-hit` 7 个名（7 处站点）。
- **状态**：☑ 完成。

## T-004 先写判据并**证明它能红**

- **验收（红基线）**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B -c "
  import sys, importlib.util
  sys.path[:0]=['D:/AI/SW','D:/AI/SW/scripts','D:/AI/SW/tests']
  s=importlib.util.spec_from_file_location('t','D:/AI/SW/tests/test_obsolete_host_review_family.py')
  m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
  h=m._host_sites(); i=m._entry_ifaces()
  print('名', len(h), '站点', sum(len(v) for v in h.values()))
  print('清空表 =>', len(m._adjudication_failures(h, {}, i)))
  mut=dict(m._HOST_EXPR_REVIEW); c,f_,w,st=mut['SketchTrim']; mut['SketchTrim']=('real-hit',f_,w,st)
  print('翻 SketchTrim:', m._adjudication_failures(h, mut, i)[:1])
  "
  ```
- **期望**：`名 13 站点 14` · `清空表 => 13` · 翻码 ⇒ 「表态与接口矛盾」。
- **状态**：☑ 完成。

## T-005 判据转绿

- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/test_obsolete_host_review_family.py -q 2>&1 | tail -2
  ```
- **期望**：`6 passed`。
- **状态**：☑ 完成。

## T-006 相关族回归（248 + 249 + 250）

- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/test_obsolete_host_review_family.py tests/test_obsolete_name_host_adjudication.py tests/test_multi_successor_both_needed_census.py -q 2>&1 | tail -2
  ```
- **期望**：`18 passed`。
- **状态**：☐

## T-007 门禁全套（★ 后台跑）

- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B scripts/release_check.py > output/_gate250.log 2>&1; tail -4 output/_gate250.log
  ```
- **期望**：`EXIT=0` · `missing []`。
- **状态**：☐ 见 `acceptance.md`。

## T-008 回写四处状态

- **状态**：☐

## T-009 未改动证明（★ 用 mtime）

- **验收**：
  ```bash
  cd "D:/AI/SW" && ls -l --time-style="+%m-%d %H:%M" tools/build_obsolete_index.py scripts/sw_com_traps.py scripts/release_check.py docs/gate-classification.json tests/test_obsolete_multi_successor_impact.py
  ```
- **期望**：全部早于 `10-09 22:38`（★ 本会话开工时刻）—— ★ 尤其 `test_obsolete_multi_successor_impact.py`
  必须仍是 `22:41`（★ 248 改的），**本轮不再动它**。
- **状态**：☑ 完成。
