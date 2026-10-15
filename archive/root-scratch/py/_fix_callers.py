"""★ 一次性：修调用器的形参撞名、给 dirty 换写操作、给 extrude 补必填实参。"""
from pathlib import Path

ROOT = Path(r"D:\AI\SW")

# ── ① tool_caller：首参改名，避免与工具的形参撞名 ─────────────────────────
p = ROOT / "tools/tool_caller.py"
s = p.read_text(encoding="utf-8")
s = s.replace("def describe(name: str) -> dict:", "def describe(tool_name: str) -> dict:")
s = s.replace("def call(name: str, *, inject_objects=None, **params):",
              "def call(tool_name: str, *, inject_objects=None, **params):")
s = s.replace('    entry = _specs().get(name)\n    if not entry:\n        return False, "★ 工具名不在声明里：%s" % name',
              '    entry = _specs().get(tool_name)\n    if not entry:\n'
              '        return False, "★ 工具名不在声明里：%s" % tool_name')
s = s.replace('    entry = _specs().get(name)\n    if not entry:\n        return {"found": False}',
              '    entry = _specs().get(tool_name)\n    if not entry:\n        return {"found": False}')
s = s.replace('    :param inject_objects: `{注入名: 宿主对象}`（★ 如 `{"model": model, "sw": sw}`）',
              '    ★★ 首参刻意**不叫 `name`** —— ★ 真机踩过：★ 有的工具的形参**就叫 `name`** ⇒\n'
              '      ★ 用 `call(name, **params)` 形式的调用会撞成 `got multiple values for argument \'name\'` ✗\n'
              '    :param inject_objects: `{注入名: 宿主对象}`（★ 如 `{"model": model, "sw": sw}`）')
p.write_text(s, encoding="utf-8")
import ast
ast.parse(s)
print("① 首参已改名 tool_name")

# ── ② 探针：dirty 换写操作 + extrude 补实参 ──────────────────────────────
pr = ROOT / "tools/probe_fingerprint_sensitivity.py"
ps = pr.read_text(encoding="utf-8")
ps = ps.replace('    "dirty": "solidworks_sketch_start",\n',
                '    #: ★★ 真机实测：`sketch_start` **确实进了编辑态**（`edit_mode` = sensitive）\n'
                '    #:   ★ 而 `GetSaveFlag` **没动** ⇒ ★ **进草图编辑态不算「脏」**（★ 要改几何才脏）\n'
                '    #:   ⇒ ★ 所以给 `dirty` 换一个**真的改文档**的写操作 ✓\n'
                '    "dirty": "solidworks_config_create",\n')
ps = ps.replace('    "solidworks_extrude_boss": {},',
                '    #: ★ 真机实测：★ `sketch_name`/`depth_mm` 的 `default` 是 `Ellipsis`（= 必填）\n'
                '    #:   ⇒ ★ 必须**主动给值**，否则底层报「缺 2 个位置实参」✗\n'
                '    "solidworks_extrude_boss": {"sketch_name": "Sketch1", "depth_mm": 10.0},')
pr.write_text(ps, encoding="utf-8")
ast.parse(ps)
print("② dirty 换写操作 + extrude 补实参")
