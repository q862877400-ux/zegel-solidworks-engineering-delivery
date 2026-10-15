"""★ 一次性：修被补丁弄坏的缩进 —— 重写 main() 的普查循环。"""
from pathlib import Path

p = Path(r"D:\AI\SW\tools\survive_sweep.py")
s = p.read_text(encoding="utf-8")

start = s.index("    rows = []\n")
end = s.index("    counts: dict = {}")
NEW = '''    rows = []
    for req in sorted(by_requires):
        group = by_requires[req]
        print("\\n★ ── `requires=%s` 组：%d 个（★ **只建一次状态**，★ 写工具后重建）──"
              % (req, len(group)))
        model, why_state = build_state(sw, req)
        if model is None and req != "app":
            #: ★ 建不出宿主 ⇒ 整组**如实记未判定**（★ 不许当成通过）✓
            for _n in group:
                rows.append({"tool": _n, "verdict": "undecided", "requires": req,
                             "writer_ok": True, "why": why_state})
            print("   ★ 整组跳过：%s" % why_state)
            continue
        #: ★★ 组内**连着调**；★ **写工具之后重建状态**（★ 那是"副本重载"）✓
        #:   ★★ 我第一版把 `before = …` 那段**写在了组循环外面** ⇒ 每组只有**最后一个**
        #:     工具被处理（★ 真机现象：47 个只出 **7 行** —— ★ 正好等于组数）✗
        for name in group:
            decl = table.get(name) or {}
            if decl.get("writes"):
                model, why_state = build_state(sw, req)
                if model is None and req != "app":
                    rows.append({"tool": name, "verdict": "undecided", "requires": req,
                                 "writer_ok": True, "why": "★ 重建状态失败：%s" % why_state})
                    continue
            before = FP.read(model, sw)
            #: ★★ 按声明**合成实参**（★ 真机证明 12/17 的失败只是"没给参数"）✓
            spec_entry = tool_caller._specs().get(name)
            extra = synth_args(spec_entry[0]) if spec_entry else {}
            ok, note = tool_caller.call(
                name, inject_objects={"model": model, "sw": sw},
                **{k: v for k, v in extra.items()
                   if k not in ("model", "sw", "asm_model", "view", "sldworks",
                                "doc", "study")})
            after = FP.read(model, sw)
            diff = FP.compare_detailed(before, after)
            verdict = classify(table[name].get("writes"),
                               {"changed": diff["changed"], "unknown": diff["unknown"]},
                               bool(before.get("usable")) and bool(after.get("usable")),
                               call_ok=bool(ok))
            rows.append({
                "tool": name, "verdict": verdict, "writer_ok": ok, "requires": req,
                "call_note": str(note)[:120],
                "declared_writes": table[name].get("writes"),
                "changed_classes": [c["class"] for c in diff["changed"]],
                "unknown_classes": [c["class"] for c in diff["unknown"]],
            })
            print("   %-46s %-13s 变了=%s" % (name, verdict,
                                             rows[-1]["changed_classes"] or "无"))

'''
s = s[:start] + NEW + s[end:]
p.write_text(s, encoding="utf-8")
import ast
ast.parse(s)
print("普查循环已重写（★ 修掉「每组只处理最后一个」的缩进错）")
