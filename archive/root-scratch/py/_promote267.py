import json
from pathlib import Path

c = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(c.read_text(encoding="utf-8"))
x = next(y for y in d["capabilities"] if y["id"] == "simulation_solver_options")
x["level"] = "verified"
x["evidence"] = [
    "python 真机（轮 347）★ **PASS 3/3** —— 整条路通了：`create_study` ⇒ `ok=true` · "
    "`get_options` ⇒ **`CDispatch`** · `configure_static_solver_report(study, reference_pressure=1.0)` ⇒ "
    "**`ok=true` · `changed=[\"reference_pressure\"]` · `returned={'DefinedReferencePressure': 1.0}`**"
    "（★ **设置真的生效**）· 证据 output/solver-options-evidence.json",
    "python 真机（轮 346）★ **工具层修掉一处一行之差**：`resolve_study` 原先 "
    "`next(iter(iter_studies(sw)), None)` **没解包**（★ `iter_studies` 产 `(index, study)` 元组）"
    "⇒ 把元组当 study 传下去 ⇒ ★ **所有没声明 `study_name` 的工具全中招**。"
    "★ 修后 `study` = **`CDispatch`**，三个配置入口的报错**换了层次**"
    "（★ 从无意义的 `SldWorks.Application.X` 变成有意义的「该研究类型可能不是这一族」）。",
    "python 真机（轮 345）★ **建研究的两个真实前置查清**：① 第一参必须是 **`ISldWorks`**"
    "（★ 传 `doc` ⇒ `AttributeError: <unknown>.GetAddInObject`）· ② 文档里**必须有实体**"
    "（★ 否则 `swsStudyError_e = 1`）⇒ `create_study_report` 真机 `ok=true`。",
    "python 真机（轮 273）★ `list_setter_summary`（零参）**ok=True**（9 个族 / 202 个 setter 名）· "
    "证据 output/batch37-evidence.json",
]
x["limitations"] = [
    "★ 从 `simulation_and_fea` **拆出**（2026-10-01 轮 275）：★ 依据是**它自己的真机结论**与别的仿真能力**互不相干**。",
    "★★ **2026-10-01（轮 347）已真机通过**（PASS 3/3）。★ 修了三处："
    "① `set_option` 把**设属性**写成**取或调**（事实 227 ⇒ 改用 `set_com_member`）；"
    "② `resolve_study` **少解包一层**（把 `(index, study)` 元组当 study）；"
    "③ **空 `kw` 被报成失败**（★ `bool({})` 是 `False` ⇒ 现改为 `ok=True` + `note`）。",
    "⚠ **仍未验**：`configure_frequency_solver_report` / `configure_buckling_solver_report` 在"
    "**对应类型的研究**上（★ 本轮只有 Static 研究 ⇒ 它们**正确地**报「该研究类型可能不是这一族」）"
    "⇒ ★ **它们各自的族**尚未在真机上验过。",
    "⚠ **环境前提**：★ 建研究需要 **Simulation 加载项已启用**（★ `ensure_simulation_addin` "
    "会尝试 `LoadAddIn` 真路径；★ 且**只影响当前会话**，不改注册表）。",
    "⚠ **会话健康**：★ 若报 **`0x800706BE`（远程过程调用失败）**，★ 那是**会话坏了**、不是这条路不通"
    "（★ 轮 347 实测：重连时打印「启动了新的 SolidWorks 实例」后即通过）。",
]
c.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
st = [z for z in d["capabilities"] if z.get("level") == "stitched"]
vf = [z for z in d["capabilities"] if z.get("level") == "verified"]
print("  ok · verified=%d stitched=%d" % (len(vf), len(st)))
