from pathlib import Path
p = Path(r"D:\AI\SW\merge_final.py")
s = p.read_text(encoding="utf-8")
old = '''        n = r["name"]
        if r["kind"] == "property" and n[:4] in ("get_", "set_"):
            n = n[4:]'''
new = '''        # 2)无条件3剥4 get_/set_ 前缀：SolidWorks 的方法名一律 PascalCase，
        #    绝不会出现小写 get_ 前缀 => 剥了不会误伤。早先按 kind 判定，
        #    漏掉了既标 hidden 又是属性的 get_Dummy001 / set_Dummy001。
        n = r["name"]
        if n[:4] in ("get_", "set_"):
            n = n[4:]'''
assert old in s, "no match"
p.write_text(s.replace(old, new, 1), encoding="utf-8")
print("  patched")