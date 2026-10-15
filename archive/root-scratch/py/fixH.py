import sys
from pathlib import Path
p = Path(r"D:\AI\SW\_miss3.py")
s = p.read_text(encoding="utf-8")
s = s.replace("""        known |= set(re.findall(r"['\\"]([A-Z]\\w{2,})['\\"]\\s*[,:}]", line))""",
              """        known |= set(re.findall(r"['\\"]([A-Za-z_]\\w{2,})['\\"]\\s*[,:}]", line))""")
p.write_text(s, encoding="utf-8")
print("scanner pattern updated")