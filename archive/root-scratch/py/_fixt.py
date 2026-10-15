import re
from pathlib import Path
# 1) 测试的反射解析器加归一化
p = Path(r"C:\swprojects\sw-skill-fork\tests\test_app_and_section_contract.py")
s = p.read_text(encoding="utf-8")
s = s.replace(
    'SIG = re.compile(r"^\\S+\\s+(\\w+)\\s*\\((.*)\\)$")',
    'SIG = re.compile(r"^\\S+\\s+(\\w+)\\s*\\((.*)\\)$")\n\n\n'
    'def _com(name: str) -> str:\n'
    '    """反射的属性形态是 get_/set_ 前缀；COM 名没有这个前缀。"""\n'
    '    return re.sub(r"^(get|set)_", "", name)')
s = s.replace('declared = {re.match(r"^\\S+\\s+(\\w+)\\s*\\(", line).group(1)\n'
              '                    for line in block if re.match(r"^\\S+\\s+(\\w+)\\s*\\(", line)}',
              'declared = {_com(m.group(1)) for m in\n'
              '                    (SIG.match(line) for line in block) if m}')
s = s.replace('declared = {re.match(r"^\\S+\\s+(\\w+)\\s*\\(", line).group(1)\n'
              '                    for line in block if re.match(r"^\\S+\\s+(\\w+)\\s*\\(", line)}',
              'declared = {_com(m.group(1)) for m in\n'
              '                    (SIG.match(line) for line in block) if m}')
s = s.replace('assert "ProcessID" in known, "带参成员才登记 arity"',
              'assert "GetProcessID" in known, "带参成员才登记 arity"')
p.write_text(s, encoding="utf-8")
print("  [ok] 测试解析器已归一化")
