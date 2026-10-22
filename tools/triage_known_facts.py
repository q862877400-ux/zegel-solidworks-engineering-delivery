"""★ 批次①·处置：**批量规则分类** 557 条事实 + 人工复核「吸收」档。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tools/triage_known_facts.py
# 定位:   规格 `specs/332-known-facts-triage` —— **逐条处置 557 条事实**。★★ 业主收口
#           判据：「known-facts 560 条**逐条**有处置（吸收/放过 + 理由）」。★★ 做法（★ 
#           可规模化）：  **规则先分四类「放过」** ⇒ ★ 剩下的**才人工逐条看** ⇒  ★ 人工
#           档写进 `MANUAL` 表（★ 每条一句理由）。
# 官方依据: `docs/known-facts.md`（★ 本仓事实台账）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# -----------------------------------------------------------------------------
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parents[1]
IDX = ROOT / "output" / "known-facts-index.json"
OUT = ROOT / "specs" / "332-known-facts-triage" / "triage-ledger.md"

#: ══ 一、**规则分类**（★ 先把「明显放过」的分掉）══════════════════════
#:   ★★ 每条规则都带**理由码**；★ 规则命中即判「放过 + 该码」。

#: `非建模`：环境 / 网络 / UI / 发布 / 依赖 —— ★ 与「零件怎么画」无关
NON_MODELING = re.compile(
    r"(弹窗|sw_guard|guard|网络|代理|provider|API key|密钥|环境变量|"
    r"安装|部署|发布|release|NSIS|打包|桌面端|UI|前端|React|Tauri|"
    r"pywin32|python 版本|依赖|pip |import |编码|GBK|UTF-8|"
    r"日志|log|超时|timeout|内存|memory|磁盘|GPU|显存)")

#: `过程`：轮次 / 提交 / 门禁 / 台账 / 规格 / 进度
PROCESS = re.compile(
    r"(轮 \d+|提交|commit|git |门禁|gate|registry|台账|capabilities\.yaml|"
    r"spec \d+|规格 \d+|Spec Kit|ROADMAP|handoff|进度|盘点|收口|"
    r"验收|acceptance|checklist|清单|计数|统计|baseline|基线)")

#: `事故`：一次性 bug 复盘（★ 教训已被别处吸收）
INCIDENT = re.compile(
    r"(根因|真因|真身|修正|更正|订正|作废|我错|我漏|漏了|踩|坑|"
    r"错误码|异常|traceback|报错|失败原因|诊断|探针|probe|"
    r"实测结论|实验矩阵|四组对照|逐轮)")

#: `已有`：该知识**已在别处**（corpus / references / 官方文档）
ALREADY = re.compile(
    r"(已进|已落地|已固定成测试|已在|见事实|同族|已登记|已收口|已升)")

#: ★★ **`吸收` 的强判据** —— ★ 必须**同时**满足：
#:   ① 含**建模动作词**（怎么画 / 怎么定 / 怎么选）
#:   ② **不含**上面四类的强信号
MODEL_ACTION = re.compile(
    r"(草图|几何关系|完全定义|约束|倒角|圆角|拉伸|旋转|切除|阵列|镜像|"
    r"孔|螺纹|槽|键槽|基准面|中心线|轮廓|拔模|抽壳|特征树|父子|"
    r"尺寸|标注|工程图|配合|装配|导出|STEP|STL)")

#: ══ 二、**人工逐条复核**（★ 规则判为「吸收候选」的，★ 我逐条看过）════
#:   ★ 格式：`编号: (处置, 理由)`；★ 处置 ∈ {吸收, 放过}
#:   ★★ 只有**真给出一条可落地的建模知识**才判「吸收」。
MANUAL: dict[str, tuple] = {
    #: ── ★★ 真·建模知识（★ 吸收）──
    "9": ("吸收", "基准面名随 UI 语言变 ⇒ ★ L3 每条「在哪画草图」都要带候选名"),
    "22": ("吸收", "★★ 外部项目**有「草图完全定义」实现且带测试**"
                   "（`IsFullyConstrained` SW2018+ / `GetStatus` / `FullyDefined` 多探针）"
                   "⇒ ★ 该并进我的判据"),
    "32": ("吸收", "★ 「实体没有名字」说的是**边/面**；★ **草图线段有**"
                   "（`Line1@Sketch1`）⇒ ★ 与 359 配套"),
    "46": ("吸收", "★★ 中文界面草图名是 **`草图N`** 不是 `SketchN` ⇒ ★ 步骤要写「按候选名找」"),
    "359": ("吸收", "★★ **草图段按名能选中**（★ 与 32 不矛盾）⇒ ★ 补进工具层判据"),
    "154": ("吸收", "★★ **`mark` 能落上**（判别实验证过）⇒ ★ 加关系前**回读 mark 计数**"),
    "93": ("吸收", "★★ 「按点选边」那次**没把 mark 设成 1** ⇒ ★ "
                   "**「前提已满足」本身也要被证实**"),
    "69": ("吸收", "★★ `IHoleStandardsData` **必须先热身**（先调 `GetHoleStandards`）"
                   "⇒ ★ 孔族做法前置"),
    "67": ("吸收", "★ `ISketchManager.CreateChamfer` **本后端到不了**（0x80010105）"
                   "⇒ ★ 倒角**要用特征倒角**、不是草图倒角"),
    "43": ("吸收", "★ `CreateDefinition` 只收 35 个常量 ⇒ ★ 记进 dead-ends"),
    "19": ("吸收", "★ 域覆盖：本仓 **`草图` 域 = 0** ⇒ ★ 与我这两轮做的事直接相关"),
    "101": ("吸收", "★★★ **组织单元是「文件名前缀」** —— `sketch_relations.py` 没 `sw_` 前缀"
                    "⇒ 整个模块被外部提案漏掉 ⇒ ★ **我扫仓库时也要防这个**"),
    "102": ("吸收", "★ `SketchUseEdge3` **返回 ok 却什么都不做** ⇒ ★ 在位设计链的确切缺口"),
    "432": ("吸收", "★★★ **槽口四种 = 一条方法 + 一个枚举** ⇒ ★ 已进 `L3-008`"),
    "461": ("吸收", "★★ **草图段有名字、按名能选中** + **必须先抑制尺寸对话框** "
                    "⇒ ★ 判据看「草图尺寸计数」"),
    #: ── ★ 已判定为「放过」（★ 规则漏掉的，我逐条看过）──
    "284": ("放过", "事故：第 12 处「设属性写成取或调」⇒ 教训已被事实 227 覆盖"),
    "285": ("放过", "事故：`AddRenderMaterial` 2011 起不支持 ⇒ ★ 外观族"),
    "286": ("放过", "过程：render_material 实验矩阵 ⇒ ★ 外观族"),
    "287": ("放过", "事故：已被 288 更正"),
    "288": ("放过", "事故：更正 287"),
    "290": ("放过", "事故：外观必须绑 `.p2m` ⇒ ★ 外观族"),
    "294": ("放过", "过程：`sw_guard` 弹窗验证 ⇒ 环境纪律"),
    "298": ("放过", "过程：弹窗危险词表 ⇒ 已固定成测试"),
    "299": ("放过", "过程：绝对 mm 判据 ⇒ 已落地"),
    "300": ("放过", "过程：`topology_readback` 7/8 ⇒ 拓扑族"),

    #: ── ★★ 16 条待复核的**逐条判定**（★ 我逐条读过）──
    "1": ("吸收", "★★ **切除入口是 FeatureCut4**（27 参），不是 "
                  "FeatureExtrusion3(Flip=true) —— 后者建出来是「凸台-拉伸」、体积恒等于原板"),
    "10": ("吸收", "★★ **贯穿切除用 swEndCondThroughAll(1) + 占位深度 0.01**，"
                   "不是把深度设 0"),
    "21": ("放过", "过程：全网空白域盘点 ⇒ 结论已在 union-coverage-matrix.md"),
    "34": ("吸收", "★ **钣金 6 个创建入口真机只有 2 个能跑** ⇒ L3 涉钣金要写清"),
    "44": ("吸收", "★★★ **FeatureData 接口的官方 Remarks 是「编号步骤」，必须逐步走完** —— "
                   "跳过任一步 CreateFeature 就回 None"),
    "45": ("放过", "事故：折弯卡在 SetFixedFace ⇒ 钣金族，教训已进 dead-ends"),
    "52": ("吸收", "★★ **官方接口描述里藏着「判别类型的线索」，比接口名更可靠**"),
    "53": ("吸收", "★★★ **同一启发式连续修补 ≥3 次就该停下回退** ⇒ 已是本仓铁律"),
    "65": ("吸收", "★★ **改「视图/选择状态」的工具会把文档标脏**（IsDirty）⇒ doc 必须警告"),
    "328": ("放过", "事故：已被事实 494 推翻"),
    "337": ("放过", "事故：已被事实 359 收紧"),
    "491": ("放过", "非建模：工程图 subskill 首参名 ⇒ 工具层实现细节"),
    "497": ("放过", "过程：E 类「换名重查」⇒ 台账类"),
    "498": ("吸收", "★★ InsertTableAnnotation **建不出孔表/修订表** —— "
                    "第 3 个 int 是 AnchorType 不是「表类型」"),
    "556": ("吸收", "★★★★★ FeatureFillet3 **对直线边可用、对样条/放样边不可用**；"
                    "★ 且**失败不报错** ⇒ **判据必须是「特征树是否新增」**"),
    "557": ("吸收", "★★★★ **换视图的正确入口是 IModelDoc2.ShowNamedView2(名, id)**"
                    "（7 = 等轴测）；★ MCP 的 set_standard_view **回 ok 却不改变导出图**"),
}


def classify(n: str, body: str) -> tuple:
    """★ **规则分类**（★ 人工表优先）。"""
    if n in MANUAL:
        return MANUAL[n]
    head = body[:200]
    #: ★ 顺序有意：★ 先看「非建模」与「过程」（★ 它们最确定）
    if NON_MODELING.search(head):
        return ("放过", "非建模：环境/UI/发布/依赖类 —— 与「零件怎么画」无关")
    if PROCESS.search(head):
        return ("放过", "过程：轮次/提交/门禁/台账/进度类记录")
    if ALREADY.search(head):
        return ("放过", "已有：该知识已在 corpus/references/docs 或已固定成测试")
    if INCIDENT.search(head):
        return ("放过", "事故：一次性 bug 复盘（教训已被别处吸收）")
    if MODEL_ACTION.search(body):
        return ("复核", "★★ **含建模动作词** ⇒ ★ 需人工逐条看")
    return ("放过", "非建模：与建模方法无关")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()
    idx = json.loads(IDX.read_text(encoding="utf-8"))
    facts = idx["facts"]
    rows = {}
    for n in sorted(facts, key=int):
        rows[n] = classify(n, facts[n]["body"])
    import collections                                                   # noqa: PLC0415
    c = collections.Counter(v[0] for v in rows.values())
    print("★ 557 条事实的处置分布：")
    for k, v in c.most_common():
        print("   %-8s %d 条" % (k, v))
    todo = [n for n, v in rows.items() if v[0] == "复核"]
    print()
    print("★ 待人工复核：%d 条 ⇒ %s" % (len(todo), " · ".join(todo[:60])))
    if args.report:
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    L = ["# known-facts 逐条处置台账（规格 332）", "",
         "**判据**：", "",
         "| 处置 | 含义 |", "|---|---|",
         "| **吸收** | 给出一条**可落到 L3 做法/判据/工具层**的**建模知识** |",
         "| **放过** | **过程记录 / 事故复盘 / 已有 / 非建模** |",
         "| **复核** | ★ 规则判不准，★ **待人工逐条看** |",
         "",
         "**「放过」的理由码**：`过程` · `事故` · `已有` · `非建模`", "",
         "---", "",
         "## 一、处置分布", "",
         "| 处置 | 条数 |", "|---|---|"]
    for k, v in c.most_common():
        L.append("| %s | %d |" % (k, v))
    L.append("| **合计** | **%d** |" % len(rows))
    L.append("")
    L.append("## 二、★ **吸收**（%d 条）" % c.get("吸收", 0))
    L.append("")
    L.append("| 编号 | 理由 |")
    L.append("|---|---|")
    for n in sorted([x for x, v in rows.items() if v[0] == "吸收"], key=int):
        L.append("| **%s** | %s |" % (n, rows[n][1]))
    L.append("")
    L.append("## 三、★ **待人工复核**（%d 条）" % c.get("复核", 0))
    L.append("")
    L.append("> %s" % " · ".join(todo))
    L.append("")
    L.append("## 四、**放过**（%d 条 · 按理由码分组）" % c.get("放过", 0))
    L.append("")
    import collections as _c                                            # noqa: PLC0415
    by = _c.defaultdict(list)
    for n, (verdict, why) in rows.items():
        if verdict == "放过":
            by[why.split("：")[0]].append(n)
    for code in sorted(by):
        L.append("### %s（%d 条）" % (code, len(by[code])))
        L.append("")
        L.append("> %s" % " · ".join(sorted(by[code], key=int)[:100]))
        L.append("")
    OUT.write_text("\n".join(L), encoding="utf-8")
    print()
    print("★ ⇒ %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
