# 014 · Tasks（全部完成，轮 94）

- [x] T-1001 写 `tools/census_orphan_callability.py`
  `→ 验收:` `python tools/census_orphan_callability.py`
- [x] T-1002 跑普查 ⇒ 17 个候选：**ok 14 · raised 3**
- [x] T-1003 ★ 逐个复验 raised
  ⇒ `get_extension` **单独调用是好的**（假阳性）；`create_cut_list` **真缺陷**；
  `get_mass_property_override_options` **真缺陷**（轮 93 已知）
  `→ 验收:` 见 [converge.md](converge.md) §2
- [x] T-1004 更新缺陷档（追加 `create_cut_list` + 普查结果）
  `→ 验收:` `Select-String docs\orphan-functions-not-runnable.md -Pattern 'create_cut_list'`
- [x] T-1005 更正轮 93 的 25% 估计 ⇒ **12%**
- [x] T-1006 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
