from pathlib import Path
p = Path(r"D:\AI\SW\e2e2.py")
s = p.read_text(encoding="utf-8")
s = s.replace('"IAssemblyDoc", "GetComponents2", True, True',
              '"IAssemblyDoc", "GetComponents", True')
s = s.replace('    print("  插前组件数:", len(before))',
              '    print("  插前组件数:", len(before))\n'
              '    # ⚑ GetComponents2 **不存在** —— 官方真名是 GetComponents(1 参)。\n'
              '    #   又一次「凭印象写 API」，被护栏当场拦下。')
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("  已改为 GetComponents(1 参)")