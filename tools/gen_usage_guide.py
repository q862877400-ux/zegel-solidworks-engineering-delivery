#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 docs/usage-guide.md —— 「某个功能该看哪个官方示例、对应本仓库哪个函数」。

与 capability-matrix.md 的分工
-----------------------------
  capability-matrix.md 回答「有哪些成员、参数什么顺序」  —— 接口清单
  usage-guide.md       回答「这件事官方怎么用」        —— 使用指南
后者依赖 C:\\swapi\\examples 的 2,839 个官方示例，此前**一次都没用过**
（AGENTS.md §四 4.1 明写「★ Example 页比方法页有用 10 倍」）。

数据源：
  _raw/example_domain_index.json   —— 由 index_examples2.py 按「示例实际调用的
                                     API 成员」归到 14 个功能域，输出多标签。
  本模块维护的 DOMAIN_MODULES      —— 域 → 本仓库对应模块/函数。

⚠ 只读文件与拼装文本，不执行任何示例代码、不连接 SolidWorks
  （见 AGENTS.md 铁律 2）。
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/gen_usage_guide.py
# 定位:   生成 docs/usage-guide.md —— 「某个功能该看哪个官方示例、对应本仓库哪个函数」。
# 官方依据: 官方源 `C:\swapi\types\**`（★ 逐条见文件内引用）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
from pathlib import Path


#: ★ 本仓库根（★ 2026-10-03 合并后自定位）
_ROOT_S = str(Path(__file__).resolve().parents[1])
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001
        pass

INDEX = Path(Path(__file__).resolve().parents[1] / "_raw" / "example_domain_index.json")
OUT = Path(r"" + _ROOT_S + r"\docs\usage-guide.md")

#: 域 → 本仓库对应实现。逐条人工核对过，不是自动匹配。
DOMAIN_MODULES: dict[str, str] = {
    "应用与会话": "`scripts/sw_connect.py`（连接/模板/凭据）、`sw_session.py`、`sw_preflight.py`、"
    "`sw_addin_host.py`（Add-in 宿主）、`sw_macro_guard.py`",
    "草图": "`scripts/sw_part.py`（草图实体与约束）、`subskills/solidworks-threaded-holes`",
    "零件特征": "`scripts/sw_part.py`（extrude / revolve / fillet / chamfer / pattern / rib）、"
    "`scripts/sw_gear.py`",
    "孔与螺纹": "`scripts/sw_hole_features.py`、`subskills/solidworks-threaded-holes`",
    "钣金": "`scripts/sw_sheet_metal.py` —— 5 个特征："
    "`create_base_flange` / `create_one_bend` / `create_edge_flange` / "
    "`create_swept_flange` / `create_gusset` / `create_draft`",
    "焊件": "`scripts/sw_weldment.py`",
    "曲面": "`scripts/sw_surface.py` —— 19 个 `IModeler.Create*Surface` 登记，"
    "14 个薄封装；`advanced_surface_ocp.py`（OCP 路线，非原生）",
    "装配": "`scripts/sw_assembly.py`",
    "工程图": "`subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py`"
    "（2033 行 / 53 函数）、`scripts/drawing_spec.py`",
    "几何与拓扑": "`scripts/sw_review.py`、`sw_appearance.py`、`advanced_geometry*.py`",
    "质量属性与导出": "`scripts/sw_export.py`、`sw_delivery.py`",
    "配置·材料·自定义属性": "`scripts/sw_document_data.py`、`sw_appearance.py`",
    "仿真(需许可证)": "`scripts/sw_simulation.py` —— 入口链 / 研究 / 载荷夹具 / 求解 / 证据回读",
    "路由/Composer/PDM": "**无**（见 §未覆盖）",
}

#: 域 → 该域必须先走的「前置步骤」。空字符串表示无特殊前置。
DOMAIN_PREREQUISITES: dict[str, str] = {
    "钣金": "**必须先有基体法兰**（`swFmBaseFlange`）—— 官方 `Create_Swept_Flange_Example_VBNET` "
    "第 53 行先调 `InsertSheetMetalBaseFlange2` 再建扫掠法兰。",
    "工程图": "**必须先有已建好的工程图文档**；视图类接口挂在 `IDrawingDoc` 上，"
    "按名取页用参数化属性 `Sheet`（官方 getter 为 `get_Sheet(String)`，"
    "**不是** `GetSheet`）。",
    "仿真(需许可证)": "**必须先加载 Simulation 加载项**并取到 `CosmosWorks`（挂在 `ICwAddincallback` 上，"
    "属性名首字母大写）。",
}


