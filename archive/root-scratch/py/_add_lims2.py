import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
p = R / "capabilities.yaml"
lines = p.read_text(encoding="utf-8").splitlines()

ADD = {
    "pattern_and_mirror": (
        "★★ **`FeatureLinearPattern*` 在 pywin32 这条后端上到不了「建成」**（★ 2026-10-03 轮 454 · 事实 369 · "
        "`output/linear-pattern-generations-evidence.json`）。★★ **三层论证**："
        "① **arity 正确的不报错**（`FeatureLinearPattern3` 是 **10** 参 · `4` 是 **20** 参 —— 按对的个数传都「接受」了）；"
        "② **选区也对**（`_select_by_id(..., \"BODYFEATURE\", mark=4)` 回 `True`，而**同族的 `circular_pattern` "
        "用同一套选区且能成**）；③ ★★ **三代都不改几何**（包围盒一模一样）—— 而阵列**必须**改变包围盒。"
        "⚠ **故不要再试**（事实 53）；★ 而它的 **arity 表**（8/9/10/20/22）已记在事实 369。"
        "★ `circular_pattern` **不受影响**（走 `FeatureCircularPattern4` · 7 参 · 能用）。"),
    "weldment_profile_and_curve": (
        "★★ **结构系统（Structure System）那条链在 pywin32 上到不了「建成」**（★ 2026-10-03 轮 441–446 · "
        "事实 356 / 360 / 361 · `output/structure-system-evidence.json`）。★★ **入口查得到**"
        "（而在 **`IModelDocExtension`** 上：`CreateStructureSystemMemberData(MemberType)` ⇒ "
        "`IStructureSystemMemberFeatureData` · `CreateStructureSystem(primary[], secondary[])` ⇒ `IFeature`）—— "
        "★ **而走不通**：① `ext.CreateStructureSystem` 在**迟到绑定下取不到**（`getattr` 回 `None`）；"
        "② `SetPathSegments` 只在 `IPrimaryMemberPathSegmentFeatureData` 上，而**换接口要 QI** —— "
        "而 **pywin32 里换不了**（`QueryInterface` 报 `no interface object registered`，"
        "与「注册表 TypeLib 检索 591 个条目里 0 个 SOLIDWORKS」吻合）。"
        "⚠ **故 `configure_member_profile` / `configure_split_member` 判「不做」**，"
        "★ 而理由**不是「查不到」**（那已被推翻）而是「**在这条后端上到不了**」· 与**事实 47** 同族。"
        "★★ 而**完整官方序列已入库**（事实 358）⇒ **换个后端就能接着做**。"),
    "selection_helpers": (
        "★ **`select_object` / `resolve_face_selector` 两条判「不做」—— 而理由是规则 3**（★ 2026-10-03 轮 452 · "
        "事实 367）。`select_object(model, obj)` **吃 COM 对象** ⇒ **没法入参数表达**；"
        "`resolve_face_selector(model, selector)` **回 `(x, y, z)` 米** ⇒ **暴露它就是暴露裸坐标** ⇒ **违反规则 3**。"
        "★ 而**同族的 `select_face_by_selector` 做了**（对外参数是**选择器**、坐标只在内部用）⇒ "
        "★★ **可复用判据**：判一个吃几何的函数能不能当工具，看它的**对外参数**是「选择器 / 具名实体」"
        "还是「坐标 / 对象」—— **而不是**看它内部用了什么。"),
}

inserted = {}
for cap_id, text in ADD.items():
    #: \u2605 \u627e `"id": "<cap_id>"` \u90a3\u884c
    key = json.dumps(cap_id)
    idx = None
    for i, l in enumerate(lines):
        if l.strip().startswith('"id":') and key in l:
            idx = i
            break
    if idx is None:
        print("  **\u627e\u4e0d\u5230 %s**" % cap_id)
        continue
    #: \u2605 \u4ece\u90a3\u91cc\u5f80\u4e0b\u627e `"limitations": [`
    j = None
    for k in range(idx, min(idx + 40, len(lines))):
        if '"limitations"' in lines[k]:
            j = k
            break
    if j is None:
        print("  **%s \u6ca1\u6709 limitations**" % cap_id)
        continue
    #: \u2605 \u627e\u5b83\u7684\u95ed\u5408 `]`
    close = None
    for k in range(j + 1, len(lines)):
        if lines[k].strip() == "],":
            close = k
            break
    if close is None:
        print("  **%s \u7684 limitations \u672a\u95ed\u5408**" % cap_id)
        continue
    indent = " " * (len(lines[j]) - len(lines[j].lstrip()) + 2)
    newline = indent + json.dumps(text, ensure_ascii=False) + ","
    lines.insert(close, newline)
    inserted[cap_id] = close + 1

if inserted:
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("  \u5df2\u63d2\u5165\uff1a%s" % inserted)
else:
    print("  (\u672a\u6539)")
