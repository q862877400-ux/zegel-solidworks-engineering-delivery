"""★ 一次性：让 call() 看工具返回体里的成败（★ 不抛异常 ≠ 成功）。"""
from pathlib import Path

p = Path(r"D:\AI\SW\tools\tool_caller.py")
s = p.read_text(encoding="utf-8")

OLD = """        note = str(r)[:160]
        if dropped:
            note += "  ★（声明里有但底层不接的形参：%s）" % "、".join(dropped)
        return True, note"""
NEW = """        #: ★★★ 2026-10-06 **真机踩过（一定要记住）**：★ 工具层返回的是 **JSON 字符串**，
        #:   ★ 里面**自带成败** —— ★★ 而"调用没抛异常"**只说明它跑完了**，不说明它做成了 ✗
        #:   ★ 现场：★ 探针调 `extrude_boss` 时**没有先建草图**（`Sketch1` 不存在）⇒
        #:     ★ 工具返回**失败载荷**，★ 而我的 `call()` 报 **`写操作 成功`** ⇒
        #:     ★★ 于是**指纹没动**被记成 `not_detected`（= "这一类不可见"）✗✗
        #:   ★★ 那正是本规格**最不许**发生的假结论（★ 与「选不上当成能力不行」同族）✓
        #:   ⇒ ★ 修法：★ **解析返回体**，★ 只看**它自己说的成败** ✓
        text = str(r)
        payload_ok = None
        try:
            import json as _json
            obj = _json.loads(text)
            if isinstance(obj, dict):
                for key in ("ok", "success", "succeeded"):
                    if isinstance(obj.get(key), bool):
                        payload_ok = obj[key]
                        break
                if payload_ok is None and (obj.get("error") or obj.get("errors")):
                    payload_ok = False
        except Exception:                                               # noqa: BLE001
            payload_ok = None
        note = text[:160]
        if dropped:
            note += "  ★（声明里有但底层不接的形参：%s）" % "、".join(dropped)
        if payload_ok is False:
            #: ★ 工具**跑完了但说自己没成** ⇒ ★ 这**不是**"这一类不可见"，★ 而是"没调成" ✓
            return False, "★ 工具返回体说失败：%s" % note[:140]
        return True, note"""
assert OLD in s, "call() 返回块没匹配上"
s = s.replace(OLD, NEW)
p.write_text(s, encoding="utf-8")
import ast
ast.parse(s)
print("call() 已看返回体的成败")
