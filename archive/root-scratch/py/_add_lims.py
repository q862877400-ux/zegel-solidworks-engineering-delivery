import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
p = R / "capabilities.yaml"
t = p.read_text(encoding="utf-8")

#: \u2605 \u4e09\u6761\u65b0\u7684 limitations\uff08\u2605 \u800c\u6bcf\u6761\u90fd\u5199\u6e05\u4f9d\u636e\uff1a\u4e8b\u5b9e\u53f7 + evidence\uff09
#: \u2605\u2605 \u800c\u5b83\u4eec\u8981**\u63d2\u8fdb\u5bf9\u5e94\u80fd\u529b\u7684 `limitations:` \u5217\u8868\u91cc**\u3002
ADD = {
    "pattern_and_mirror": [
        "★★ **`FeatureLinearPattern*` 在 pywin32 这条后端上到不了「建成」**（★ 2026-10-03 轮 454 · 事实 369 · "
        "`output/linear-pattern-generations-evidence.json`）。★★ **三层论证**："
        "① **arity 正确的不报错**（`FeatureLinearPattern3` 是 **10** 参 · `4` 是 **20** 参 —— "
        "而按对的个数传都「接受」了）；② **选区也对**（`_select_by_id(..., \"BODYFEATURE\", mark=4)` 回 `True`，"
        "而**同族的 `circular_pattern` 用同一套选区且能成**）；③ ★★ **三代都不改几何**（包围盒一模一样）—— "
        "而阵列**必须**改变包围盒。⚠ **故不要再试**（事实 53）；★ 而它的 **arity 表**（8/9/10/20/22）"
        "已记在事实 369。★ `circular_pattern` **不受影响**（它走 `FeatureCircularPattern4` · 7 参 · 能用）。",
    ],
    "weldment_profile_and_curve": [
        "★★ **结构系统（Structure System）那条链在 pywin32 上到不了「建成」**（★ 2026-10-03 轮 441–446 · "
        "事实 356 / 360 / 361 · `output/structure-system-evidence.json`）。★★ **入口查得到**（★ 而在 "
        "**`IModelDocExtension`** 上：`CreateStructureSystemMemberData(MemberType)` ⇒ "
        "`IStructureSystemMemberFeatureData` · `CreateStructureSystem(primary[], secondary[])` ⇒ `IFeature`）—— "
        "★ **而走不通**：① `ext.CreateStructureSystem` 在**迟到绑定下取不到**（`getattr` 回 `None`）；"
        "② `SetPathSegments` 只在 `IPrimaryMemberPathSegmentFeatureData` 上，而**换接口要 QI** —— "
        "而 **pywin32 里换不了**（`QueryInterface` 报 `no interface object registered`，"
        "与「注册表 TypeLib 591 个条目里 0 个 SOLIDWORKS」吻合）。"
        "⚠ **故 `configure_member_profile` / `configure_split_member` 两条判「不做」**，"
        "★ 而理由**不是「查不到」**（★ 那已被推翻）而是「**在这条后端上到不了**」· 与**事实 47** 同族。"
        "★★ 而**完整官方序列已入库**（事实 358）⇒ **换个后端就能接着做**。",
    ],
    "selection_helpers": [
        "★ **`select_object` / `resolve_face_selector` 两条判「不做」—— 而理由是规则 3**（★ 2026-10-03 轮 452 · "
        "事实 367）。`select_object(model, obj)` **吃 COM 对象** ⇒ **没法入参数表达**；"
        "`resolve_face_selector(model, selector)` **回 `(x, y, z)` 米** ⇒ **暴露它就是暴露裸坐标** ⇒ "
        "**违反规则 3**。★ 而**同族的 `select_face_by_selector` 做了**（★ 对外参数是**选择器**、"
        "坐标只在内部用）⇒ ★★ **可复用判据**：判一个吃几何的函数能不能当工具，"
        "看它的**对外参数**是「选择器 / 具名实体」还是「坐标 / 对象」—— **而不是**看它内部用了什么。",
    ],
}


def add_under(cap_id: str, items: list) -> int:
    """★ 在 `cap_id` 那条的 `limitations:` 列表**末尾**插入 items（★ 缩进照该列表）。"""
    lines = t.splitlines() if isinstance(t, str) else []
    return 0


#: \u2605 \u6309\u884c\u5904\u7406\uff08\u2605 \u6bd4\u7eaf\u6587\u672c\u66ff\u6362\u5b89\u5168\uff1a\u80fd\u770b\u5230\u7f29\u8fdb
lines = t.splitlines()
out = []
cur_id = None
in_lim = False
lim_indent = ""
inserted: dict = {}
i = 0
while i < len(lines):
    line = lines[i]
    out.append(line)
    s = line.strip()
    if s.startswith("id:"):
        cur_id = s.split(":", 1)[1].strip()
        in_lim = False
    elif s.startswith("limitations:"):
        in_lim = True
        lim_indent = " " * (len(line) - len(line.lstrip()))
        #: \u2605 \u627e\u5230\u8be5\u5217\u8868\u7684\u672b\u5c3e\uff08\u2605 \u5373\u4e0b\u4e00\u884c\u4e0d\u518d\u662f\u540c\u7ea7 "- "  \u9879\uff09
        j = i + 1
        last = i
        while j < len(lines):
            lj = lines[j]
            if lj.strip().startswith("- ") and (len(lj) - len(lj.lstrip())) >= len(lim_indent):
                last = j
                j += 1
                #: \u2605 \u8df3\u8fc7\u8be5\u9879\u7684\u7eed\u884c
                while j < len(lines) and lines[j].strip() and \
                        (len(lines[j]) - len(lines[j].lstrip())) > len(lim_indent) and \
                        not lines[j].strip().startswith("- "):
                    j += 1
                continue
            break
        if cur_id in ADD and cur_id not in inserted:
            for it in ADD[cur_id]:
                out.append(lim_indent + "- " + it)
            inserted[cur_id] = len(ADD[cur_id])
        #: \u2605 \u628a\u672a\u8bfb\u7684\u90a3\u51e0\u884c\u4e5f\u8865\u4e0a
        for k in range(i + 1, last + 1):
            out.append(lines[k])
        i = last + 1
        in_lim = False
        continue
    i += 1

if inserted:
    p.write_text("\n".join(out) + "\n", encoding="utf-8")
    print("  已往 %s 追加 limitations" % inserted)
else:
    print("  (\u6ca1\u627e\u5230\u5bf9\u5e94\u6761\u76ee\uff0c\u672a\u6539)")
try:
    compile(Path(R / "tools" / "gen_dead_ends.py").read_text(encoding="utf-8"), "x", "exec")
except Exception:                                              # noqa: BLE001
    pass
