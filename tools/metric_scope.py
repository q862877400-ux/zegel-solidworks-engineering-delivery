"""★ 指标的「口径」注册表 —— 口径必须落成可复现代码，不能只写在散文里。"""

# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/metric_scope.py
# 定位:   **规格 206 的 T0 交付** —— 把我这一路报过的每个百分比，连同它的
#         「口径 / 分母 / 归一化层级 / **什么不算命中** / 排序确定性 / 语料版本」一起落成代码。
# 依据:   `specs/206-c1c6-harvest/spec.md` 的 SC-5 与 D-4；
#         `docs/known-facts.md` **事实 517**（支线 C1–C6 三条定则：
#         口径没写死 · 判据比结论宽 · 稳定性没验）。
# 官方依据: 不适用（本项目内部工具）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class MetricScope:
    """一个指标的**完整口径**。

    ★★ 设计要点（针对事实 517 的三条定则）：
      · 定则一「口径没写死」⇒ 口径是**结构化字段**，且本模块 `__main__` 会打印成块；
      · 定则二「判据比结论宽」⇒ 有 **`not_counted`（不算什么）** 这个必填字段；
      · 定则三「稳定性没验」⇒ 有 **`ordering`** 字段，且 `stable_topk()` 把顺序钉死。
    """

    key: str  #: 指标标识（进 JSON 用）
    question: str  #: ★ 它回答的问题（一句话）
    unit: str  #: 计数单位（任务 / 工具 / 行 …）
    denominator: str  #: ★ 分母**是什么、多少**
    normalization: str  #: ★ 归一化层级（★ 支线 C1 的教训：层级差 4.5 个百分点）
    counts_as_hit: str  #: ★ 什么算命中
    not_counted: tuple  #: ★★ **什么不算命中**（判据的否定面）
    ordering: str  #: ★ 排序/取值的确定性保证
    corpus: str  #: 语料/目录的来源与版本
    known_limits: tuple = ()  #: ★ 如实声明的边界
    not_comparable_with: tuple = ()  #: ★★ **不能与哪些数并排比较**（★ 我犯过的错）

    def __post_init__(self) -> None:
        """★★ 缺了「不算什么」或「顺序」的口径**不许存在** —— 这是负例可证的门禁式约束。

        ★ 依据：事实 517 定则二（判据要写「不算什么」）与定则三（顺序必须钉死）。
        ★★ 设计成**构造期就抛**，而不是靠 reviewer 事后发现 —— 一个能被绕过的约定不是约定。
        """
        problems = []
        if not (self.not_counted or ()).__len__():
            problems.append("`not_counted`（不算什么）为空")
        if not (self.ordering or "").strip():
            problems.append("`ordering`（顺序声明）为空")
        if not (self.denominator or "").strip():
            problems.append("`denominator`（分母）为空")
        if problems:
            raise ValueError("口径 [%s] 不合格：%s" % (self.key, "；".join(problems)))
        for f in self.not_counted:
            if not str(f).strip():
                raise ValueError("口径 [%s] 的「不算什么」里有空条目" % self.key)

    def block(self) -> str:
        """★ 打印块 —— 任何头条数字旁边都必须打这个。"""
        lines = [
            "── 口径 [%s] ──" % self.key,
            "   问题   : %s" % self.question,
            "   单位   : %s" % self.unit,
            "   分母   : %s" % self.denominator,
            "   归一化 : %s" % self.normalization,
            "   算命中 : %s" % self.counts_as_hit,
            "   ★不算  : %s"
            % ("；".join(self.not_counted) or "（未声明 —— 这本身是缺陷）"),
            "   顺序   : %s" % self.ordering,
            "   语料   : %s" % self.corpus,
        ]
        if self.known_limits:
            lines.append("   限度   : %s" % "；".join(self.known_limits))
        if self.not_comparable_with:
            lines.append("   ★不可比: %s" % "；".join(self.not_comparable_with))
        return "\n".join(lines)

    def as_dict(self) -> dict:
        d = dict(self.__dict__)
        d["not_counted"] = list(self.not_counted)
        d["known_limits"] = list(self.known_limits)
        d["not_comparable_with"] = list(self.not_comparable_with)
        return d


