from pathlib import Path
p = Path(r"D:\AI\SW\e2e_toolbox.py")
s = p.read_text(encoding="utf-8")
s = s.replace('asm = sw.call_index(app, "ISldWorks", "NewDocument", "Assembly", 0, 0)',
              '# ⚑ NewDocument(String Template, Int32 Type, Double X, Double Y) —— 4 参\n'
              '        #   Template 传 ""（用系统默认模板）；Type: 1=swDocPART 2=swDocASSEMBLY\n'
              '        #   ⚠ 第一次写错成 3 参，被本仓库的 arity 护栏当场拦下 —— 护栏有效。\n'
              '        asm = sw.call_index(app, "ISldWorks", "NewDocument", "", 2, 0.0, 0.0)')
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("  已改为 4 参")