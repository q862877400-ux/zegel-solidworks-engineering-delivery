import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\audit_call_arity.py")
lines = P.read_text(encoding="utf-8").splitlines(keepends=True)

# 修 L192（1 基）与 L197/L199 的引号
fixes = {
    192: '        "（`_comtypes_document_names()`，由 `comtypes.client.GetModule` 得到）。"\n',
    197: '        "`sw.OpenDoc6(path, type, options, empty)` —— 同样是 **comtypes 早绑定**"\n',
    199: '        "comtypes 代理自行分配出参。**不是缺陷。**"\n',
}
for n, new in fixes.items():
    old = lines[n - 1]
    lines[n - 1] = new
    print("  L%-4d %s" % (n, ("改 " + old.strip()[:48] + " …") if old != new else "（未变）"))
t = "".join(lines)
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  语法 OK")

# 调用方：元组从 4 元变 5 元
t = P.read_text(encoding="utf-8")
n1 = t.count("_ok, _doubt, _missing, _dyn = audit(")
t = t.replace("_ok, _doubt, _missing, _dyn = audit(",
              "_ok, _doubt, _missing, _dyn, _com = audit(", 1)
n2 = t.count("ok, doubt, missing, dynamic = audit(")
t = t.replace("ok, doubt, missing, dynamic = audit(",
              "ok, doubt, missing, dynamic, comtypes = audit(", 1)
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok 调用方已跟上（%d + %d 处）" % (n1, n2))
