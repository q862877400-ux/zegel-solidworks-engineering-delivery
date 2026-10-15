import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tests\test_sw_export_image_contract.py")
t = P.read_text(encoding="utf-8")

#: 两条测试要**真存在**的 .png（否则函数按设计抛"文件不在"）
for fname in ("test_calls_the_seven_arg_form", "test_empty_dispatch_variants_for_the_object_params"):
    i = t.index("def %s(" % fname)
    j = t.index("\ndef ", i + 1)
    body = t[i:j]
    body2 = body.replace("def %s():" % fname, "def %s(tmp_path):" % fname)
    body2 = body2.replace('r"D:\\AI\\SW\\output\\x.png"', 'str(_real_png(tmp_path))')
    t = t[:i] + body2 + t[j:]

#: 加个小工具：造一个**真的**空 PNG 文件（让"文件在且非空"那一关过）
HELPER = '''

def _real_png(tmp_path):
    """造一个**真的、非空**的 `.png`（只为过「文件在且非空」那一关）。"""
    p = Path(str(tmp_path)) / "x.png"
    p.write_bytes(b"\\x89PNG\\r\\n\\x1a\\n" + b"\\x00" * 16)
    return p

'''
if "_real_png" not in t.split("def test_calls")[0]:
    t = t.replace("class _Ext:", HELPER.lstrip("\n") + "\nclass _Ext:", 1)
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  语法 OK")
