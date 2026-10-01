import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tools\verify_mcp_protocol_layer.py")
t = P.read_text(encoding="utf-8")

OLD = '''            props = (by_name[n].get("inputSchema") or {}).get("properties") or {}
            declared = {p.name for p in spec.params}
            missing = declared - set(props)
            extra = set(props) - declared
            chk("★ schema 参数逐条对上 · %s" % n, not missing and not extra,
                "声明=%s 协议=%s 缺=%s 多=%s" % (sorted(declared), sorted(props),
                                                sorted(missing), sorted(extra)))'''

NEW = '''            # ⚠⚠ **第一版判据错了（本轮当场发现）**：我去**顶层** `properties` 找**展平**的参数名，
            #   报「协议里只有一个 `params`」—— 但那是**设计**：
            #   每个工具统一收一个 `params` 对象（与 `server.py` 原生工具一致），
            #   **声明的参数是嵌在 `params` 的 `$ref` → `$defs.<Model>.properties` 里**。
            #   ⇒ 判据要**顺着 `$ref` 走进去**。
            schema = by_name[n].get("inputSchema") or {}
            top = schema.get("properties") or {}
            ref = ((top.get("params") or {}).get("$ref") or "")
            model_name = ref.rsplit("/", 1)[-1]
            inner = (((schema.get("$defs") or {}).get(model_name) or {}).get("properties") or {})
            declared = {p.name for p in spec.params}
            #: ⚑ 框架会**统一补**一个 `response_format`（`json`/`markdown`）—— 声明里没有它
            extra = set(inner) - declared
            missing = declared - set(inner)
            chk("★ schema 参数逐条对上（顺 `$ref` 走进去） · %s" % n,
                not missing and not extra - {"response_format"},
                "声明=%s 协议(内层)=%s 缺=%s 多=%s"
                % (sorted(declared), sorted(inner), sorted(missing), sorted(extra)))
            #: 顺带记下"框架统一补了 response_format"这件事
            if "response_format" in inner:
                ev.setdefault("framework_added", set())
                ev["framework_added"] = sorted(set(ev.get("framework_added") or []) |
                                               {"response_format"})'''

assert OLD in t, "判据锚点不符"
t = t.replace(OLD, NEW, 1)
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok 判据已改成「顺 $ref 走进去」")
