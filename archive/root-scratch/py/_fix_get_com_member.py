import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_connect.py")
t = P.read_text(encoding="utf-8")

OLD = '''    member = getattr(obj, attr_name)
    if args:
        return member(*args)
    try:
        return member() if callable(member) else member
    except Exception as exc:
        message = str(exc)
        if "-2147352573" in message or "找不到成员" in message or "Member not found" in message:
            return member
        raise'''

NEW = '''    member = getattr(obj, attr_name)
    if args:
        return member(*args)
    # ⚠⚠⚠ **2026-10-01（轮 143）发现本函数的一个危险设计**：
    #   下面那句"没有实参就先调一次" —— 对**有副作用**的 COM 成员，
    #   **"取"就等于"调"**！
    #   实证：`get_com_member(doc, "InsertDome")` **自己抛了**
    #   `0x8002000F`（`DISP_E_PARAMNOTOPTIONAL`，因为 `InsertDome` 有 3 个必填参数）
    #   ⇒ 说明它**真的把 `InsertDome` 调了一次**。
    #   ⇒ ★ 危险在于：**无必填参数**且有副作用的方法（如 `InsertDeleteHole()`、
    #     任何 `File*` 写盘方法）会**被"取"这个动作静默执行**。
    #   ⚠ 本函数的白名单原本只认 `找不到成员`（`0x80020005`/`-2147352573`），
    #     所以 `DISP_E_PARAMNOTOPTIONAL` **会抛出去** —— 那让"取不到"与"取到了但参数不够"
    #     看起来一样。
    #   ★ 本轮的最小修法：把 `DISP_E_PARAMNOTOPTIONAL` 也纳入"**返回成员、不调用**"。
    #     （不改成"永不调用"—— 那会动到全仓库依赖的既有语义。）
    try:
        return member() if callable(member) else member
    except Exception as exc:
        message = str(exc)
        if ("-2147352573" in message or "找不到成员" in message or "Member not found" in message
                #: `DISP_E_PARAMNOTOPTIONAL` —— 说明"它是个**需要实参的方法**"，
                #: 而不是"读不到这个成员"。
                or "-2147352561" in message or "非选择性的参数" in message
                or "Parameter not optional" in message):
            return member
        raise'''

if "危险设计" not in t:
    assert OLD in t, "get_com_member 锚点不符"
    P.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
    print("  ok get_com_member 已修（DISP_E_PARAMNOTOPTIONAL 纳入：返回成员、不调用）")
else:
    print("  已有")
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")
