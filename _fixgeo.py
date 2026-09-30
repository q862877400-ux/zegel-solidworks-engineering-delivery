import io, sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_geometry.py")
s = p.read_text(encoding="utf-8")
FIX = [
 # 1) GetAdjacentFace -> GetAdjacentFaces（官方是复数）
 ('    ⚠ 官方有 ``GetAdjacentFace2`` 等多个重载，差别未注明\n'
  '      ⇒ 本模块只调最基础的无参版。',
  '    ⚑⚑ **更正**：初稿调的是 ``GetAdjacentFace``（**单数**），官方实为\n'
  '      ``GetAdjacentFaces``（**复数**）—— 拼错会让运行时直接 AttributeError。\n'
  '      由 scripts/audit_call_arity.py 的「查不到」一栏抓出。'),
 ('get_com_member(edge, "GetAdjacentFace")', 'get_com_member(edge, "GetAdjacentFaces")'),
 # 2) MateType -> Type（官方 IMate2 上是 Type）
 ('    """配合类型码。⚑ 官方是**属性**。"""\n'
  '    _require(mate, "mate")\n'
  '    return int(get_com_member(mate, "MateType") or -1)',
  '    """配合类型码。⚑ 官方是**零参方法** ``Type()``。\n'
  '\n'
  '    ⚑⚑ **更正**：初稿调的 ``MateType`` **在 IMate2 上不存在**，\n'
  '      官方是 ``Type()``；另有两个真成员 ``MinimumVariation`` / ``MaximumVariation``。\n'
  '      同样由 audit_call_arity.py 抓出。\n'
  '    """\n'
  '    _require(mate, "mate")\n'
  '    return int(get_com_member(mate, "Type") or -1)'),
]
for old, new in FIX:
    if old in s:
        s = s.replace(old, new, 1)
        print("  [ok]", old.splitlines()[0][:52])
    else:
        print("  [SKIP]", old.splitlines()[0][:52])
p.write_text(s, encoding="utf-8")
