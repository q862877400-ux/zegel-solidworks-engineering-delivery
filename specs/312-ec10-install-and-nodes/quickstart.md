# Quickstart — 312-ec10-install-and-nodes

**Feature**: `specs/312-ec10-install-and-nodes/`

---

## 一、跑判据

```bash
python -m pytest tests/test_ec10_*.py -q
```

## 二、怎么用

```python
import sys
sys.path.insert(0, "scripts")
from engineering import nodes
```

## 三、边界

★ 本模块**纯离线**（★ 不 import COM）—— ★ 真机部分见 `acceptance.md` 的 `runtime` 段。
