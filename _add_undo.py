import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
code = Path(r"D:\AI\SW\_undo_code.txt").read_text(encoding="utf-8")

#: ★ ① 追加到 sw_session.py（★ 它需要 feature_names 与 get_com_member）
sp = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_session.py")
t = sp.read_text(encoding="utf-8")
if "def undo_report" in t:
    print("  sw_session: already")
else:
    #: ★ 确保导入存在（★ 在文件首部的 import 段之后插一句 —— ★ 用最简做法：文件尾追加 + 就地 import）
    add = ("\n\n#: ★ 本模块新增入口所需的两个依赖（★ 就地 import，★ 避免动首部结构）\n"
           "from sw_connect import get_com_member  # noqa: E402\n"
           "from sw_feature_readback import feature_names  # noqa: E402\n")
    sp.write_text(t.rstrip() + add + code, encoding="utf-8")
    print("  sw_session: appended")
try:
    compile(sp.read_text(encoding="utf-8"), str(sp), "exec")
    print("  ok-compile")
except SyntaxError as e:
    print("  **错 L%s**: %s" % (e.lineno, str(e.msg)[:80]))

#: ★ ② 检查 feature_names 到底在哪个模块（★ 别猜）
import ast
for p in Path(r"C:\swprojects\sw-skill-fork\scripts").glob("*.py"):
    if p.name.startswith("sw_api_"):
        continue
    try:
        src = p.read_text(encoding="utf-8")
    except Exception:                                          # noqa: BLE001
        continue
    if "def feature_names" in src:
        print("  feature_names 定义在: %s" % p.name)
