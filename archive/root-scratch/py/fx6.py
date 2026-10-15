from pathlib import Path
p = Path(r"D:\AI\SW\probe_api.py")
s = p.read_text(encoding="utf-8")
s = s.replace('"GetAddinObject"', '"GetAddInObject"')
# ③ 改成用 GetCommandID / GetCommandManager 逐个查，不猜批量接口
old = s[s.index("        print(\"  ③"):s.index("        print()\n        print(\"  ①")]
new = '''        print("  ③ SolidWorks 命令表里有没有它注册的：")
        try:
            cm = sw.call_index(app, "ISldWorks", "GetCommandManager", 1)   # 1=模型
            print("     命令管理器:", repr(cm)[:40])
        except Exception as e:
            print("     ERR", str(e)[:60])
'''
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("  成员名已改：GetAddInObject（大写 I）")