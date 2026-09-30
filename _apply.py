import io, re, sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
S = Path(r"C:\swprojects\sw-skill-fork\scripts")
FIX = [
 ("sw_sldworks_app.py", '"GetErrorMessages": 3,', '"GetErrorMessages": 0,'),
 ("sw_sldworks_app.py", '"GetLastSaveError": 2,', '"GetLastSaveError": 0,'),
 ("sw_model_doc_extension.py",
  '"GetObjectByPersistReference3": 2,   # ⚑ 反射是 **2 参**，初稿写了 1 —— 已更正',
  '"GetObjectByPersistReference3": 1,   # ⚑ 反射是 Object GetObjectByPersistReference3(Object)'),
 ("sw_model_doc_extension.py",
  '"GetMassProperties": 2,              # ⚑ 反射是 **2 参**，初稿写了 1 —— 已更正',
  '"GetMassProperties": 1,              # ⚑ Object GetMassProperties(Int32, Int32&)'),
 ("sw_document_core.py", '"SelectByID2": 11,', '"SelectByID2": 9,'),
 ("sw_section_view.py", '"GetFirstPlaneParameters": 2,', '"GetFirstPlaneParameters": 0,'),
 ("sw_section_view.py", '"GetSecondPlaneParameters": 2,', '"GetSecondPlaneParameters": 0,'),
 ("sw_section_view.py", '"GetThirdPlaneParameters": 2,', '"GetThirdPlaneParameters": 0,'),
]
NOTE = ('    # ⚑⚑ arity 口径 = **调用方要传的实参**，**排除 by-ref 出参**（`Xxx&`）。\n'
        '    #   反射里 `Void GetErrorMessages(Object&, Object&, Object&)` 是 **0 参** —\n'
        '    #   早先手写数成了 3，运行必错。由 tests 抓出。\n')
for fn, old, new in FIX:
    p = S / fn
    s = p.read_text(encoding="utf-8")
    if old in s:
        p.write_text(s.replace(old, new, 1), encoding="utf-8")
        print("  [ok]", fn, "->", new[:46])
    else:
        print("  [SKIP]", fn, "未匹配:", old[:40])
# 口径注释插到第一张表后面
p = S / "sw_sldworks_app.py"
s = p.read_text(encoding="utf-8")
if "arity 口径 = **调用方要传的实参**" not in s:
    anchor = 'ISLDWORKS_ARITY: dict[str, int] = {\n'
    s = s.replace(anchor, anchor + NOTE, 1)
    p.write_text(s, encoding="utf-8")
    print("  [ok] 口径注释已插入 sw_sldworks_app")
