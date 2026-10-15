# Tasks — 索引后继规则：同名链接优先

**Feature**: `specs/251-index-successor-rule/`
**日期**: 2026-10-09

---

## T-001 先量：规则生效会改动多少条

- **验收**（★ 复制执行）：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B output/_probe251_rule_impact.py > output/_probe251_rule_impact.txt 2>&1
  grep -E "总条目|多链接|含「同名链接」|后继会变" output/_probe251_rule_impact.txt
  ```
- **期望**：`总条目 1671` · `多链接 254` · `含同名链接 11` · ★ `后继会变 6`。
- **状态**：☑ 完成（1671 / 254 / 11 / **6**）。

## T-002 备份索引（★ 可回滚）

- **验收**：
  ```bash
  cd "D:/AI/SW" && cp specs/202-user-coverage-gaps/recon/official-obsolete-index.json output/_index_backup_251.json && wc -c < output/_index_backup_251.json
  ```
- **期望**：`474209`。
- **状态**：☑ 完成。

## T-003 改生成器（★ 只改取链接那三行）

- **验收**：
  ```bash
  cd "D:/AI/SW" && grep -nA6 "spec 251" tools/build_obsolete_index.py | head -12
  ```
- **期望**：出现「同名链接优先」的实现（`re.findall` + 同名匹配）。
- **状态**：☑ 完成。

## T-004 重生成索引并核对 diff

- **验收**（★ 复制执行）：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B tools/build_obsolete_index.py > /dev/null 2>&1
  "C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -c "
  import json
  a=json.load(open('output/_index_backup_251.json',encoding='utf-8'))
  b=json.load(open('specs/202-user-coverage-gaps/recon/official-obsolete-index.json',encoding='utf-8'))
  ea={(e['interface'],e['member']):e.get('successor') for e in a['entries']}
  eb={(e['interface'],e['member']):e.get('successor') for e in b['entries']}
  d=[(k,ea[k],eb[k]) for k in ea if ea[k]!=eb.get(k)]
  print('条目数', len(ea), '->', len(eb), '| 变动', len(d))
  "
  ```
- **期望**：`条目数 1671 -> 1671 | 变动 6`。
- **状态**：☑ 完成。

## T-005 同步连带判据（★ 4 处）

- **验收**：
  ```bash
  cd "D:/AI/SW" && timeout 400 "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/test_obsolete_multi_successor.py tests/test_obsolete_multi_successor_impact.py tests/test_obsolete_host_review_family.py tests/test_obsolete_name_host_adjudication.py tests/test_multi_successor_both_needed_census.py tests/test_deprecated_multi_successor_adjudication.py tests/test_deprecated_table_admission.py tests/test_deprecated_entry_interlock.py tests/test_deprecated_admissible_disposition.py -q 2>&1 | tail -2
  ```
- **期望**：全绿。
- **状态**：☐

## T-006 门禁全套（★ 后台跑）

- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B scripts/release_check.py > output/_gate251.log 2>&1; tail -4 output/_gate251.log
  ```
- **期望**：`EXIT=0` · `missing []`。
- **状态**：☐ 见 `acceptance.md` §五。

## T-007 回写四处状态

- **状态**：☐

## T-008 未改动证明（★ 用 mtime）

- **验收**：
  ```bash
  cd "D:/AI/SW" && ls -l --time-style="+%m-%d %H:%M" scripts/sw_com_traps.py scripts/release_check.py docs/gate-classification.json tools/build_obsolete_index.py
  ```
- **期望**：`sw_com_traps.py` / `release_check.py` / `gate-classification.json` **早于** `22:38`；
  ★ `build_obsolete_index.py` **晚于** `22:38`（★ 本轮**故意**改的 —— 唯一被改的 `tools/` 文件）。
- **状态**：☑ 完成。
