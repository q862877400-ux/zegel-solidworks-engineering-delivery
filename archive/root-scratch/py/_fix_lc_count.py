import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"C:\swprojects\sw-skill-fork\tools\prove_link_connector_vertex.py")
t = p.read_text(encoding="utf-8")

OLD = """            def count():
                try:
                    return len(list(get_com_member(lm, "GetLoadsAndRestraints") or []))
                except Exception:                              # noqa: BLE001
                    return -1"""
NEW = """            def count():
                #: \u2605\u2605\u2605 2026-10-03\uff08\u8f6e 457\uff09**\u8bfb\u6570\u4e09\u6761\u5e76\u5217** \u2014\u2014
                #:   \u2605 \u4e0a\u4e00\u7248\u53ea\u7528 `GetLoadsAndRestraints`\uff0c\u2605 \u800c\u5b83**\u56de -1**\uff08\u2605 \u800c\u4e0d\u662f\u62a5\u9519\uff09\u26a0
                #:   \u2605\u2605 \u800c\u300c\u5efa\u6210\u6ca1\u6709\u300d**\u73b0\u5728\u8bfb\u4e0d\u51fa\u6765** \u21d2 \u2605 \u6545**\u628a\u4e09\u6761\u8bfb\u6570\u90fd\u62a5\u51fa\u6765**\uff1a
                #:     \u2460 `Count`\uff08\u2605 \u672c\u4ed3\u65e7\u5305\u88c5\u7528\u7684 \u00b7 \u2605\u2605 \u800c\u4e8b\u5b9e\u91cc\u8bb0\u8fc7\u5b83**\u95f4\u6b47\u6027\u4e0d\u7a33**\uff09
                #:     \u2461 `GetLoadsAndRestraints` \u7684\u957f\u5ea6\uff08\u2605 \u800c**\u62a5\u9519\u539f\u6587**\uff09
                #:     \u2462 \u2605**\u7279\u5f81\u6811\u540d\u5b57\u589e\u91cf**\uff08\u2605 \u8fde\u63a5\u4ef6\u53ef\u80fd**\u4e0d\u662f\u7279\u5f81**\uff0c\u2605 \u800c\u90a3\u4e5f\u8be5\u770b\uff09
                out = {}
                try:
                    v = get_com_member(lm, "Count")
                    out["count"] = int(v) if v is not None else None
                except Exception as exc:                       # noqa: BLE001
                    out["count_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:70])
                try:
                    arr = get_com_member(lm, "GetLoadsAndRestraints")
                    out["lar_len"] = len(list(arr or []))
                except Exception as exc:                       # noqa: BLE001
                    out["lar_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:90])
                try:
                    from scripts.sw_feature_readback import feature_names as _fn
                    out["tree"] = len(list(_fn(doc)))
                except Exception as exc:                       # noqa: BLE001
                    out["tree_err"] = str(exc)[:60]
                return out"""
if "读数三条并列" not in t:
    t = t.replace(OLD, NEW, 1)
    #: ★ 而那两个用 count() 的地方要改成取 count 那一条
    t = t.replace("""                rec["count"] = [before, count()]""",
                  """                after = count()
                rec["before"] = before
                rec["after"] = after""")
    t = t.replace("""            ev["any_built"] = any((t.get("count") or [0, 0])[1] > (t.get("count") or [0, 0])[0]
                                  for t in ev["trials"])""",
                  """            def _n(d, key="count"):
                v = (d or {}).get(key)
                return v if isinstance(v, int) else -1
            ev["any_built"] = any(_n(t.get("after")) > _n(t.get("before")) for t in ev["trials"])""")
    p.write_text(t, encoding="utf-8")
    print("  已把读数改成三条并列")
try:
    compile(t, str(p), "exec")
    print("  ok-compile")
except SyntaxError as e:
    print("  **错 L%s**: %s" % (e.lineno, str(e.msg)[:74]))
