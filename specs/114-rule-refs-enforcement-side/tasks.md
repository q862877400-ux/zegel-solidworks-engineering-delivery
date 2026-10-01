# 114 · Tasks（全部完成，轮 194）

- [x] T-11401 ★★ 测量全仓库引用 R 编号的文件
  `→ 验收:` `python -c "import re,sys;from pathlib import Path;R=Path('.');print(sum(1 for p in list(R.glob('scripts/*.py'))+list(R.glob('tests/*.py'))+list(R.glob('docs/*.md')) if re.search(r'\bR\d{1,2}\b',p.read_text(encoding='utf-8',errors='replace'))))"`（**17**）
- [x] T-11402 ★★★ 扩到执行侧 `unregistered_refs(glob, registry, base=None)`
  `→ 验收:` `python scripts/check_union_conventions.py`（**8 段全过 · exit 0**）
- [x] T-11403 ★★★ 新检查抓到一处（docstring 里的举例 `R99`）⇒ 改成 `R<n>` 占位
- [x] T-11404 ★★ 在登记表里**声明覆盖面**（守什么 / 不守什么）
- [x] T-11405 ★ 3 条永久测试（**全程临时目录**）
  `→ 验收:` `python -m pytest tests/test_gate_negative_cases.py -q`（**49 passed**）
- [x] T-11406 事实 134
- [x] T-11407 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）· 全量 **1255 passed**
