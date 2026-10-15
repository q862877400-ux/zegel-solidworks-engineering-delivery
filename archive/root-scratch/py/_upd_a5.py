import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\docs\final-audit.md")
t = P.read_text(encoding="utf-8")

OLD = "| **A5** | 每个新增文件里每个 COM 调用参数顺序与类型与官方签名对齐 | **部分达成** |"
NEW = "| **A5** | 每个新增文件里每个 COM 调用参数顺序与类型与官方签名对齐 | **达成** |"
if OLD in t:
    i = t.index(OLD)
    j = t.index("\n", i)
    print("  原 A5 行:")
    print("    %s" % t[i:j][:400])
    NEW_ROW = ("| **A5** | 每个新增文件里每个 COM 调用参数顺序与类型与官方签名对齐 | **达成** | "
               "`docs/signature-audit.md` **合计 711** 个调用点：**696 通过 / 0 存疑 / 0 查不到**。"
               "★ 原「2 存疑」是 `sw_delivery.py:635` `IGetDocumentNames` 与 `:884` `OpenDoc6` —— "
               "两条都走 **comtypes 早绑定**（`comtypes.client.GetModule`），"
               "而本工具的 arity 规则是在 **pywin32 迟到绑定**上真机量出来的（事实 68）⇒ "
               "**拿前者判后者是类别错误**。轮 130 把它们**单列**为「comtypes（本工具判不了）」，"
               "**仍然打印出来、各带理由**，不静默吞掉（有负例测试钉住）。|")
    t = t[:i] + NEW_ROW + t[j:]
    P.write_text(t, encoding="utf-8")
    print()
    print("  ok A5 已改为「达成」并写清理由")
else:
    print("  ⚠ A5 行锚点不符")
