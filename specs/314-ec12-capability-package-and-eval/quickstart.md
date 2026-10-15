# Quickstart — 314-ec12-capability-package-and-eval

**Feature**: `specs/314-ec12-capability-package-and-eval/`

---

## 一、跑判据

```bash
python -m pytest tests/test_ec12_*.py -q
```

## 二、怎么用

```python
import sys
sys.path.insert(0, "scripts")
from engineering import evaluation
```

## 三、边界

★ 本模块**纯离线**（★ 不 import COM）—— ★ 真机部分见 `acceptance.md` 的 `runtime` 段。
