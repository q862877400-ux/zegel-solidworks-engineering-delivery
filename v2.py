import sys, re
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
M = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_api_sldworks.py").read_text(encoding="utf-8")
def reg(iface, member):
    m = re.search(r"'%s': \{\n(.*?)\n    \}," % re.escape(iface), M, re.S)
    if not m: return None
    d = dict(re.findall(r"'(\w+)': (\d+)", m.group(1)))
    return d.get(member)
print("=== ① 子代理说 SaveAs / SaveAs2 已 Obsolete，应迁 SaveAs3 —— 我索引里有吗 ===")
for v in ("SaveAs", "SaveAs2", "SaveAs3", "SaveAs4"):
    print("  IModelDocExtension.%-10s arity=%s" % (v, reg("IModelDocExtension", v)))
print()
print("=== ② 弹窗开关：ShowFeatureErrorDialog / GetCurrentLicenseType ===")
for iface, mem in (("IModelDoc2","ShowFeatureErrorDialog"),
                   ("IModelDoc2","GetCurrentLicenseType"),
                   ("IModelDocExtension","GetLicenseType"),
                   ("ISldWorks","GetCurrentLicenseType")):
    print("  %-20s.%-26s arity=%s" % (iface, mem, reg(iface, mem)))
print()
print("=== ③ 我已有的 swSaveAsOptions 表 vs 子代理给的官方值 ===")
app = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_sldworks_app.py")
t = app.read_text(encoding="utf-8") if app.is_file() else ""
print("  sw_sldworks_app.py 存在:", app.is_file())
print("  (该文件本轮已并入 sw_api_sldworks / 删了自造模块)")
m = re.search(r'SW_SAVE_AS_OPTIONS.*?\n\}', M, re.S)
if m: print("  索引里的:", " ".join(re.findall(r"'(sw\w+)': (\d+)", m.group(0))))
print()
print("=== ④ HRESULT arity 判据的两个码（第三方说法，本机无法核验，仅记录）===")
print("  DISP_E_BADPARAMCOUNT     = 0x8002000A (-2147352562)  参数太多")
print("  DISP_E_PARAMNOTOPTIONAL = 0x8002000B (-2147352561)  参数太少")