#: ★★ 口径注册表 —— 我这一路报过的每一个数，都要在这里有一条
SCOPES: tuple = (
    MetricScope(
        key="bm25_topk",
        question="用朴素 BM25 检索，我标注的期望工具落在 top-k 里的比例是多少（★ 手写题批）",
        unit="任务",
        denominator="★ **两批，不可相减、不可混报**：早期批 **24** 条手写题；分层批见 `bm25_topk_stratified`",
        normalization="tokenizer 已修（★ 字符类不含 `_`，snake_case 被切开）",
        counts_as_hit="`rank(期望工具) <= k`，k ∈ {1,3,5,10}（★ 报数必须写明 k）",
        not_counted=(
            "★ 返回了但**不是**期望工具的那些结果，一律不算（★ 这是**召回**口径，不是**正确性**口径）",
            "★ 期望工具是**我标的** ⇒ 我标错则本条判据失效",
            "★ **未报的 k 不算**（只报 top-5 时，不得据它推断 top-1/top-10 的水平）",
        ),
        ordering="按 (-score, tool_name) 排序 —— ★ 同分用名字码点升序钉死",
        corpus="`register_capabilities.all_specs()`（当期 433 个 ToolSpec）",
        known_limits=(
            "题面由我手写 ⇒ 我自己的措辞偏倚未消除",
            "★ 百分比未声明取整方式（本轮按四舍五入到整数报）",
        ),
        not_comparable_with=(
            "★ `model_pick_correct` —— 那量的是「挑出来的对不对」，与本条的「召回」不同口径",
            "★ `lens_replica_topk` —— 检索器不同",
            "★★ `name_reverse_lookup` —— 那是**工具**口径且**近乎同义反复**，不得与任务口径并列",
            "★★ `bm25_topk_stratified` —— 分母是分层抽样的 48 题，与本条的 24 条**不可相减**",
        ),
    ),
    MetricScope(
        key="bm25_topk_stratified",
        question="在同一份 BM25 上换成**分层抽样的 48 题**（冷门/薄文档/自研层/热门各一档），召回是多少",
        unit="任务",
        denominator="★ 分层批 **48** 题（各格样本：C1 冷门 18 · C2 薄文档 2 · C3 自研 18 · H 热门 10）",
        normalization="同 `bm25_topk`（同一 tokenizer、同一目录）",
        counts_as_hit="`rank(期望工具) <= k`，k 与每格 n **必须同时报**",
        not_counted=(
            "★ 同 `bm25_topk`：不是期望工具的返回不算",
            "★★ **样本过小的格不下结论** —— C2 只有 2 题，它的百分比**不得**被当成该层的水平",
            "★ 未报 k 的档不算",
        ),
        ordering="按 (-score, tool_name) 排序；★ 分层内的汇总也按层键升序，不依赖 dict 迭代序",
        corpus="同一份 433 个 ToolSpec；题面为 Bunny 写的中文查询（独立产出者）",
        known_limits=(
            "★ 48 路里 34 路产出成功（覆盖 68 个工具），后按 48 题重抽 ⇒ 部分是子集",
            "★ 分层是按「是否出现在中文清单 / 域大小」机械分的，不代表真实使用频率",
        ),
        not_comparable_with=(
            "★★ `bm25_topk` 的 24 条手写批 —— 分母不同，**不可相减**",
            "★ `model_pick_correct` —— 同题面但**机制不同**（有检索器 vs 模型自己挑）",
        ),
    ),
    MetricScope(
        key="name_reverse_lookup",
        question="把工具名去掉前缀下划线换空格当作查询，能不能命中该工具自己（★ 工具口径）",
        unit="工具",
        denominator="当期 433 个 ToolSpec",
        normalization="`name.removeprefix('solidworks_').replace('_', ' ')`",
        counts_as_hit="排名 <= k",
        not_counted=(
            "★★ **它不构成任何召回/可用性证据** —— 用工具自己的名字查它自己，**近乎同义反复**",
            "★ 它只证明「工具面自洽：没有结构上找不到的工具」这一点",
        ),
        ordering="按 (-score, name) 排序",
        corpus="同一份 433 个 ToolSpec",
        known_limits=("★ 该口径的高命中率是**构造使然**，不是质量指标",),
        not_comparable_with=(
            "★★ **任何任务口径的召回或正确率** —— 单位不同（工具 vs 任务），且是同义反复",
        ),
    ),
    MetricScope(
        key="lens_replica_topk",
        question="换成 dsh-mcp-lens 的检索算法，同一批任务的 top-k 召回是多少",
        unit="任务",
        denominator="同一批 24 / 48 条任务",
        normalization="照抄其口径：NFKC → 驼峰切 → `[\\p{L}\\p{N}]+`；中文=整块 Han+相邻二元组；无 tf/k1",
        counts_as_hit="`rank(期望工具) <= k`",
        not_counted=(
            "★ 同 `bm25_topk`：不是期望工具的返回不算",
            "★ **不等于**「lens 在它自己的 1000 工具 fixture 上的表现」—— ★ fixture 是**合成的**",
        ),
        ordering="按 (-score, name) 排序；★ 其公式的 `/sqrt(词数)` 对所有文档同值 ⇒ 不影响排序",
        corpus="同一份 433 个 ToolSpec；算法逐字复刻自 `src/catalog.ts::searchCatalog`",
        known_limits=(
            "★ 复刻基于**他人调研抽出的公式**（该公式已用其真实 trace 的 score 反算校验）",
            "★ 字段贡献用 `name` 时我去掉了 `solidworks_` 统一前缀 ⇒ ★ 若有偏，是**偏向 lens**（给了它更干净的名字）",
        ),
        not_comparable_with=(
            "★ `bm25_topk` 只在同语料同题面上可比（本表已同语料同题面）",
        ),
    ),
    MetricScope(
        key="model_pick_correct",
        question="真模型自己挑的工具，**到底对不对**（不是「有没有挑到我标的那个」）",
        unit="任务",
        denominator="★ **有效 47 / 回收 48**（48 路里 1 路失败；另 1 组自报看不见工具清单 ⇒ 已排除）",
        normalization="判档四值 yes / partial / no / cannot_tell；★ 主判 A + 复核 B，两判独立",
        counts_as_hit=(
            "★ **盲判裁判判 `yes`**（= 这个工具**就是**用来做这件事的）；"
            "★★ 分三个**各自命名**的口径报：「主判 A」「复核 B」「前二≥1」（首选或备选里至少一个 yes）"
            " —— ★ 三者**不得合并或并列**成一个数"
        ),
        not_counted=(
            "★ `partial` **不算**命中（只做一部分/要配合别的工具）",
            "★ `cannot_tell` **不算**命中",
            "★ **挑到我标的期望工具**不算命中 —— ★★ 判据是裁判的判定，不是我标的标签",
            "★ 多选题里「多工具任务」只给一个工具 ⇒ **结构性拿不到满分**，不算工具缺陷",
        ),
        ordering="按题号升序；★ 裁判候选**随机打乱**（去位置偏倚），按**工具名**对齐而非位置",
        corpus="任务文本来自 Bunny 写的中文查询（独立产出者）；候选工具的真实 title/doc 取自 ToolSpec",
        known_limits=(
            "★ 单轮、单模型、单次选择 —— **不是**多轮真实工作流的成功率",
            "★ 裁判是模型（2 个），不是人；两判对首选的**分歧 4%**",
            "★ 48 路里 1 路失败、1 组自报看不见清单 ⇒ 有效 47",
        ),
        not_comparable_with=(
            "★★ **任何检索器的 top-k** —— 本条是「模型读描述后自己选」，没有检索器参与",
        ),
    ),
    MetricScope(
        key="alias_gain",
        question="给工具追加别名后，用该别名当查询去检索，这个工具的排名提升多少",
        unit="工具",
        denominator="★ 机械筛后的 **52** 个工具（源自 C5 手核的 24 行「换名已有」→ 79 对 → 归并到 52 个工具）",
        normalization="同一 tokenizer、同一 433 工具面；★ 别名只在**内存里**追加（不碰 ToolSpec）",
        counts_as_hit="★ 排名数字（现状 rank → 加别名 rank）；「提升」= rank1 < rank0",
        not_counted=(
            "★★ **它不证明用户真的会这么说** —— 查询词就是被追加的那个别名本身，"
            "**结构上近似同义反复**（★ 与 `name_reverse_lookup` 同族缺陷）",
            "★ **不构成**任何「中文用户会怎么说」的证据（别名全是英文词）",
            "★ 变差的一律不采纳（本批 0 个变差）",
            "★ 无变化的（7 个）**不采纳** —— 别名挣不到它的字节",
        ),
        ordering="按 (-gain, tool_name) 排序 —— ★ 同分用名字码点升序钉死",
        corpus="别名取自 `c5-gap-handcheck.json`（另一个对话的手核，只读复用）里 `op` 与 `keys` —— "
        "★ 那些词来自**四家外部开源项目各自的工具名**，不是本仓编的",
        known_limits=(
            "★ 缓解证据仅到「四个独立团队都这么命名 ⇒ 是该领域自然用词的弱到中等证据」",
            "★ 本批未做中文别名（无真实中文语料）",
        ),
        not_comparable_with=(
            "★★ `bm25_topk` / `model_pick_correct` 等**任务口径**的召回或正确率 —— 本条是**工具口径**的机制验证",
            "★ `name_reverse_lookup` —— 同族（都是拿被测对象自己的词去查它），**不得叠加引用当两个证据**",
        ),
    ),
    MetricScope(
        key="zero_han_surface",
        question="有多少个工具的**模型可见文本**完全不含汉字（中文查询对它词元重叠恒为 0）",
        unit="工具",
        denominator="`all_specs()` 的全部工具（当期 433）",
        normalization="L0 原样；★ 判据是 `[\\u4e00-\\u9fff]` 正则命中数 == 0",
        counts_as_hit="`name + title + doc` 三处**都没有**汉字",
        not_counted=(
            "★ `params` / 参数说明里的汉字**不算**（★ 支线另一路实测：若把 schema 算进来，"
            "零汉字者由 205 降到 161 ⇒ ★ 两个口径都成立但**数不同**，引用必须写明口径）",
        ),
        ordering="不涉及排序（是计数）",
        corpus="`register_capabilities.all_specs()`（当期 433 个 ToolSpec）",
        known_limits=(
            "★ 未含上游 `server.py` 的 45 个工具 ⇒ ★ 真实模型可见面是 **433+45**，"
            "★ 我曾把它说成 433 ⇒ **已更正**",
        ),
        not_comparable_with=(
            "★ 与支线那路报的 `161 / 37.2%` **不同口径**（它们算了 schema）",
            "★★ `official_term_alignment` 的 90.8% —— 那的分母是 **273**（能取到官方成员名者），"
            "本条的 47.3% 分母是 **433**，★ 两者**不得并列**成「工具面健康度」（★ 裁判 A 点名）",
        ),
    ),
    MetricScope(
        key="official_term_alignment",
        question="工具面（名字+标题+描述）与它调的**官方 COM 成员名**有没有词交集",
        unit="工具",
        denominator="能取到官方成员名的 273 个（其余 156 个取不到 ⇒ 本条判据对它们**不适用**）",
        normalization="两侧都做驼峰切 + 下划线切 + 小写；按**集合交集**判",
        counts_as_hit="交集非空",
        not_counted=(
            "★★ **本指标与检索命中率几乎无关** —— 官方成员名**不在模型可见面上**（模型只看到工具名/描述/参数）",
            "★ 抽取器抓到平凡成员（`Name` / `__len__`）或报告类工具时，**不构成「命名错」** —— 那是量法 artifact",
            "★ **平凡单共词**（如 `name` / `get` / `set`）造成的交集**不算语义对应**（★ 两条路裁判都点了这一条）",
        ),
        ordering="不涉及排序（是计数）",
        corpus="`all_specs()` 的 `module`+`function` → `scripts/<module>.py` 函数体内的字符串实参",
        known_limits=("★ 只判**词面**对应，不判**语义**对应",),
        not_comparable_with=("★ 任何检索/选择正确率 —— 因果链不成立，我曾据此被误导",),
    ),
)

