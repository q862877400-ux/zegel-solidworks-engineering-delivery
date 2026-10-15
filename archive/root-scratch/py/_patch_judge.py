import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"C:\swprojects\sw-skill-fork\tools\judge_naked_batch2.py")
t = p.read_text(encoding="utf-8")

OLD = """        verdict = ("已有（★ 有实现入口）" if (hits and mem) else
                   "★ 需人工核（有入口而同名 COM 成员为空）" if hits else "**真缺**（两层都无）")
        rows.append({"gap": gap, "funcs": hits[:6], "com_members": mem[:8],
                     "verdict": verdict})
        print("  %-22s ⇒ %s" % (gap, verdict))
        print("      函数: %s" % (", ".join(hits[:5]) or "—"))
        print("      COM : %s" % (", ".join(mem[:5]) or "—"))"""

NEW = """        #: ★★★★ 2026-10-03（轮 394）**第三层证据：枚举常量与文档串** ——
        #:   ★ 前两层（函数名 + COM 成员）**看不到"参数取值"** ⇒ 真例：
        #:   `solidworks_entities_on_body(kind="VERTEX")` 的函数名里**没有 vertex**
        #:   ⇒ 两层都判"无" ⇒ ★★ **误判成"有原语无工具"**（★ 而它**早就是工具**了）。
        #:   ⇒ 所以还要搜 **枚举常量名**（如 `ENTITY_KINDS`）与 **工具文档串里的取值**。
        enumish: list[str] = []
        for p2 in list((ROOT / "scripts").glob("*.py")) + list((ROOT / "mcp-server").glob("*.py")):
            if p2.name.startswith("sw_api_"):
                continue
            try:
                src2 = p2.read_text(encoding="utf-8")
            except Exception:                                   # noqa: BLE001
                continue
            for m2 in re.finditer(r'"([A-Z_]{3,})"', src2):
                name2 = m2.group(1)
                if any(k.lower() in name2.lower() for k in keys):
                    enumish.append("%s:%s" % (p2.name, name2))
            for m2 in re.finditer(r'([A-Za-z_]*KINDS[A-Za-z_]*)\\s*=\\s*\\{([^}]{0,400})\\}', src2):
                body2 = m2.group(2)
                if any(k.upper() in body2.upper() for k in keys):
                    enumish.append("%s:%s" % (p2.name, m2.group(1)))
        enumish = sorted(set(enumish))
        verdict = ("已有（★ 有实现入口）" if (hits and mem) else
                   "已有（★ 由**枚举取值/文档串**佐证 —— 第三层）" if enumish else
                   "★ 需人工核（有入口而同名 COM 成员为空）" if hits else "**真缺**（三层都无）")
        rows.append({"gap": gap, "funcs": hits[:6], "com_members": mem[:8],
                     "enum_or_doc": enumish[:6], "verdict": verdict})
        print("  %-22s ⇒ %s" % (gap, verdict))
        print("      函数: %s" % (", ".join(hits[:5]) or "—"))
        print("      COM : %s" % (", ".join(mem[:5]) or "—"))
        if enumish:
            print("      枚举/文档: %s" % (", ".join(enumish[:4])))"""

if "第三层证据" not in t:
    t = t.replace(OLD, NEW, 1)
    p.write_text(t, encoding="utf-8")
    print("  已加第三层证据")
try:
    compile(p.read_text(encoding="utf-8"), str(p), "exec")
    print("  ok-compile")
except SyntaxError as e:
    print("  **错 L%s**: %s" % (e.lineno, str(e.msg)[:80]))