def main() -> int:
    if not INDEX.exists():
        print(f"[FATAL] 找不到示例索引: {INDEX}", file=sys.stderr)
        return 2
    data = json.loads(INDEX.read_text(encoding="utf-8"))
    by_domain: dict[str, list[dict]] = data["by_domain"]
    total = data["total"]

    strong_count = {
        d: len([x for x in items if x.get("weight", 0) > 0])
        for d, items in by_domain.items()
    }

    L: list[str] = []
    L.append("# 官方使用指南（usage-guide）")
    L.append("")
    L.append(f"> 生成日期：2026-09-29 · 示例总数 **{total}**")
    L.append(f"> 官方示例来源：`C:\\swapi\\examples\\`（`{total}` 个）")
    L.append(
        "> 归类依据：**解析示例代码块里实际调用的 API 成员**，"
        "经反射清单反查宿主接口再映射到功能域 —— 不是按标题猜测。"
    )
    L.append(">")
    L.append("> **本文件与 `capability-matrix.md` 的分工**：")
    L.append("> - `capability-matrix.md` = 有哪些成员、参数什么顺序（**接口清单**）")
    L.append("> - `usage-guide.md` = 这件事**官方怎么用**（**使用指南**）")
    L.append(">")
    L.append(
        "> **本轮全部内容由静态解析生成，未启动 SolidWorks、未执行任何示例代码。**"
    )
    L.append("")
    L.append("---")
    L.append("")
    L.append("## 一分钟索引：14 个域的官方示例存量")
    L.append("")
    L.append("| # | 功能域 | 官方示例（强相关） | 本仓库实现 |")
    L.append("|---|---|---|---|")
    order = [
        "应用与会话",
        "草图",
        "零件特征",
        "孔与螺纹",
        "钣金",
        "焊件",
        "曲面",
        "装配",
        "工程图",
        "几何与拓扑",
        "质量属性与导出",
        "配置·材料·自定义属性",
        "仿真(需许可证)",
        "路由/Composer/PDM",
    ]
    for i, d in enumerate(order, 1):
        n = strong_count.get(d, 0)
        mods = DOMAIN_MODULES.get(d, "—")
        mark = " ⚠" if n == 0 else ""
        L.append(f"| {i} | {d}{mark} | **{n}** | {mods} |")
    L.append("")
    L.append(
        "> **多标签说明**：一个示例天然横跨多个域（`Select4` 几乎每个示例都调，"
        "`GetAnnotation` 三个域都有）。故本表按「该域被该示例调用的成员数」加权统计，"
        "同一示例会在多个域下出现。"
    )
    L.append("")

    # —— 逐域展开
    L.append("---")
    L.append("")
    L.append("## 逐域明细")
    L.append("")
    for d in order:
        items = by_domain.get(d, [])
        strong = sorted(
            [x for x in items if x.get("weight", 0) > 0],
            key=lambda x: (-x["weight"], x["file"]),
        )
        L.append(f"### {d}")
        L.append("")
        L.append(f"- **官方示例（强相关）**：{len(strong)} 个")
        L.append(f"- **本仓库实现**：{DOMAIN_MODULES.get(d, '—')}")
        pre = DOMAIN_PREREQUISITES.get(d)
        if pre:
            L.append(f"- ⚠ **前置**：{pre}")
        L.append("")
        if not strong:
            L.append(
                "> ⚠ **该域在 `C:\\swapi\\examples` 中没有任何示例。**"
                "官方示例集只覆盖 sldworks 等 12 个程序集，"
                "而该域对应的程序集（cosworks / SWRoutingLib / sldcostingapi）"
                "**不在收录范围内** —— 这与 `capability-matrix.md` 记录的"
                "「两套官方源同时失效」是同一个根因。"
            )
            L.append("")
            continue
        L.append("| 命中 | 语言 | 官方示例 | 关键成员 |")
        L.append("|---|---|---|---|")
        for it in strong[:25]:
            name = it["file"][:-3]
            mem = ", ".join(f"`{m}`" for m in it["types"][:6])
            L.append(f"| {it['weight']} | {it['lang']} | `{name}` | {mem} |")
        if len(strong) > 25:
            L.append(
                f"| … | | *其余 {len(strong) - 25} 个见* `_raw/examples_by_domain.txt` | |"
            )
        L.append("")

    # —— 未覆盖
    # —— 路线专题
    L.append("---")
    L.append("")
    L.append("## 专题 · 域 7 曲面的两条互补路线（读官方示例才看得出来）")
    L.append("")
    L.append("曲面域的官方示例几乎全部演示**路线 B**，而脚本能直接调的只有**路线 A**。")
    L.append("只查接口清单会漏掉这个区分，故单列。")
    L.append("")
    L.append("### 路线 A · 脚本直接造几何曲面")
    L.append("")
    L.append("`ISldWorks.GetModeler()` → `IModeler` 的 19 个非指针 `Create*Surface`")
    L.append("（平面 / 圆柱 / 球 / 圆锥 / 圆环 / 偏置 / 拉伸 / 旋转 / 直纹 / 扫掠 /")
    L.append("B 样条 / Coons / 加厚 / Loft / 由边成面）。")
    L.append("")
    L.append("**本仓库实现**：`scripts/sw_surface.py`")
    L.append("")
    L.append("### 路线 B · 界面创建 + 脚本参数化")
    L.append("")
    L.append("```vbnet")
    L.append(
        "swFeat = (Feature)swFeatureMgr.PostTrimSurface(true)          ' 唯一有脚本入口的"
    )
    L.append("surfTrimFeatData = (SurfaceTrimFeatureData)swFeat.GetDefinition()")
    L.append("surfTrimFeatData.AccessSelections(swModel, Nothing)")
    L.append("... 读 / 改属性 ...")
    L.append("surfTrimFeatData.ReleaseSelectionAccess()")
    L.append("```")
    L.append("")
    L.append("Radiate / Planar / Extend / Knit / Fill 等**没有脚本创建入口**——")
    L.append(
        "官方示例一律是「用户在界面里 Insert ▸ Surface 建好，脚本再用 `GetDefinition()` 取回参数化」。"
    )
    L.append("")
    L.append(
        "依据：扫描 `IFeatureManager` 全部 263 个方法，曲面类 `Post*` **只有** `PostTrimSurface` 一个。"
    )
    L.append("")
    L.append(
        "> ⚑ **更正记录**：本项目早前依据「无任何接口返回 `ISurface*FeatureData`」"
    )
    L.append("> 判定它们「不是创建入口」——这结论对；但由此推断「官方不用它们」是错的。")
    L.append("> 官方示例（`Create_Radiate_Surface_Example_CSharp`、")
    L.append("> `Create_Planar_Surface_Feature_Example_CSharp`、")
    L.append(
        "> `Create_Trimmed_Surface_Feature_Example_CSharp`、`Access_Selections_Example_VB`）"
    )
    L.append("> 证明它们是**路线 B 的载体**。")
    L.append("")
    L.append("---")
    L.append("")
    L.append("## 未被官方示例覆盖的域（与 A1 的「不覆盖+原因」对应）")
    L.append("")
    L.append("| 域 | 官方示例 | 本仓库 | 原因 |")
    L.append("|---|---|---|---|")
    L.append(
        "| 仿真(需许可证) | **0** | `scripts/sw_simulation.py`（部分） | "
        "`C:\\swapi` 只收录 12 个程序集，**不含 cosworks**；"
        "CHM `cosworks` 册是 JS 空壳。两个官方源同时失效 ⇒ "
        "84 个接口里只有 7 个载荷方法拿得到签名。 |"
    )
    L.append(
        "| 路由/Composer/PDM | **0** | **无** | 同上（SWRoutingLib / sldcostingapi / "
        "swdocumentmgr 均不在 `C:\\swapi` 收录范围），且需许可证。 |"
    )
    L.append("")
    L.append(
        "> ⚠ 这两行的「0 个官方示例」本身就是**重要结论**：不是我没写指南，"
        "是**官方在这个域就没给可参考的示例**。"
    )
    L.append("")
    L.append("---")
    L.append("")
    L.append("## 附：语言分布（可参考选哪种语言的示例来读）")
    L.append("")
    L.append("| 语言 | 示例数 |")
    L.append("|---|---|")
    for lang, n in sorted(data["languages"].items(), key=lambda kv: -kv[1]):
        L.append(f"| {lang} | {n} |")
    L.append("")
    L.append(
        "> 本仓库是 **Python**，而官方示例里**没有一个 Python 版本**"
        "（VB 1,201 / C# 794 / VB.NET 777 / C++ COM 41）。"
        "读 VB 即可 —— 迟到绑定的调用形状与 VB 最接近，"
        "这也是 AGENTS.md §六 多条「按 VB 推断 Python 调用形状」结论的由来。"
    )

    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"已生成 {OUT}  ({OUT.stat().st_size} 字节, {len(L)} 行)")
    for d in order:
        print(f"  {d:<24} 强相关示例 {strong_count.get(d, 0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
