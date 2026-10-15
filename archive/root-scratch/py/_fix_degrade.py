"""★ 一次性：把"读不出 ⇒ 拒绝"改成"**降级到标题路**并记明用的哪条"。"""
from pathlib import Path

p = Path(r"D:\AI\SW\tools\session_verdict.py")
s = p.read_text(encoding="utf-8")

OLD = """        problem = str((probe.get("snapshot") or {}).get("readback_problem") or "")
        if not docs and problem:
            return {
                "ok": False, "path_used": path, "documents": [], "ours": [], "foreign": [],
                "unsaved": [], "unsaved_unknown": 0,
                "why": "★★ 这条路**读不出已打开的文档** ⇒ 拒绝放行（★ 读不到 ≠ 没有）：%s" % problem,
            }"""
NEW = """        problem = str((probe.get("snapshot") or {}).get("readback_problem") or "")
        if not docs and problem:
            #: ★★★ 2026-10-06 **真机查出的静默漏洞 + 我随后的过度纠正**（两个都记下来）：
            #:   ★ 漏洞：★ SolidWorks 明明开着文档，而 COM 路的 `GetDocuments` 返回**空** ⇒
            #:     `count=None · 文档数=0`，★ 而当时的裁决**照样放行** ✗（★ 门禁瞎着却报"干净"）
            #:   ★ 过度纠正：★ 我随后改成"读不出就**拒绝**" ⇒ ★★ 结果**会话干净时也拒绝** ⇒
            #:     ★ **门禁变成了路障**（★ 与上一轮 `sandbox_before` 那次同族）✗
            #:   ⇒ ★★ 正解：★ **降级到另一条探路**，★ 并把"用的是哪条"如实记进 `path_used`，
            #:     ★ 同时把 COM 路的失败原因写进 `why` —— ★ 于是**既不瞎、也不堵** ✓
            tried_paths.append(path)
            continue"""
assert OLD in s, "读不出分支没匹配上"
s = s.replace(OLD, NEW)

#: ★ 需要在循环前备一个"试过哪些路"的名单，并在最终返回里说清
s = s.replace("""    order = ["com", "title"] if prefer == "com" else ["title"]
    tried: list = []""",
"""    order = ["com", "title"] if prefer == "com" else ["title"]
    tried: list = []
    #: ★ 因"读不出"而降级掉的那些路（★ 记进返回值，免得读者以为只试了一条）✓
    tried_paths: list = []""")

OLD2 = """    return {"ok": False, "path_used": "", "documents": [], "ours": [], "foreign": [],
            "unsaved": [], "unsaved_unknown": 0,
            "why": "★★ 两条探路都探不通（试过 %s）⇒ ★ 按铁律 5 记「查不到」并**停下问人**，"
                   "★ 不许当成「会话是干净的」" % "、".join(tried)}"""
NEW2 = """    return {"ok": False, "path_used": "", "documents": [], "ours": [], "foreign": [],
            "unsaved": [], "unsaved_unknown": 0, "tried_paths": tried_paths,
            "why": "★★ **所有探路都读不出已打开的文档**（试过 %s；其中因读不出而降级的有 %s）⇒ "
                   "★ 按铁律 5 记「查不到」并**停下问人**，★ **不许当成「会话是干净的」**"
                   % ("、".join(tried), "、".join(tried_paths) or "无")}"""
assert OLD2 in s, "最终返回块没匹配上"
s = s.replace(OLD2, NEW2)

#: ★ 成功返回里也带上 tried_paths
s = s.replace('''            "unsaved_unknown": sum(1 for d in docs if (d or {}).get("dirty") is None),''',
              '''            "unsaved_unknown": sum(1 for d in docs if (d or {}).get("dirty") is None),
            "tried_paths": tried_paths,''')

p.write_text(s, encoding="utf-8")
import ast
ast.parse(s)
print("已改成「降级到标题路并记明路径」")
