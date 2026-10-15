import json, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
f = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_hubs.py")
src = f.read_text(encoding="utf-8")
reg = json.loads(Path(r"D:\AI\SW\_raw\member_registry.json").read_text(encoding="utf-8"))
order = ["IFeatureManager","IDrawingDoc"]
L = []
L.append("# ── 来源 ─────────────────────────────────────────────────────────────")
L.append("# 仓库:   本项目自身（本任务新增的能力层）")
L.append("# 文件:   scripts/sw_hubs.py —— 本文件自身")
L.append("# 定位:   两个总入口的能力登记表 {族: {能力名: 实参个数}}。**机械生成，不手抄**。")
L.append("#         生成器 D:\\AI\\SW\\tools\\gen_member_registry.py。")
L.append("# ⚑ 编号变体（FeatureExtrusion2 / Create3rdAngleViews2 之类）已**折叠")
L.append("#   到基础名**，保留实参最多的那一条 —— **明确声明的取舍**，不是「它们等价」。")
L.append("# 取值:   原始 / I前缀 / 属性 / 方法 / 归约后能力 —— 逐族：")
for k in order:
    i = reg[k]
    L.append("#     %-20s %4d / %3d / %3d / %4d -> %3d 项" % (
        k, i["raw_members"], i["internal_dispatch"], i["property_count"],
        i["method_count"], i["distinct_capabilities"]))
L.append("# 覆盖:   后续同级定义")
L.append("# ⚠ 本组为静态照录，未在本机实测（见 AGENTS.md 铁律 2）")
L.append("# ────────────────────────────────────────────────────────────────────")
L.append("HUB_FAMILIES: tuple[str, ...] = (")
for k in order: L.append("    %r," % k)
L.append(")")
L.append("")
L.append("HUB_ARITY: dict[str, dict[str, int]] = {")
tot = 0
for k in order:
    L.append("    %r: {" % k)
    for it in reg[k]["members"]:
        L.append("        %r: %d," % (it["name"], it["arity"]))
        tot += 1
    L.append("    },")
L.append("}")
L.append("")
L.append("#: 各族的属性名（反射里是 get_/set_，**不是方法**）")
L.append("HUB_PROPERTIES: dict[str, tuple[str, ...]] = {")
for k in order:
    L.append("    %r: (" % k)
    for p in reg[k]["properties"]: L.append("        %r," % p)
    L.append("    ),")
L.append("}")
L.append("")
anchor = "\n\ndef _require(obj"
assert anchor in src
src = src.replace(anchor, "\n\n" + "\n".join(L) + anchor, 1)
f.write_text(src, encoding="utf-8")
print("已注入：%d 项能力 / %d 个族" % (tot, len(order)))
