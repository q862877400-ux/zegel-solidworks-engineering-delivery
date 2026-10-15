import json
from pathlib import Path

c = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(c.read_text(encoding="utf-8"))
x = next(y for y in d["capabilities"] if y["id"] == "simulation_load_family_breadth")
x["level"] = "verified"
x["evidence"] = [
    "python 真机（轮 349）★ **PASS 5/5** —— **三类荷载全通 + 回读载荷数 = 3**："
    "`add_pressure` ⇒ `ok` · `add_force` ⇒ `ok` · `add_gravity` ⇒ `ok`（都是 `<COMObject>`）· "
    "★ `LoadsAndRestraintsManager.Count` ⇒ **3**（★ 规则 6 的回读：三个荷载**真的加进去了**）· "
    "证据 output/loadfamily-evidence.json",
    "python 真机（轮 348/349）★ **两处通用修复（都在能力层 `_check`，一处 ⇒ 整批受益）**："
    "① **末尾 `ByRef ErrorCode` 统一补 `out_i4()`**（★ 缺它 ⇒ `DISP_E_PARAMNOTOPTIONAL`"
    "「非选择性的参数」）；② **第 3 参 `RefGeom` 裸传 `None` ⇒ 换成空 Dispatch 参数包**"
    "（★ 裸 `None` ⇒ `com_error(-2147352571, '类型不匹配', None, 3)`）。"
    "★ 两处都**只对已从官方声明核过的成员**生效（★ 白名单，★ 表外不乱补 —— 铁律 5）。",
    "python 真机（轮 245 的历史发现，本批兑现）★ `RegGeom`/`RefGeom` **不能裸传 `None`** —— "
    "★ 而那时**只修了 `add_torque`，`add_force` 漏了**（★ 本轮补上）。",
    "★ **静态那一半是绿的**：`all_specs()` 出现这 4 个工具 · `scripts/check_param_binding.py` **PASS**。",
]
x["limitations"] = [
    "★★ **2026-10-01（轮 349）已真机通过**（PASS 5/5：pressure / force / gravity + 回读计数 3）。",
    "⚠ **仍未验**：`add_centrifugal_force`（★ 离心力）与 `Add{Bearing,Bolt,EdgeWeld,Elastic,Link,Pin}"
    "**连接器**族 —— ★ 它们的官方声明形态各异（★ `AddGravity` 那种**单数 `DispEntity`** 就是例子）"
    "⇒ ★ **要逐个读声明再验**，不能假定与 pressure/force 同形。",
    "⚠ **`AddGravity` 的第 1 参是单数**（`ByVal DispEntity As Object`）⇒ ★ **传数组会报位置 1 的类型不匹配**"
    "（★ 轮 349 实测）—— ★ 本能力层**如实按签名转达**，★ 调用方要给单数。",
    "⚠ **`RefGeom` 的语义**：★ 官方明写「**valid only if** `NRestraintType` is"
    " `swsRestraintTypeReferenceGeometry`」⇒ ★ 其余类型传空 Dispatch 是对的。",
]
c.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
st = [z for z in d["capabilities"] if z.get("level") == "stitched"]
vf = [z for z in d["capabilities"] if z.get("level") == "verified"]
print("  ok · verified=%d stitched=%d" % (len(vf), len(st)))
