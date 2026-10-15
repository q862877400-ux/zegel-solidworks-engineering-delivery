from pathlib import Path
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_jlcfa_audit.py")
s = p.read_text(encoding="utf-8")
# GENERATED 视作 SELECT 的成功态
s = s.replace('    if S.page_kind(st) == kind:\n        return h, w',
              '    cur = S.page_kind(st)\n'
              '    if cur == kind or (kind == "SELECT" and cur == "GENERATED"):\n'
              '        return h, w')
s = s.replace('            if S.page_kind(S.read_state(w)) == kind:',
              '            _k = S.page_kind(S.read_state(w))\n'
              '            if _k == kind or (kind == "SELECT" and _k == "GENERATED"):')
# 生成成功也认 GENERATED
s = s.replace('    rec["ok"] = "SLDPRT" in title or "SLDASM" in title',
              '    rec["ok"] = ("SLDPRT" in title or "SLDASM" in title\n'
              '                or "建模完成" in S.read_state(w)["visible"])')
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("audit 已认 GENERATED 态")