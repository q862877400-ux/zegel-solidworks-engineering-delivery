import inspect
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path[:0] = [r"" + _ROOT_S + r"\scripts"]

print("  ══ ① 引用文档：sw_pdm.get_all_external_references 怎么用 ══")
import sw_pdm
fn = getattr(sw_pdm, "get_all_external_references", None)
if fn:
    print("  签名:", inspect.signature(fn))
    for l in (inspect.getsource(fn).splitlines()[:14]):
        print("    %s" % l[:104])

print()
print("  ══ ② 有没有「从 model 取 PDM 文档 / 取引用」的 helper ══")
import re as _re
for mod_name in ("sw_pdm", "sw_connect"):
    m = __import__(mod_name)
    for n in sorted(dir(m)):
        if n.startswith("_"):
            continue
        o = getattr(m, n)
        if callable(o) and getattr(o, "__module__", "").endswith(mod_name):
            if _re.search(r"pdm|reference|external|document", n, re.I):
                try:
                    print("    %-16s %-36s %s" % (mod_name, n, str(inspect.signature(o))[:54]))
                except Exception:                              # noqa: BLE001
                    pass

print()
print("  ══ ③ 自定义属性 / 模板 有没有实现 ══")
for mod_name in ("sw_pdm", "sw_part", "sw_connect", "sw_delivery"):
    try:
        m = __import__(mod_name)
    except Exception:                                          # noqa: BLE001
        continue
    for n in sorted(dir(m)):
        if n.startswith("_"):
            continue
        o = getattr(m, n)
        if callable(o) and getattr(o, "__module__", "").endswith(mod_name):
            if _re.search(r"propert|custom|template|revision|title", n, re.I):
                try:
                    print("    %-16s %-38s %s" % (mod_name, n, str(inspect.signature(o))[:52]))
                except Exception:                              # noqa: BLE001
                    pass
