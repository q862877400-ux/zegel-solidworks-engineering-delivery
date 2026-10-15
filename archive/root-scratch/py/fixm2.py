import sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
p = Path(r"D:\AI\SW\merge_dims.py")
s = p.read_text(encoding="utf-8")
# HEADER 里的四个表头要拆成独立标记，拼接时逐表闭合
s = s.replace('''#: 只读属性 —— 只能读，传 set 会失败
READONLY: dict[str, tuple[str, ...]] = {
#: 只写属性 —— ⚠ **读它会报 -2147352567「无法读只写属性」**
#: （错误文本随 UI 语言变化；pywin32 源码里无此消息，属本地化 HRESULT）
WRITEONLY: dict[str, tuple[str, ...]] = {
#: 内部使用成员 —— 官方标了 FHidden，**不应当作公开能力调用**
#: （典型是 `Dummy1..19` 这类占位，以及 `IModelDocExtension.ExtractImageData`）
HIDDEN: dict[str, tuple[str, ...]] = {
#: 成员名 → DISPID（makepy 生成物用它做主键，可与 wrapper 精确 join）
DISPID: dict[str, dict[str, int]] = {''',
'''#: 只读属性 —— 只能读，传 set 会失败
@@READONLY@@
#: 只写属性 —— ⚠ **读它会报 -2147352567「无法读只写属性」**
#: （错误文本随 UI 语言变化；pywin32 源码里无此消息，属本地化 HRESULT）
@@WRITEONLY@@
#: 内部使用成员 —— 官方标了 FHidden，**不应当作公开能力调用**
#: （典型是 `Dummy1..19` 这类占位，以及 `IModelDocExtension.ExtractImageData`）
@@HIDDEN@@
#: 成员名 → DISPID（makepy 生成物用它做主键，可与 wrapper 精确 join）
@@DISPID@@''')
# 拼接：按标记逐表替换
s = s.replace('        block = "\\n".join(x for x in blocks if x)\n'
              '        new = src.rstrip("\\n") + "\\n\\n\\n" + HEADER + block + "\\n"',
              '        raw = "\\n".join(x for x in blocks if x)\n'
              '        head, _, rest = HEADER.partition("@@READONLY@@")\n'
              '        seg_r, _, rest2 = rest.partition("@@WRITEONLY@@")\n'
              '        seg_w, _, rest3 = rest2.partition("@@HIDDEN@@")\n'
              '        seg_h, _, seg_d = rest3.partition("@@DISPID@@")\n'
              '        body = (head + "READONLY: dict[str, tuple[str, ...]] = {\\n" + seg_r\n'
              '                + "WRITEONLY: dict[str, tuple[str, ...]] = {\\n" + seg_w\n'
              '                + "HIDDEN: dict[str, tuple[str, ...]] = {\\n" + seg_h\n'
              '                + "DISPID: dict[str, dict[str, int]] = {\\n" + seg_d.rstrip("### DISPID\\n")\n'
              '                + raw.rstrip("\\n") + "\\n")\n'
              '        new = src.rstrip("\\n") + "\\n\\n\\n" + body')
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("  拼接逻辑已改为逐表闭合")