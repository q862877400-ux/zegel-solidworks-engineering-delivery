from pathlib import Path
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_jlcfa_fill.py")
s = p.read_text(encoding="utf-8")
# PLACEHOLDER 必须定义在 _has_cjk 之前
if s.index("PLACEHOLDER = ") > s.index("def _has_cjk"):
    s = s.replace('PLACEHOLDER = "【去填写】"\n', '', 1)
    s = s.replace('def _has_cjk(s: str) -> bool:',
                  'PLACEHOLDER = "【去填写】"\n\n\ndef _has_cjk(s: str) -> bool:', 1)
    p.write_text(s, encoding="utf-8")
    print("PLACEHOLDER 已前移")
import ast; ast.parse(s)
print("ok")