# Quickstart — 304-ec02-rules-and-standards

**Feature**: `specs/304-ec02-rules-and-standards/`

---

## 一、跑判据

```bash
python -m pytest tests/test_ec02_*.py -q
```

## 二、怎么用

```python
import sys
sys.path.insert(0, "scripts")
from engineering import rules
```

## 三、边界

★ 本模块**纯离线**（★ 不 import COM）—— ★ 真机部分见 `acceptance.md` 的 `runtime` 段。
