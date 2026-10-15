import re
from pathlib import Path
# 同一处设计缺口：sw_sldworks_app._checked 与 sw_section_view._call 也只校 arity，不校「是否存在」
for fn, old, new in (
 ("sw_sldworks_app.py",
  '    expected = ISLDWORKS_ARITY.get(member)\n    if expected is not None and expected != len(args):',
  '    expected = ISLDWORKS_ARITY.get(member)\n'
  '    if expected is None:\n'
  '        raise KeyError(\n'
  '            f"ISldWorks 上没有登记 {member}；本模块登记 "\n'
  '            f"{len(ISLDWORKS_ARITY)} 项。⚠ 不要临时加成员名 —— 先回反射核实它存在。")\n'
  '    if expected != len(args):'),
 ("sw_section_view.py",
  '    expected = table.get(member)\n    if expected is not None and expected != len(args):',
  '    expected = table.get(member)\n'
  '    if expected is None:\n'
  '        raise KeyError(\n'
  '            f"该族没有登记 {member}；本族登记 "\n'
  '            f"{len(table)} 项：{\', \'.join(table)}")\n'
  '    if expected != len(args):'),
 ("sw_document_core.py",
  '    expected = DOC_CORE_ARITY.get(member)\n    if expected is not None and expected != len(args):',
  '    expected = DOC_CORE_ARITY.get(member)\n'
  '    if expected is None:\n'
  '        raise KeyError(\n'
  '            f"没有登记 {member}；本模块登记 {len(DOC_CORE_ARITY)} 项。"\n'
  '            f"⚠ 不要临时加成员名 —— 先回反射核实它存在。")\n'
  '    if expected != len(args):'),
):
    p = Path(r"C:\swprojects\sw-skill-fork\scripts") / fn
    s = p.read_text(encoding="utf-8")
    if old in s:
        p.write_text(s.replace(old, new, 1), encoding="utf-8")
        print("  [ok]", fn)
    else:
        print("  [skip]", fn, "未匹配")
