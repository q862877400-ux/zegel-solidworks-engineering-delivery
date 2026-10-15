import re
from pathlib import Path
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_document_core.py")
s = p.read_text(encoding="utf-8")
s = s.replace('    "GetBuildNumbers": 1,\n    "GetBuildNumbers2": 2,\n',
  '    # ⚑ GetBuildNumbers / GetBuildNumbers2 的实参**全是 by-ref 出参**\n'
  '    #   （反射: Void GetBuildNumbers(String&, String&)）⇒ 调用方**一个都不传**。\n'
  '    #   迟到绑定下回写不保证 ⇒ 本模块**不提供**「取版本号」封装，已删除。\n'
  '    "GetBuildNumbers": 0,\n    "GetBuildNumbers2": 0,\n')
# 删函数
s = re.sub(r'\ndef get_build_numbers\(sldworks, which: str = ""\):.*?return _checked\(sldworks, "GetBuildNumbers", str\(which\)\)\n',
           '\n', s, flags=re.S)
s = s.replace('    "get_build_numbers",\n', '')
p.write_text(s, encoding="utf-8")
print("  [ok] sw_document_core: 已删除不可能工作的 get_build_numbers")
