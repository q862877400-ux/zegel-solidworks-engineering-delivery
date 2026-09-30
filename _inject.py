import json, re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
f = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_assembly_doc.py")
src = f.read_text(encoding="utf-8")
reg = json.loads(Path(r"D:\AI\SW\_raw\member_registry.json").read_text(encoding="utf-8"))
info = reg["IAssemblyDoc"]
lines = []
lines.append("# ── 来源 ─────────────────────────────────────────────────────────────")
lines.append("# 仓库:   本项目自身（本任务新增的能力层）")
lines.append("# 文件:   scripts/sw_assembly_doc.py —— 本文件自身")
lines.append("# 定位:   IAssemblyDoc 能力登记表：{能力名: 实参个数}。**机械生成，不手抄**。")
lines.append("#         生成器 D:\\AI\\SW\\tools\\gen_member_registry.py，")
lines.append("#         对 IAssemblyDoc 段的**逐行解析**结果。")
lines.append("# ⚑ 编号变体（AddMate2 / AddMate3 …）已**折叠到基础名**，")
lines.append("#   保留实参最多的那一条 —— 这是**明确声明的取舍**，不是「它们等价」。")
lines.append("# 取值:   原始成员 %d / I 前缀 %d / 属性 %d / 方法 %d -> 归约后 **%d 项**" % (
    info["raw_members"], info["internal_dispatch"], info["property_count"],
    info["method_count"], info["distinct_capabilities"]))
lines.append("# 覆盖:   后续同级定义")
lines.append("# ⚠ 本组为静态照录，未在本机实测（见 AGENTS.md 铁律 2）")
lines.append("# ────────────────────────────────────────────────────────────────────")
lines.append("ASSEMBLY_DOC_ARITY: dict[str, int] = {")
for it in info["members"]:
    lines.append("    %r: %d," % (it["name"], it["arity"]))
lines.append("}")
lines.append("")
lines.append("#: IAssemblyDoc 上的属性名（反射里是 get_/set_，**不是方法**）")
lines.append("ASSEMBLY_DOC_PROPERTIES: tuple[str, ...] = (")
for p in info["properties"]:
    lines.append("    %r," % p)
lines.append(")")
lines.append("")
anchor = "\n\ndef _require(doc):"
assert anchor in src, "锚点没找到"
src = src.replace(anchor, "\n\n" + "\n".join(lines) + anchor, 1)
f.write_text(src, encoding="utf-8")
print("已注入：能力 %d 项 / 属性 %d 项" % (len(info["members"]), len(info["properties"])))