#: ★ 本条口径模块的自我声明：它**不**声称能做什么
COVERAGE_NOTE = (
    "★ 本模块只做两件事：① 把口径**结构化落盘**；② 把「取前 k」的顺序**钉死**。"
    "★ 它**不**重算任何指标（重算由各探针自己做），也**不**判任何结论的对错。"
)


def block_for(key: str) -> str:
    """★ 取某条口径的打印块 —— 探针里任何头条数字旁边都该调它。"""
    for s in SCOPES:
        if s.key == key:
            return s.block()
    raise KeyError("口径注册表里没有 %r（★ 先在这里登记，再报数字）" % key)


def stable_topk(rows, k: int = 10, key=None, name=None) -> list:
    """★ 固定顺序取前 k —— 主键降序、次键**名字码点升序**。

    ★★ 为什么需要它：支线 C5 的事故是「从 `set` 迭代序里取 `exact[0]`」⇒
    **约三成对应关系不可复现**（换 `PYTHONHASHSEED` 就变）。
    ⇒ 凡是从集合里「取一个」的地方，都要**固定顺序** ✓
    """
    key = key or (lambda r: r[0])
    name = name or (lambda r: r[1])
    return sorted(rows, key=lambda r: (-key(r), str(name(r))))[:k]


def dump(path: Path | None = None) -> dict:
    """★ 导出全部口径（供 `output/metric-scope-report.json`）。"""
    d = {
        "coverage_note": COVERAGE_NOTE,
        "n_scopes": len(SCOPES),
        "scopes": [s.as_dict() for s in SCOPES],
    }
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    return d


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("★ 指标口径注册表 · **%d** 条" % len(SCOPES))
    print(COVERAGE_NOTE)
    for s in SCOPES:
        print()
        print(s.block())
    print()
    print("★ 共性自查（★ 事实 517 的三条定则）:")
    miss_not = [s.key for s in SCOPES if not s.not_counted]
    miss_ord = [s.key for s in SCOPES if not s.ordering]
    print("   · 「不算什么」缺失的: %s" % (miss_not or "**无** ✓"))
    print("   · 排序声明缺失的  : %s" % (miss_ord or "**无** ✓"))
    print(
        "   · 声明了「不可比」的: %d / %d 条"
        % (sum(1 for s in SCOPES if s.not_comparable_with), len(SCOPES))
    )
    out = ROOT / "output" / "metric-scope-report.json"
    dump(out)
    print("★ 已导出: %s" % out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
