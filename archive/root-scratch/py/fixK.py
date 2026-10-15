import sys
from pathlib import Path
p = Path(r"D:\AI\SW\build_complete_index.py")
s = p.read_text(encoding="utf-8")
old = '''            if INTERNAL.match(name):
                continue  # COM 内部分发口，不是独立能力'''
new = '''            if INTERNAL.match(name):
                continue  # COM 内部分发口，不是独立能力
            # ⚑ 零参成员的返回值名（如 `Point get_X()` → 成员名 `X`）**也登记**：
            #   它们是**可取用的属性**（读 X / Y / Z 坐标、读 ID），
            #   不是文档占位符。漏掉会让覆盖表永远差 14 个。
            if name[0].islower() and name.upper() == name:
                fams[cur]["props"].append(name)
                continue'''
assert old in s
p.write_text(s.replace(old, new, 1), encoding="utf-8")
import ast; ast.parse(s.replace(old, new, 1))
print("  [ok] 构建器已登记零参属性的返回值名")