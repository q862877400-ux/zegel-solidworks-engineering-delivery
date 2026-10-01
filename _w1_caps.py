import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(P.read_text(encoding="utf-8"))

NEW_EV = ("python tools/capture_sketch_evidence.py（**真机**，2026-10-01 轮 222 / 砌墙 W1："
          "新零件 → 画 1 条线 + 1 个圆 → **退草图** → 按名取草图对象 → 4 个读数 + 2 个负例，"
          "**verdict: pass**，证据落 output/sketch-evidence.json）"
          "—— ★ 这一步是**挂成 MCP 工具之后**的验证：走的是工具真实路径（"
          "import tool_specs_batch18._sketch_args），不是只调底层函数。"
          "★ 它当场抓到一个只有真机能暴露的 bug：草图关闭时 sw_part.current_sketch_name "
          "回**英文 fallback**「Sketch1」，而中文 UI 下真名是「草图1」⇒ 新加 sw_sketch.resolve_sketch "
          "（中英文候选名 → 特征树兜底 → 抛错）修掉。")

n = 0
for c in d["capabilities"]:
    if c.get("id") == "sketch_query":
        ev = c.setdefault("evidence", [])
        if not any("capture_sketch_evidence" in str(x) for x in ev):
            ev.append(NEW_EV)
            n += 1
        #: ★ 本条目的"限制"要补一条与本轮直接相关的（工具层的名字问题）
        lim = c.setdefault("limitations", [])
        NOTE = ("★ 2026-10-01 轮 222（挂成工具时）补记：**草图已关闭**时 "
                "`IModelDoc2.GetActiveSketch2` 与 `ISketchManager.ActiveSketch` **都返回 None** "
                "（真机探针 tools/probe_sketch_object_routes.py）⇒ 取草图对象**只能按名取**；"
                "而按名取要先解决**名字随 UI 语言变**的问题（中文 UI 是「草图1」）"
                "⇒ 工具层统一走 `sw_sketch.resolve_sketch`。")
        if not any("resolve_sketch" in str(x) for x in lim):
            lim.append(NOTE)

assert n == 1, "没找到或重复追加 sketch_query（n=%d）" % n
P.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("  ✓ sketch_query 的 evidence 追加 1 条 · limitations 追加 1 条")
d2 = json.loads(P.read_text(encoding="utf-8"))
for c in d2["capabilities"]:
    if c.get("id") == "sketch_query":
        print("    evidence 条数: %d" % len(c["evidence"]))
        print("    limitations 条数: %d" % len(c["limitations"]))
