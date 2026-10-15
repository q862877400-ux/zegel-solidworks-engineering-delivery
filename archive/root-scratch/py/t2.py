import sys, io, importlib.util, re
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
spec = importlib.util.spec_from_file_location("ct", r"C:\swprojects\sw-skill-fork\scripts\sw_com_traps.py")
m = importlib.util.module_from_spec(spec); sys.modules["ct"]=m; spec.loader.exec_module(m)
print("  0x8002000A 判定:", m.ERROR_CODES.get(m.DISP_E_BADPARAMCOUNT)[:22])
print("  0x8002000B 判定:", m.ERROR_CODES.get(m.DISP_E_PARAMNOTOPTIONAL)[:22])
print("  0x80020004 判定:", m.ERROR_CODES.get(m.DISP_E_MEMBERNOTFOUND)[:22])
print("  byref_pair:", [type(x).__name__ for x in m.byref_pair()])
print("  真/伪 .swp:", m.is_swp_macro(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"junk"), m.is_swp_macro(b"Sub Main()"))
print("  SaveAs3 标记:", m.DEPRECATED_SAVEAS["IModelDocExtension.SaveAs"])
# 关键：模块注释里声称的 arity，逐条对反射
M = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_api_sldworks.py").read_text(encoding="utf-8")
def ar(iface, mem):
    g = re.search(r"'%s': \{\n(.*?)\n    \}," % re.escape(iface), M, re.S)
    return dict(re.findall(r"'(\w+)': (\d+)", g.group(1))).get(mem) if g else None
print()
print("  声称的 arity vs 反射:")
for iface, mem, claim in (("ISldWorks","GetErrorMessages","0"),
                          ("ISldWorks","OpenDoc6","6 参末2个[out]"),
                          ("ISldWorks","RunMacro2","5 参末1个[out]"),
                          ("IModelDocExtension","SaveAs","4"),
                          ("IModelDocExtension","SaveAs2","6"),
                          ("IModelDocExtension","SaveAs3","5")):
    print("    %-20s %-18s 反射 arity=%-3s  模块称=%s" % (iface, mem, ar(iface,mem), claim))