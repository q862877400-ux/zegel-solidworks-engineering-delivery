"""★ 批次⑰：给 `mech-design` **全部 86 篇**做逐篇处置清单（★ 收口）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tools/triage_mech_design.py
# 定位:   规格 `specs/332-known-facts-triage` 批次⑰ ——
#           ★★ 收口判据要求「**各批都有明确的『已扫 / 已判断』结论**」。
#           ★ `mech-design` 有 **86 篇** —— ★ 前几批精读了 **18 篇**，
#             ★ 本工具给**全部 86 篇**逐篇处置（★ 吸收 / 放过 + 理由）。
# 官方依据: `~/.agents/skills/mech-design/知识库/`（★ 只读）
# 许可:   本仓库 MIT。★ 外部 skill 只读。
# 覆盖:   全文件
# -----------------------------------------------------------------------------
from __future__ import annotations

import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parents[1]
KB = (pathlib.Path.home() / ".agents" / "skills" / "mech-design"
      / "知识库")

#: ★★★ **已吸收的篇**（★ 逐篇带理由 —— ★ 前几批精读过的）
ABSORBED: dict[str, str] = {
    "静默失败与判据自检": "★★★ 三类静默失败 + 判据自检七种断法 + 成功码不止 0",
    "设计验证的四级信任层级": "★★★★★ L1/L2/L3/L4 + 判据要带方向 + L4 三路径",
    "DFM与机加工工艺性": "★★ 退刀槽/去毛刺/薄壁螺纹/内 R ≥ 刀具半径",
    "ReferenceResolver语义引用与稳定选择器": "★★★★★★ 语义引用 → 索引 + 三个封闭码 + 三条限制",
    "轮廓可行性判据": "★ 判「轮廓能不能建」（★ 与本仓 `check_sketch_definition` 互补）",
    "revolve旋转体": "★★★ 旋转体必须「轮廓 + 轴线段」，缺则 `AXIS_NOT_FOUND`",
    "拉伸与切除": "★★ 草图轮廓必须闭合，否则 `EXTRUSION_FAILED`",
    "钣金": "★★ 必须在【已成形的钣金面】上建折弯线草图；★ 看面数不看体积",
    "装配设计与装配工艺": "★★★ **装配不要全约束**（留 1~2 个给装配公差）",
    "尺寸标注": "★★ 圆/弧不好定位 ⇒ 优先标注直线段",
    "GD&T完整体系": "★★ ASME Y14.5 全体系 + Ⓜ 不要滥用 + `IAnnotation` 无 bbox",
    "形位公差与表面粗糙度": "★★ 轴承孔同轴 ◎0.01~0.03 · 内孔轴线 ⊥端面 0.02~0.05",
    "O型圈与螺纹孔": "★★ 槽深 h≈0.70~0.75w · 软硬材料差 0.1~0.2mm",
    "螺旋弹簧设计": "★★ 有初拉力的拉伸弹簧必须先克服初拉力",
    "工作流W1_从需求到交付做一根轴": "★★ 判据带方向（圆角 R2.1 必须减少 36 mm³）",
    "工作流W3_静力分析端到端": "★★★ 材料必须设在 Simulation 树「零件」节点",
    "工作流W4_工程图端到端": "★★ 必须加 `include_unmarked=$true` 才有尺寸",
    "机械设计工作流手册": "★ 工程图 PDF 必须有 + 材料绑错位置",
    "圆角倒角": "★★★ 优先 `edge_indices`，不要用坐标",
    "轴承数据怎么读": "★ 读表头找列，不要硬编码索引",
    "轴承选型实测": "★★ 报「库的边界」前必须把所有同类表都扫一遍",
    "直齿圆柱齿轮选型": "★★ 换算式必须先在纸面上验算量纲",
    "AddForce终局诊断-两头都卡": "★★ 错误码要看全（6=InvalidArray · 3=Normal 力）",
    "制造工艺路线与工序卡": "★★ 内孔与外圆必须一次装夹 · IT7 必须三坐标",
    "导入导出与文档管理": "★★ 不要只看返回成功（空几何导出 STL 是 0 字节）",
    "攻关战报-布局与粗糙度已通": "★★ 摆位必须从图纸尺寸推导，不能硬编码坐标",
    "工程图整链根因": "★ `IAnnotation` 没有原生 bounding-box API",
    "表面粗糙度符号API速查": "★ 调用前必须先选中面/边",
    "下一步操作指令-修SelectFaceByIndex": "★★ 先查前置，再试形态（面选对了形态就自己对了）",
    "知识库索引": "★ 全库索引（★ 本批的入口）",
    "知识库完整索引": "★ 同上",
    "MCP建模稳定性经验": "★★ MCP 建模的稳定性经验",
    "模态弹窗阻塞COM-根因与DialogGuard": "★ 弹窗根因（★ 已进本仓 `sw_guard`）",
    "元教训合集-操作问题误判成环境问题": "★★ 元教训（★ 与事实 51/53 同族）",
    #: ── ★★ 批次⑰ 精读的 5 篇 ──
    "失败处置决策树": "★★★★★ **四层决策树**（L1 参数 60% · L2 **方法选错** · "
                      "L3 环境 20% · L4 版本/许可 20%）+ "
                      "★「**参数试了 5 遍都不行 = 方法选错了**」+ "
                      "★「**同一错误码连续 2 次就进决策树**」",
    "特征数据接口名对照表": "★★★★★ **136 个 FeatureData 接口名** —— "
                            "★ 孔族 `IWizardHoleFeatureData2` · "
                            "★ loft/sweep `ILoftFeatureData`/`ISweepFeatureData` · "
                            "★ 可变圆角 `IVariableFilletFeatureData2` · "
                            "★★ **Simulation 载荷是两套不同层次**",
    "阵列pattern": "★★★ **「圆周均布 N 个」首选「一草图多圆」**"
                   "（★ 不用轴、不用阵列；★ 实测 9 圆一次成功）",
    "sweep正确入口与诊断": "★★ 扫描的 mark 分工（1=Profile · 2=Guide · 4=Sweep path）"
                           "+ ★ **6 次尝试的精确诊断**（卡在路径 mark=4 设不上）",
    "草图": "★★ 草图相关（★ 已由本仓 `check_sketch_definition` + "
            "`sketch-definition-protocol.md` 覆盖并超越）",
}

#: ★★ **放过的判据**（★ 按主题 —— ★ 每条带理由）
PASS_RULES: list = [
    (re.compile(r"(Simulation|仿真|拓扑|网格|求解|许可|CAE|静力|疲劳|焊缝|失效)"),
     "放过：★ Simulation 探路记录 —— ★ 已进 `known-facts.md` 与本仓 "
     "`docs/A9-solve-attempts.md`"),
    (re.compile(r"(18仓库|GitHub|项目通读|外部资料源|施工计划|调研源|切削用量数据源|"
                r"反面样本)"),
     "放过：★ 外部项目调研 —— ★ 与本仓 `docs/sources.md` 重复"),
    (re.compile(r"(BT30|主轴|设计任务|方案比选|需求分析)"),
     "放过：★ 具体零件设计案例（★ 非通用方法）"),
    (re.compile(r"(材料选型)"),
     "放过：★ 材料选型数据表（★ 属选型数据，★ 非建模方法）"),
    (re.compile(r"(轴承|齿轮|V带|弹簧|螺旋传动|丝杠|电机|O型圈|标准件)"),
     "放过：★ 选型计算 —— ★ 数据已由 `standard_parts.py` 接出（★ 17 张表）"),
    (re.compile(r"(公差|配合|GD&T|粗糙度|形位)"),
     "放过：★ 公差体系 —— ★ 关键条已吸收（★ 见 `ABSORBED`）"),
    (re.compile(r"(环境|工具|许可|NET|编译|Python|VBA|宏|弹窗|守卫|attach|"
                r"进程|产品真实可用性|接口遍历|官方API全量|服务端49)"),
     "放过：★ 环境/工具探路 —— ★ 已进 `known-facts.md`"),
    (re.compile(r"(工程图|图纸|图幅|视图|标注|BOM|钣金|焊接|工艺|工序|DFM|失效)"),
     "放过：★ 已吸收关键条（★ 见 `ABSORBED`）"),
]


def main() -> int:
    if not KB.is_dir():
        print("★★ 没有 %s" % KB)
        return 1
    arts = sorted(KB.rglob("*.md"))
    absorbed, passed, unknown = [], [], []
    for f in arts:
        stem = f.stem
        if stem in ABSORBED:
            absorbed.append((stem, str(f.relative_to(KB)), ABSORBED[stem]))
            continue
        t = f.read_text(encoding="utf-8", errors="replace")
        #: ★ 先读 front matter 的「标题 / 标签」
        head = t[:600]
        why = None
        for pat, reason in PASS_RULES:
            if pat.search(head) or pat.search(f.name):
                why = reason
                break
        if why:
            passed.append((stem, str(f.relative_to(KB)), why))
        else:
            unknown.append((stem, str(f.relative_to(KB))))
    print("★★ `mech-design` 全库：**%d 篇**" % len(arts))
    print("   ★ 已吸收（★ 逐篇带理由）：**%d**" % len(absorbed))
    print("   ★ 放过（★ 按主题带理由）：**%d**" % len(passed))
    print("   ★ 未判定：**%d**" % len(unknown))
    if unknown:
        print()
        print("★★ 未判定的（★ 要逐篇看）：")
        for s, p in unknown:
            print("   %s  ← %s" % (s, p))
    #: ★★ 落盘
    out = ROOT / "specs" / "332-known-facts-triage" / "mech-design-ledger.md"
    L = ["# `mech-design` 全库逐篇处置台账（规格 332 · 批次⑰）", "",
         "**判据**：", "",
         "| 处置 | 含义 |", "|---|---|",
         "| **吸收** | 给出**可落到本仓语料/工具层/判据**的**方法** |",
         "| **放过** | 已由别处覆盖 / 非通用方法 / 数据已接出 |",
         "",
         "**★ 全库共 %d 篇**" % len(arts), "",
         "---", "",
         "## 一、★ 已吸收（%d 篇）" % len(absorbed), "",
         "| 篇 | 吸收了什麼 |", "|---|---|"]
    for s, _, why in absorbed:
        L.append("| `%s` | %s |" % (s, why))
    L.append("")
    L.append("## 二、★ 放过（%d 篇 · 按主题）" % len(passed))
    L.append("")
    by: dict[str, list] = {}
    for s, _, why in passed:
        by.setdefault(why, []).append(s)
    for why in sorted(by):
        L.append("### %s" % why)
        L.append("")
        L.append("> %s" % " · ".join("`%s`" % s for s in sorted(by[why])))
        L.append("")
    if unknown:
        L.append("## 三、★★ 未判定（%d 篇）" % len(unknown))
        L.append("")
        for s, p in unknown:
            L.append("- `%s` ← `%s`" % (s, p))
        L.append("")
    out.write_text("\n".join(L), encoding="utf-8")
    print()
    print("★ ⇒ %s" % out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
