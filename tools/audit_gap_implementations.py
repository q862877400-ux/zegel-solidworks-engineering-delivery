"""★ 静态审计：`user-feature-coverage.md` 的缺口项，**本仓到底有没有真实现**（AST 为准）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（只读审计）· 规格 `specs/202-user-coverage-gaps`（T004 的机器可核那
# 一半）
# 文件:   tools/audit_gap_implementations.py
# 定位:   ★ 2026-10-03（接手轮）★ 为「提升覆盖面」先量**最便宜的那一类待办**：
#   ★★ **已经写好了、只是没挂成工具的** —— 那些**不用从零实现**（宪法 §I 缝合优先）。
#
# ⚠★ **为什么不用 grep**（实测踩过）：★ 直接 grep 成员名会把**注释与来源块**也算成"有实
# 现"
#     —— 本仓的来源块里**大量引用官方成员名**（那是它的用途）⇒ grep 会给出**假阳性**。
#     ★ 实测：`CreateExplodedView` / `InsertProtrusionBlend2` / `InsertRevolvedRefSurface`
#       在 grep 下"有实现"，★ 而**逐行看是在文档串里** ⚠
#     ⇒ ★★ 故判据改用 **AST**：只看**真的调用节点**（`get_com_member(o,"M")` 与 `o.M`），
#       ★ 注释与文档串**在 AST 里不存在** ⇒ 从形态上消掉这类假阳性。
#
#   ⚠★ **另一条边界（如实写）**：★ 本审计**不判「该不该暴露成工具」** ——
#     ★ 很多函数是**内部步骤**（同一流程的一段）⇒ "未引用"不等于"该挂"。
#     ★ 「该不该」由人判（事实 53：不为它调启发式）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parents[1]

#: ★ **反射转储不算实现** —— 它是生成的 API 索引（本仓既有约定：`find_real_implementatio
#: ns` 排除它）
EXCLUDE_PREFIX = ("sw_api_",)

#: ★ 缺口项 ⇒ 候选官方成员名（★ 来自 `docs/user-feature-coverage.md` §八）
GAP_ITEMS = {
    "草图/样条曲线": ["CreateSpline", "CreateSpline2"],
    "草图/完全定义检查": ["GetConstrainedStatus"],
    "特征/边界凸台": ["InsertProtrusionBlend2", "InsertProtrusionBlend"],
    "特征/孔向导": ["HoleWizard5", "HoleWizard"],
    "特征/曲线驱动阵列": ["InsertCurveDrivenPattern"],
    "特征/加厚": ["InsertThickenFeature", "FeatureThicken"],
    "特征/组合相交": ["InsertCombineFeature", "InsertIntersect"],
    "特征/缩放变形": ["InsertScale", "Scale"],
    "曲面/旋转曲面": ["InsertRevolvedRefSurface"],
    "曲面/剪裁曲面": ["InsertTrimSurface", "InsertCutSurface"],
    "曲面/中面": ["InsertMidSurface"],
    "钣金/斜接法兰": ["InsertMiterFlange"],
    "钣金/闭合角转折褶边": ["InsertClosedCorner", "InsertJog", "InsertHem"],
    "钣金/展开折叠": ["InsertFlatPattern", "Unfold"],
    "钣金/平板型式导出DXF": ["ExportFlatPatternView", "ExportToDWG"],
    "焊件/裁剪延伸焊件": ["InsertTrimExtend"],
    "焊件/顶端盖": ["InsertEndCap"],
    "焊件/角撑板": ["InsertGusset", "IGussetFeatureData", "ISMGussetFeatureData"],
    "焊件/焊接符号": ["InsertWeldSymbol"],
    "装配/爆炸视图": ["CreateExplodedView", "AutoExplode"],
    "工程图/投影视图": ["CreateDrawViewFromModelView3", "CreateDrawViewFromModelView"],
    "工程图/剖面视图": ["CreateSectionViewAt5", "CreateSectionViewAt"],
    "工程图/局部视图": ["CreateDetailViewAt4", "CreateDetailViewAt"],
    "工程图/断裂视图": ["InsertBreak", "BreakView"],
    "工程图/辅助视图": ["CreateAuxiliaryViewAt2", "CreateAuxiliaryView"],
    "工程图/图纸格式模板": ["SetupSheet5", "SetTemplate"],
    "工程图/表面粗糙度": ["InsertSurfaceFinishSymbol3", "InsertSurfaceFinishSymbol"],
    "工程图/基准符号": ["InsertDatumTag2", "InsertDatumTag"],
    "工程图/注释文字": ["InsertNote", "InsertBOMBalloon2"],
    "工程图/气泡序号": ["AutoBalloon5", "AutoBalloon", "InsertBOMBalloon2"],
    "工程图/孔表": ["InsertHoleTable2", "InsertHoleTable"],
    "工程图/修订表": ["InsertRevisionTable2", "InsertRevisionTable"],
    "工程图/中心符号线": ["InsertCenterMark3", "InsertCenterMark"],
    "其他/宏VBA": ["RunMacro", "RunMacro2"],
    "其他/PDM": ["IPDMObject", "PDM"],
}


def _module_refs(path: Path):
    """★ 该模块在**代码里**引用到的 COM 成员名（AST 为准；注释与文档串不算）。"""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return set(), set()
    via_helper, via_attr = set(), set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            name = (
                f.id
                if isinstance(f, ast.Name)
                else (f.attr if isinstance(f, ast.Attribute) else "")
            )
            if name in ("get_com_member", "set_com_member", "_get", "_sel", "getattr"):
                for a in node.args[1:2]:
                    if isinstance(a, ast.Constant) and isinstance(a.value, str):
                        via_helper.add(a.value)
        elif isinstance(node, ast.Attribute):
            via_attr.add(node.attr)
    return via_helper, via_attr


def _scan_roots():
    refs = {}
    for d in ("scripts", "mcp-server"):
        for f in sorted((R / d).glob("*.py")):
            if f.name.startswith(EXCLUDE_PREFIX):
                continue
            h, a = _module_refs(f)
            if h or a:
                refs[f"{d}/{f.name}"] = (h, a)
    return refs


def main() -> int:
    refs = _scan_roots()
    rows = []
    for item, members in GAP_ITEMS.items():
        hits = []
        for mod, (h, a) in refs.items():
            for m in members:
                if m in h:
                    hits.append(f"{mod}:{m}(★ 真调用)")
                elif m in a:
                    hits.append(f"{mod}:{m}(属性访问)")
        rows.append(
            {
                "item": item,
                "members": members,
                "implemented": bool(hits),
                "hits": sorted(set(hits))[:4],
            }
        )
    out = R / "output" / "gap-implementation-audit.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            {"modules_scanned": len(refs), "rows": rows}, ensure_ascii=False, indent=1
        )
        + "\n",
        encoding="utf-8",
    )
    done = [r for r in rows if r["implemented"]]
    print("缺口项审计 · 扫了 %d 个模块（★ 已排除 sw_api_* 反射转储）" % len(refs))
    print(
        "  ★ **已有真实现**（⇒ 最便宜的待办：挂工具即可）：%d / %d"
        % (len(done), len(rows))
    )
    for r in done:
        print("    %-22s %s" % (r["item"], r["hits"][0]))
    print("  未实现：%d 项（★ 需从零做或判到不了）" % (len(rows) - len(done)))
    print("  产物：%s" % out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
