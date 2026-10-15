import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_export.py")
t = P.read_text(encoding="utf-8")

OLD = '''    code = get_com_member(
        get_com_member(model, "Extension"), "SaveAs3",
        str(p), 0, SW_SAVE_AS_SILENT if silent else 0)
    if code not in (0, None) and code != 0:'''
NEW = '''    #: ⚠⚠ **实测（轮 147）**：反射里那个 **3 参**重载
    #: `Int32 SaveAs3(String, Int32, Int32)` 在 **pywin32 迟到绑定下报
    #: `0x8002000F`（`DISP_E_PARAMNOTOPTIONAL`，中文「非选择性的参数」）**
    #: —— 说明解析到的是 **7 参**那个（末两个 `out Int32`）。
    #: ⇒ 必须按 **7 参**调，并用本模块既有的 `out_i4()` 给出参占位
    #:   （事实 12 / 68 那一族；`sw_connect.out_i4` 就是为此存在的）。
    #: ★ 返回也从 `Int32` 变成 **`Boolean`** ⇒ 判据随之改变。
    ok = get_com_member(
        get_com_member(model, "Extension"), "SaveAs3",
        str(p), 0, SW_SAVE_AS_SILENT if silent else 0,
        None, None, out_i4(), out_i4())
    if ok is False:'''
assert OLD in t, "SaveAs3 调用锚点不符"
t = t.replace(OLD, NEW, 1)

#: 补 `out_i4` 的导入
IMP_OLD = "    from .sw_connect import get_com_member"
IMP_NEW = "    from .sw_connect import get_com_member, out_i4"
t = t.replace(IMP_OLD, IMP_NEW, 1)
t = t.replace("    from sw_connect import get_com_member\n",
              "    from sw_connect import get_com_member, out_i4\n", 1)
#: 收敛兜底：若两条导入路径都没匹配上，就找任意一处
if "out_i4" not in t.split("def ")[0]:
    idx = t.find("from .sw_connect import")
    if idx >= 0:
        j = t.index("\n", idx)
        t = t[:j] + "\n    from .sw_connect import out_i4" + t[j:]
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok 已改成 7 参 + out_i4()")
for i, l in enumerate(t.splitlines()[:60], 1):
    if "sw_connect import" in l:
        print("     L%-4d %s" % (i, l[:92]))
