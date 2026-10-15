# Tasks — 加判别层

**Feature**: `specs/271-real-gap-visible-again/`
**日期**: 2026-10-10

## T-001 ★★ 先量：打两类站点的 `slots`/`com`
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -c "
  import sys; sys.path[:0]=['D:/AI/SW','D:/AI/SW/scripts']
  import check_dispatch_byref_guard as G, check_dispatch_entry_guard as DEG
  from pathlib import Path
  ROOT=Path('D:/AI/SW'); entries,_v,_n,_b,_df,_cf,files=DEG.scan(ROOT)
  classes,_r=DEG.resolution(entries,files); imap=DEG._import_map(files); srcs={p:files[p][0] for p in files}
  for e in entries:
      if classes.get((e[0].name, e[1].lineno), ('',0))[0]=='no-callers': continue
      inner=DEG.inner_wrapper_call(e[1], e[3]); slots=DEG.forward_slots(e[1], inner) if inner is not None else None
      if slots is None: continue
      for cp, call in DEG._entry_sites(e, files, imap):
          st, mem, com = G.com_args(e, cp, call, slots, srcs)
          if st=='ok' and mem in {'CreateFlattenRoute','GetNodeLocation'}:
              print('%-24s com=%d slots=%s' % (mem, len(com), slots))
  "
  ```
- **期望**：★ 两行**完全相同**（★ `slots=[('*args', None)]` · `com=1`）⇒ ★ **AST 分不开**。
- **状态**：☑ 完成。

## T-002 加判别层 + 跑门禁
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B scripts/check_dispatch_byref_guard.py 2>&1 | tail -2
  ```
- **期望**：`arity 不符 13` · `可核 21` · `已核 316` · ★ **`[PASS] · exit 0`**。
- **状态**：☑ 完成。

## T-003 判据能红 / 转绿
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/test_real_gap_visible_again.py -q 2>&1 | tail -2
  ```
- **期望**：`4 passed`。 **状态**：☑ 完成。

## T-004 ★★ 生成器链 + 门禁（★ 改了 `scripts/`）
- **状态**：☑ 生成器链 7 步 OK；☐ 门禁见 `acceptance.md`。

## T-005 回写四处状态
- **状态**：☐
