import json, re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
res = json.loads(Path(r"D:\AI\SW\toolsets.json").read_text(encoding="utf-8"))
DOM = {
 "① 会话/文档/文件": r"document|file|open|close|save|new_|export|import|template|status|connect|rebuild",
 "② 参考几何": r"plane|axis|point|coordinate|refgeom",
 "③ 草图": r"sketch|line|circle|arc|rectang|polygon|spline|ellipse|slot|trim|offset|mirror|convert_ent|construction|fillet|chamfer|text",
 "④ 尺寸/约束/参数": r"dimension|relation|constraint|equation|global_var|design_table|driving|link_",
 "⑤ 零件特征": r"extrude|revolve|fillet|chamfer|shell|draft|rib|dome|wrap|intersect|boundary|pattern|mirror|hole|sweep|loft|body|combine|split|scale|helix|curve",
 "⑥ 曲面": r"surface|knit|thicken|delete_face|filled",
 "⑦ 钣金": r"sheet|flange|bend|unfold|fold|jog|hem|flat_pattern",
 "⑧ 焊件": r"weld|structural|gusset|end_cap|trim_weld",
 "⑨ 模具": r"mold|parting|shut_off|tooling|core|cavity",
 "⑩ 装配": r"component|mate|assembl|interference|explode|assembly_tree",
 "⑪ 工程图": r"drawing|sheet|view|annot|balloon|bom|dimension|centerline|center_mark|note|revision|hole_table|section",
 "⑫ 检查/测量/反馈": r"screenshot|mass_prop|bbox|measure|check_|analyze|inspect|geometry|view_orient|zoom|display_mode|sensor",
 "⑬ 仿真/Motion": r"simulat|motion|study|fea|cosworks|thermal|buckling|fatigue|drop|static",
 "⑭ 外观/材质/配置": r"material|appearance|color|config|display_state|background|render",
 "⑮ 宏/自动化": r"macro|vba|record|script|batch|automation",
 "⑯ 高级/专项": r"topolog|dfm|machin|cost|pdm|vault|revision|routing|pipe|harness|electrical|toolbox|dimxpert|tolerance|gdt|datum|surface_finish|draft_analys",
}
PROJS = list(res.keys())
print("%-20s %s" % ("域", " ".join("%-13s" % p[:13] for p in PROJS)))
tot = {p: 0 for p in PROJS}
for dom, rx in DOM.items():
    row = []
    for p in PROJS:
        hit = [t for t in res[p] if re.search(rx, t, re.I)]
        tot[p] += len(hit)
        row.append("%-13s" % ("%d" % len(hit) if hit else "·"))
    print("%-20s %s" % (dom, " ".join(row)))
print()
print("=== 各项目在「⑯ 高级/专项」的具体能力（护城河候选）===")
for p in PROJS:
    hit = sorted(t for t in res[p] if re.search(DOM["⑯ 高级/专项"], t, re.I))
    if hit: print("  %-14s %s" % (p, ", ".join(hit)))