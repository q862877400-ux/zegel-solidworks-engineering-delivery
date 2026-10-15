import json
from pathlib import Path

c = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(c.read_text(encoding="utf-8"))

x = next(y for y in d["capabilities"] if y["id"] == "mold_analysis")
x["level"] = "verified"
x["evidence"] = [
    "python 真机（轮 343）★ **冒烟 5/5 PASS**（★ 改前报 3/5 fail，★ 真因是**脚本的键形状假定过时**："
    "它在顶层找 4 个计数键，而实现放在 `counts` 子字典）：「含官方只读入口的键 **6/6**」·"
    "「新零件上读数都是空/0 **6 个**」· 证据 output/mold-evidence-smoke.json",
    "python 真机（轮 177，复验于 343）★ **4/4 PASS**：`IFeatureManager.MoldDraftAnalysis` ⇒ **AttributeError** · "
    "`IModelDoc2.MoldDraftAnalysis` ⇒ **能取到** · ★ **而真机回 `bool`**（★ 官方签名写的是 `Void`）· "
    "证据 output/mold-draft-analysis-owner.json",
]
x["limitations"] = [
    "★ 从 `mold_tools` **拆出**（轮 276）：★ 依据是**意图不同** —— 本族是**分析**（拔模/底切）。",
    "★★ **2026-10-01（轮 343）已真机通过**（冒烟 5/5 · 探针 4/4）。",
    "⚠ **仍未查证**：`MoldUndercutDetect` 官方是 `Void`，而 `MoldUndercutDetect2` 有 **5 个 `Col*` 颜色参数** "
    "⇒ ★ **结果是用颜色标在面上**；★ 两份官方文档**都没有 Remarks**，枚举目录里也**只有** "
    "`swPartingSurfaceMoldParmType_e` ⇒ ★ **「怎么把颜色读回来」仍是未知**（铁律 5）。",
    "⚠ **未验**：`MoldDraftAnalysis` 的**返回值语义**（★ 真机回 `bool`，而官方未给返回码枚举）"
    "⇒ ★ 本模块**原样返回、不判定成败**。",
]

y = next(z for z in d["capabilities"] if z["id"] == "mold_parting_geometry")
y["evidence"] = [
    "⚠ **仍无真机证据**：本族 4 个工具需**先选拔模方向参考**，★ 而在**未准备的分型件**上会弹框 "
    "⇒ ★ 前置得由人配合。（★ 2026-10-01 轮 343：已删去旧 evidence 里那句**已过时**的「冒烟 3/5 fail」"
    "—— ★ 那是 **`mold_analysis` 的脚本键形状**问题，与本族无关。）"
]

c.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
st = [z for z in d["capabilities"] if z.get("level") == "stitched"]
vf = [z for z in d["capabilities"] if z.get("level") == "verified"]
print("  ok · verified=%d stitched=%d" % (len(vf), len(st)))
