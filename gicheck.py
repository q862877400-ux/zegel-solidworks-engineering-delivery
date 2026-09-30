import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_gui_input as GI
print("① 配置项:")
for k, v in GI.CONFIG.items():
    print("     %-18s %r" % (k, v))
print()
print("② 换个策略只改配置，不改代码:")
GI.CONFIG["commit_key"] = "tab"
print("     commit_key -> %r" % GI.CONFIG["commit_key"])
GI.CONFIG["commit_key"] = "enter"
print("     commit_key -> %r" % GI.CONFIG["commit_key"])
print()
print("③ 小数点键码常量: 0x%X（win32con 无 VK_OEM_PERIOD）" % GI.VK_PERIOD)
print("④ 数字键映射: %s" % {k: hex(v) for k,v in list(GI.VK_DIGIT.items())[:5]})