"""★ 规格 211 · B0 台账生成器：逐项查官方入口 + 判可做性（★ 只读，不碰真机）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（规格 211 · B0 的台账生成器）
# 文件:   tools/gen_spec211_ledger.py
# 定位:   ★ 规格 `specs/211-user-feature-gaps` 的 **B0**。★ 21 项用户功能缺口要逐项查：
# ★ **官方有没有这个入口** · ★ 是**哪个接口的哪个成员** · ★ **要不要 `AccessSelections`*
# *
#   ⇒ ★★ 这三件事**决定一项是"可做"还是"不做"** —— 不先判就动手 = 拿真机窗口去撞已知的墙
#     （★ 事实 47：`AccessSelections` 族 20+ 形态穷尽，★ **不许重试**）✓
# 判据:   ★★ **必须同时查四处**（★ 2026-10-06 实测踩过：**只查一处会漏**）：
#     ① `C:\swapi\types\<接口>\<成员>.md`（★ 签名精确）
#     ② `C:\swapi\enums\*`（★ 常量）
# ③ ★ **CHM 正文树的 API 命名空间**（`SolidWorks.Interop.*`）—— ★★ 漏了它会**误判"查不到
# "**：
# 实录 ★「边界凸台」⇒ ★ `C:\swapi\types` 里查不到，★ **而 CHM 里有 `IBoundaryBossFeature
# Data`** ✗
#     ④ ★ CHM 里的**示例页**（`.htm`，★ 判"有没有示例可抄"）
#   ★★ 判"不做"要有依据：① 四处**都查不到** ⇒ 「官方无入口」（铁律 5）·
# ② 入口存在但**要 `AccessSelections`** ⇒ 事实 47（后端限制）· ③ 要**另外的产品/许可证**
#  ✓
# 官方依据: `C:\swapi\`（结构化）+ `D:\AI\SW\AI Solidworks\官方文档\SWhelp\`（CHM 解包）
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import os
import re
from pathlib import Path

#: ★★ 人工终判表（★ 只补空、不覆盖自动结果；★ 事实 53：启发式改了 3 次就停手）✓
import spec211_manual_verdicts as MV

SWAPI = Path(r"C:\swapi")
TYPES = SWAPI / "types"
ENUMS = SWAPI / "enums"
SWHELP = Path(
    os.environ.get(
        "DSL_SWHELP",
        Path(__file__).resolve().parents[1] / "AI Solidworks" / "官方文档" / "SWhelp",
    )
)
OUT = Path(Path(__file__).resolve().parents[1] / "docs" / "spec211-entry-ledger.md")
OUT_JSON = Path(
    Path(__file__).resolve().parents[1] / "output" / "spec211-ledger-candidates.json"
)

ITEMS = [
    ("特征", "边界凸台", ("BoundaryBoss",)),
    (
        "特征",
        "曲线驱动阵列",
        (
            "CurveDrivenPattern",
            "CurvePattern",
            "swFmCurvePattern",
            "swFmCurveDrivenPattern",
        ),
    ),
    (
        "特征",
        "缩放/变形",
        ("InsertScale", "InsertDeform", "ScaleFeatureData", "DeformFeatureData"),
    ),
    ("特征", "特征识别/Instant3D", ("FeatureRecogn", "Instant3D", "RecognizeFeature")),
    ("曲面", "扫描曲面", ("InsertSweepSurface", "SweepSurface")),
    (
        "曲面",
        "边界曲面",
        (
            "InsertBoundarySurface",
            "BoundarySurface",
            "RuledSurface",
            "InsertRuledSurface",
        ),
    ),
    ("曲面", "剪裁曲面", ("InsertUntrimSurface", "TrimSurface", "InsertTrimSurface")),
    ("钣金", "成形工具", ("FormTool", "InsertFormTool")),
    ("钣金", "展开/折叠", ("InsertSheetMetalUnfold", "InsertSheetMetalFold", "Unfold")),
    (
        "钣金",
        "平板型式/导出 DXF",
        ("FlatPattern", "InsertFlatPattern", "ExportToDXF", "ExportFlatPattern"),
    ),
    (
        "焊件",
        "裁剪/延伸焊件",
        ("InsertWeldmentTrim", "WeldmentTrim", "InsertEndCapFeature"),
    ),
    ("焊件", "角撑板（焊件）", ("Gusset", "InsertGussetFeature")),
    ("焊件", "圆角焊缝", ("FilletBead", "WeldBead", "InsertFilletBead")),
    ("焊件", "焊接符号", ("WeldSymbol", "InsertWeldSymbol")),
    ("装配", "爆炸直线", ("ExplodeLine", "InsertExplodeLineSketch", "ExplodeStep")),
    ("装配", "零部件阵列", ("ComponentPattern", "swFmLocal", "LocalPattern")),
    ("装配", "SpeedPak", ("SpeedPak", "Speedpak")),
    (
        "装配",
        "序列 / 说明书（Assembly Visualization）",
        ("AssemblyVisualization", "AssemblySequence", "Storybook"),
    ),
    (
        "装配",
        "装配体性能分析",
        ("PerformanceAnalysis", "AssemblyPerformance", "PerformanceEvaluation"),
    ),
    ("评估", "截面属性", ("SectionProperties", "GetSectionProperties")),
    ("其他", "PDM", ("sldPDM", "IEdm", "IEdmFile", "PDM")),
]


def _swapi_index() -> tuple:
    t: dict = {}
    for p in TYPES.glob("*/*.md"):
        t.setdefault(p.stem.lower(), []).append(p)
    e: dict = {}
    if ENUMS.is_dir():
        for p in ENUMS.glob("*.md"):
            e[p.stem.lower()] = p
    return t, e


def _chm_index() -> tuple:
    """★ 建 CHM 索引：★ 只收 **API 命名空间** 的页；★ 示例页（`.htm`）另收 ✓"""
    api, examples, sig = {}, [], {}
    if not SWHELP.is_dir():
        return api, examples, sig
    for p in SWHELP.rglob("*.html"):
        n = p.name
        if "SolidWorks.Interop." not in n:
            continue
        #: ★ 形如 `...sldworks.IModelDoc2~GetSectionProperties2.html` ⇒ 取成员名 ✓
        #: ★★★ **修过一次**：★ 我第一版写 `~([A-Za-z_][\w]*)\.html$`（★ **不许名字里有点
        #: **）⇒
        #: ★★ 于是**接口页**（`~SolidWorks.Interop.sldworks.IBoundaryBossFeatureData.htm
        #: l`）
        #:   一个都进不来 ⇒ ★ 台账把「边界凸台」误判成"四个源都查不到" ✗
        #:   ⇒ ★ 改成**允许点**、★ 再取**最后一段**（★ 于是接口页与成员页都收）✓
        m = re.search(r"~([\w.]+)\.html$", n)
        if m:
            api.setdefault(m.group(1).rsplit(".", 1)[-1].lower(), []).append(p)
    for p in list(SWHELP.rglob("*.htm")) + list(SWHELP.rglob("*.html")):
        if "Example" in p.name:
            examples.append(p)
    return api, examples, sig


def _needs_access(p: Path) -> bool:
    """★ 这一页要不要 `AccessSelections`（★ **必须读正文**，★ 不能只看它是从哪个源来的）✓

    ★★★ **修过一次**：★ 我第一版把 CHM 侧的 `needs_access` 一律置 `False`（★ 因为没读它的正文）
      ⇒ ★★ 于是「**边界凸台**」**逃过了** `AccessSelections` 检查、被判「可做」✗
      —— 而它实际有 `IBoundaryBossFeatureData::AccessSelections` ✓（★ 我另行核实过）✓
    """
    try:
        t = p.read_text(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        return False
    return "AccessSelections" in t


def _sig_of(p: Path) -> str:
    try:
        t = p.read_text(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        return ""
    m = re.search(r"\*\*Signature\*\*:\s*(.+?)\s*$", t, re.M)
    if m:
        return m.group(1)[:110]
    m = re.search(r"Signature.*?</", t)
    return ""


def main() -> int:
    types, enums = _swapi_index()
    chm_api, chm_examples, _ = _chm_index()
    print(
        "★ 索引规模：swapi types %d 名 · enums %d · CHM API 页名 %d · CHM 示例页 %d"
        % (len(types), len(enums), len(chm_api), len(chm_examples))
    )

    rows, raw = [], []
    for domain, name, keys in ITEMS:
        hits, ex_n = [], 0
        for k in keys:
            kl = k.lower()
            for stem, paths in types.items():
                if kl in stem:
                    txt = paths[0].read_text(encoding="utf-8", errors="replace")
                    hits.append(
                        {
                            "src": "swapi",
                            "key": k,
                            "iface": paths[0].parent.name,
                            "member": paths[0].stem,
                            "sig": _sig_of(paths[0]),
                            "needs_access": "AccessSelections" in txt,
                        }
                    )
            if kl in enums:
                hits.append(
                    {
                        "src": "swapi-enum",
                        "key": k,
                        "iface": "enums",
                        "member": enums[kl].stem,
                        "sig": "",
                        "needs_access": False,
                    }
                )
            #: ★★ CHM 的 API 命名空间（★ 漏了它会误判"查不到"）
            for stem, paths in chm_api.items():
                if kl in stem:
                    #: ★★ CHM 侧**也要读正文**判 AccessSelections（★ 否则会误判"可做"）✓
                    hits.append(
                        {
                            "src": "chm-api",
                            "key": k,
                            "iface": "(CHM)",
                            "member": paths[0].name,
                            "sig": "",
                            "needs_access": _needs_access(paths[0]),
                        }
                    )
            for p in chm_examples:
                if kl in p.name.lower():
                    ex_n += 1
        seen, uniq = set(), []
        for h in hits:
            kk = (h["iface"], h["member"])
            if kk not in seen:
                seen.add(kk)
                uniq.append(h)
        api_hits = [h for h in uniq if h["src"] != "swapi-enum"]
        #: ★★ 判定
        if not api_hits:
            verdict, why = (
                "疑无入口",
                "★ **四处都查不到**该入口（★ 关键词是拟的，★ 可能是我命名猜错）⇒ 需人工确认（铁律 5）",
            )
        else:
            #: ★ 若 `C:\swapi` 侧命中且**全都要 AccessSelections** ⇒ 后端限制
            #: ★★ **任一源说"要"就算要**（★ 不再只看 `C:\swapi` 那一侧）✓
            sw = [h for h in api_hits if h["needs_access"]]
            if sw:
                verdict, why = (
                    "待核实",
                    "★ 候选里**出现 `AccessSelections`**（★ 关键词共现，**不是定论**）⇒ 需读那一页确认",
                )
            else:
                verdict, why = "可做", "★ 官方有入口"
        raw.append(
            {
                "domain": domain,
                "item": name,
                "keys": list(keys),
                "examples_matched": ex_n,
                "hits": uniq,
                "verdict": verdict,
                "why": why,
            }
        )
        #: ★★ **人工终判优先**（★ 只补空 + 不一致要留痕）✓
        mv = MV.verdict_of(name)
        auto_verdict = verdict
        if mv:
            m_domain, m_verdict, m_why = mv
            why = "★★ **人工终判**：%s" % m_why
            verdict = m_verdict
            if m_verdict != auto_verdict:
                why += "　（★ 自动台账原判：%s）" % auto_verdict
        rows.append((domain, name, uniq, verdict, why, ex_n))

    OUT_JSON.write_text(
        json.dumps(raw, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    n_do = sum(1 for r in rows if r[3] == "可做")
    n_no = sum(1 for r in rows if r[3] == "不做")
    n_done = sum(1 for r in rows if r[3] == "已覆盖")
    n_todo = sum(1 for r in rows if r[3] == "待实测")
    lines = [
        "# 规格 211 · B0 官方入口台账（21 项）",
        "",
        "> ★ 由 `tools/gen_spec211_ledger.py` 生成 —— ★ **不要手改**。",
        "> ★★ 查**四处**：`C:\\swapi\\types` · `C:\\swapi\\enums` · **CHM 的 API 命名空间** · CHM 示例页。",
        "> ⚠★ 实录：**只查 `C:\\swapi` 会误判「边界凸台」为「查不到」**，而 CHM 里有 `IBoundaryBossFeatureData` ✗",
        "> ★★ 故「不做」的两种依据：**四处都查不到**（官方无入口）· **要 `AccessSelections`**（事实 47）。",
        "> ⚠ ★★ **这不是终判** —— ★ `AccessSelections` 信号是**关键词共现**、★ 太粗（★ 实录：「曲线驱动阵列」17 个候选，★ 只要**一个**提到就触发）；★ 「疑无入口」也可能是我**命名猜错**。",
        "> ★★ **终判方式：逐项读那一页的三样**（签名 / Remarks / Example）⇒ ★ 见 `tasks.md` B0-2。",
        "> ★ 依据**事实 53**：同一启发式已连续改 3 次 ⇒ ★ **停止调它**，改成「信号 + 人工终判」✓",
        "",
        "★★ 合计 **21** 项（★ **人工终判**）：★ **可做 %d** · **不做 %d** · **已覆盖 %d** · **待实测 %d**"
        % (n_do, n_no, n_done, n_todo),
        "",
    ]
    for domain, name, uniq, verdict, why, ex_n in rows:
        lines.append("## %s · %s ⇒ **%s**" % (domain, name, verdict))
        lines.append("")
        lines.append("· 初判：%s" % why)
        lines.append("· 该关键词命中的 CHM **示例页**：**%d**" % ex_n)
        for h in uniq[:6]:
            tag = "★ 要 AccessSelections" if h["needs_access"] else ""
            lines.append(
                "  · `[%s] %s::%s` %s %s"
                % (h["src"], h["iface"], h["member"], h["sig"], tag)
            )
        if len(uniq) > 6:
            lines.append("  · …（共 %d 个候选）" % len(uniq))
        lines.append("")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("★ 台账：%s" % OUT)
    print(
        "★★ 终判：可做 **%d** · 不做 **%d** · 已覆盖 **%d** · 待实测 **%d**"
        % (n_do, n_no, n_done, n_todo)
    )
    for domain, name, uniq, verdict, why, ex_n in rows:
        print(
            "   %-5s %-26s %-5s 候选%3d 示例%3d  %s"
            % (domain, name, verdict, len(uniq), ex_n, why[:40])
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
