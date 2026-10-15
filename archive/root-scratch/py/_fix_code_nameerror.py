import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_export.py")
t = P.read_text(encoding="utf-8")
i = t.index("def export_to_image(")
j = t.find("\ndef ", i + 1)
body = t[i:j if j > 0 else len(t)]
print("  ── 函数体里还在用 `code` 的地方 ──")
n = 0
for k, l in enumerate(body.splitlines(), 1):
    if "code" in l and "code =" not in l:
        print("     %s" % l.strip()[:100])
        n += 1
print("  共 %d 处" % n)

#: 把报错消息里的 `%r` 占位与变量名一起换成 `ok`
body2 = body.replace('"IModelDocExtension.SaveAs3 返回 %r（非 0）⇒ 图片没导出来。"',
                      '"IModelDocExtension.SaveAs3 返回 False ⇒ 图片没导出来。"')
body2 = body2.replace('"⚠ 常见原因：扩展名不在该文档类型的图片过滤器里 / 路径不可写。" % (code,)',
                      '"⚠ 常见原因：扩展名不在该文档类型的图片过滤器里 / 路径不可写。"')
body2 = body2.replace('"SaveAs3 返回 %r（看着成功）但**文件不在或为空**：%s —— "',
                       '"SaveAs3 返回 True（看着成功）但**文件不在或为空**：%s —— "')
body2 = body2.replace('"★ 这正是「**0 不代表成功**」那条纪律要挡的（照 `export_to_step` 的既有做法）。"\n            % (code, p)',
                       '"★ 这正是「**成功返回值不代表文件写出来了**」那条纪律要挡的"\n            "（照 `export_to_step` 的既有做法）。" % (p,)')
t = t[:i] + body2 + (t[j:] if j > 0 else "")
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  语法 OK")
print()
print("  ── 改完后再看有没有残留 `code` ──")
i = t.index("def export_to_image(")
j = t.find("\ndef ", i + 1)
for k, l in enumerate(t[i:j if j > 0 else len(t)].splitlines(), 1):
    if "code" in l:
        print("     %s" % l.strip()[:100])
