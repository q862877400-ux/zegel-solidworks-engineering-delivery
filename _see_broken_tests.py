import ast
import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\swprojects\sw-skill-fork")

#: 这两个断言是「**零参调用**」的判据 ⇒ 现在生产代码用 `call_com_member`，
#: 判据要**认这个名字**（不然后面的人会以为"没零参调用了"）
FIX = [
    ("tests/test_sw_simulation_signature_contract.py",
     "test_run_analysis_is_called_with_zero_arg"),
    ("tests/test_sw_view_contract.py", "test_zero_arg_view_methods"),
]
for rel, tname in FIX:
    p = ROOT / rel
    t = p.read_text(encoding="utf-8")
    i = t.index("def %s(" % tname)
    #: 找该函数体里提到 get_com_member 的行
    j = t.find("\ndef ", i + 1)
    body = t[i:j if j > 0 else len(t)]
    print("── %s :: %s" % (rel, tname))
    for k, l in enumerate(body.splitlines(), 1):
        if "get_com_member" in l:
            print("     %s" % l.strip()[:100])
