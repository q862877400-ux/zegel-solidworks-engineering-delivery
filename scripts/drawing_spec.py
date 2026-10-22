"""工程图 DrawingSpec 子技能的兼容入口。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   scripts/drawing_spec.py
# 定位:   工程图 DrawingSpec 子技能的兼容入口。
# 官方依据: 不适用（兼容转发壳：真源见文件内 `_IMPLEMENTATION` 指向的模块）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import importlib.util
from pathlib import Path


_IMPLEMENTATION = (
    Path(__file__).resolve().parents[1]
    / "subskills"
    / "solidworks-engineering-drawing"
    / "scripts"
    / "drawing_spec.py"
)
_SPEC = importlib.util.spec_from_file_location(
    "solidworks_drawing_spec", _IMPLEMENTATION
)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"无法加载 DrawingSpec: {_IMPLEMENTATION}")
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)

__all__ = [name for name in vars(_MODULE) if not name.startswith("_")]
for _name in __all__:
    globals()[_name] = getattr(_MODULE, _name)
