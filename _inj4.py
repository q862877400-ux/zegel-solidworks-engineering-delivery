import json, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
f = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_drawing_annotations.py")
src = f.read_text(encoding="utf-8")
reg = json.loads(Path(r"D:\AI\SW\_raw\member_registry.json").read_text(encoding="utf-8"))
order = ["IDisplayDimension","IAnnotation","ITableAnnotation","ISheet","IDimension","IBomTableAnnotation"]
L = []
L.append("# ── 来源 ─────────────────────────────────────────────────────────────")
L.append("# 仓库:   本项目自身（本任务新增的能力层）")
L.append("# 文件:   scripts/sw_drawing_annotations.py —— 本文件自身")
L.append("# 定位:   六族能力登记表 {族: {能力名: 实参个数}}。**机械生成，不手抄**。")
L.append("#         生成器 D:\\AI\\SW\\tools\\gen_member_registry.py。")
L.append("# ⚑ 编号成员**未折叠** —— SolidWorks 的编号不是重载，是不同版本的不同")
L.append("#   操作（见 sw_hubs.py 里 FeatureExtrusion{,2,3} 的实测），折叠会产出")
L.append("#   「名字真实但 arity 取自别的成员」的条目。")
L.append("# 取值:   原始 / I前缀 / 属性 / 方法 —— 逐族：")
for k in order:
    i = reg[k]
    L.append("#     %-22s %4d / %3d / %3d / %4d" % (
        k, i["raw_members"], i["internal_dispatch"], i["property_count"],
        i["method_count"]))
L.append("# 覆盖:   后续同级定义")
L.append("# ⚠ 本组为静态照录，未在本机实测（见 AGENTS.md 铁律 2）")
L.append("# ────────────────────────────────────────────────────────────────────")
L.append("ANNOTATION_FAMILIES: tuple[str, ...] = (")
for k in order: L.append("    %r," % k)
L.append(")")
L.append("")
L.append("ANNOTATION_ARITY: dict[str, dict[str, int]] = {")
tot = 0
for k in order:
    L.append("    %r: {" % k)
    for it in reg[k]["members"]:
        L.append("        %r: %d," % (it["name"], it["arity"])); tot += 1
    L.append("    },")
L.append("}")
L.append("")
L.append("#: 各族的属性名（反射里是 get_/set_，**不是方法**）。")
L.append("# ⚑ 本批属性占比很高（ITableAnnotation 44 属性 / 59 方法），所以**单独成表**：")
L.append("#   把属性混进方法表会导致「属性被当成零参方法调用」这类错误。")
L.append("ANNOTATION_PROPERTIES: dict[str, tuple[str, ...]] = {")
ptot = 0
for k in order:
    L.append("    %r: (" % k)
    for p in reg[k]["properties"]: L.append("        %r," % p); ptot += 1
    L.append("    ),")
L.append("}")
L.append("")
anchor = "\n\ndef _require(obj"
assert anchor in src
src = src.replace(anchor, "\n\n" + "\n".join(L) + anchor, 1)
f.write_text(src, encoding="utf-8")
print("已注入：%d 项能力 / %d 项属性 / %d 族" % (tot, ptot, len(order)))
