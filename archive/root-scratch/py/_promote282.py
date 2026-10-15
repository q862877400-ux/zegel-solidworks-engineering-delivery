import json
from pathlib import Path

c = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(c.read_text(encoding="utf-8"))
x = next(y for y in d["capabilities"] if y["id"] == "costing_templates_and_defaults")
x["level"] = "verified"
if not x.get("verified_versions"):
    x["verified_versions"] = ["2026"]
x["evidence"] = [
    "python 真机（轮 366）★ **PASS 3/3** —— 修掉一条真 bug 后整族通过："
    "`list_costing_templates_report(cm)` ⇒ `ok=true · count=2` · "
    "`get_default_template_report(cm, 0)` 与 `(cm, 1)` ⇒ 都 `ok=true`（回了真实模板路径 "
    "`…\\lang\\chinese-simplified\\costing templates\\…`）· 证据 output/costing-templates-evidence.json",
    "python 真机（轮 366）★ **真 bug 修在一行上**：`list_costing_templates_report` 原先把 `d`"
    "（`CostingDefaults`）传给 `list_templates`，而 `GetTemplatePathnames` **挂在 `ICostManager` 上**"
    "（反射转储 `iface_sldcostingapi.txt` 的 `## ICostManager`：`GetTemplateCount(Int32)` / "
    "`GetTemplatePathnames(Int32)` 成对）⇒ 改成传 `cost_manager` 即通。"
    "⚠ COM 报的是 `<unknown>.GetTemplatePathnames`（**像"成员不存在"，其实是对象不对** —— 事实 36 的形态）。",
    "python 真机（轮 366）★ **受控实验定位**：A（只取 defaults）/ B（先取 model 再取 defaults）**都通**，"
    "★ 而工具层入口不通 ⇒ 把嫌疑缩到"工具层内部那一处传参"上。",
]
x["limitations"] = [
    "★★ **2026-10-02（轮 366）已真机 PASS 3/3**（修掉上面那条一行 bug 之后）。",
    "⚠ **仍只有 2 个模板类别**（`GetTemplateCount(0)` ⇒ `2`）—— ★ 本机 Costing 模板库只有这两个；"
    "★ `category` 的语义**官方无文档**（`Int32`，未标含义）。",
    "⚠ **`get_default_template` 要 `CostingDefaults` 对象，而 `list_templates` 要 `ICostManager`** —— "
    "★ 同一族里两个成员挂**不同接口**上（★ 本轮踩到，已修）。",
    "⚠ **反射转储里的 `get_Xxx` 是**属性 getter 的名字**，不是 pywin32 里该用的名字**："
    "真机实测 `get_LotSizeForMultibody` 等**全部**报 `<unknown>.get_Xxx`，而**去掉 `get_` 就能调**"
    "（★ 探针若手试反射名，会把好代码报成坏代码）。",
]

#: ★ 同轮顺带更正：`costing_readback` 与 `costing` 的旧限制里若有"list_templates fail"字样也一并说明
for cid in ("costing_readback", "costing"):
    y = next((z for z in d["capabilities"] if z["id"] == cid), None)
    if y is None:
        continue
    lim = list(y.get("limitations") or [])
    note = ("★ 2026-10-02（轮 366）：本族「模板清单」那条的**根因已查明并修好** —— "
            "`GetTemplatePathnames` 挂在 `ICostManager` 上（不是 `CostingDefaults`），"
            "见 `costing_templates_and_defaults` 的 evidence。")
    if not any("GetTemplatePathnames" in t for t in lim):
        lim.insert(0, note)
    y["limitations"] = lim

c.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
vf = sum(1 for z in d["capabilities"] if z.get("level") == "verified")
st = sum(1 for z in d["capabilities"] if z.get("level") == "stitched")
print("  ok · verified=%d stitched=%d" % (vf, st))
