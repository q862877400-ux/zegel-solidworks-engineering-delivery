"""★ 门禁：评审稿里引用的 `L1-/L2-/L3-` 编号必须**真的存在**，且括号里的描述要对得上。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/check_review_ids.py
# 定位:   规格 `specs/315-eval-corpus` 的**评审稿编号门禁**。★★ 实测（2026-10-12，业主
#           指出）：`owner-review.md` §5「我明确不确定的 6 条」里，**4 条引错了编号** ✗
#           ——  · 写 `L3-025`（鼠标外壳），实际 `L3-025` 是「台式平口钳」  · 写 `L3-031`
#           （梯形螺纹），实际是「给我建一个零件」  · 写 `L3-050`（换个材料），实际是「
#           安装板 + 机架」  · 写 `L3-060`（好看的），实际是「换另一种材料」★ 而**括号里
#           的描述是对的**、**编号全错** ⇒ ★ 那正是「**看起来像 A，其实是 B**」—— ★ 业主
#           照着编号去翻，★ 翻到的会是**另一条**，★ 于是他会以为自己看错了。
# 官方依据: `corpus/l1-mainline.yaml` · `l2-longtail.yaml` · `l3-semantic.yaml`
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ⚠ 等级 `verified`：★ 本门禁**用真数据自证**（★ 见 `selftest()` —— 它拿
#   修复前的错编号当负例，★ 必须报出来）。
# -----------------------------------------------------------------------------
from __future__ import annotations

import pathlib
import re

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
REVIEW = ROOT / "specs" / "315-eval-corpus" / "owner-review.md"
CORPUS = ("l1-mainline.yaml", "l2-longtail.yaml", "l3-semantic.yaml")

#: ★★ **「编号 + 括号描述」的引用形态**（★ 评审稿里到处是这种写法）
#:   例：`**3. L3-037**（鼠标外壳）：……` 或 `**L1-002** | 板上四角打 4 个 M6 孔`
REF = re.compile(r"(L[123]-\d{3})\*\*（([^）]{2,40})）")

#: ★ 描述对不上时**允许**的宽容度：★ 描述里任一段（按标点切）出现在需求里即可
SPLIT = re.compile(r"[，,、/＋+ ]+")

#: ★★ **明显的编号错**（★ 本门禁真正要抓的那一类）——
#:   ★ 判据：**描述里的关键词**一个都不在需求里 ⇒ 报。
#:   ⚠ 实测（2026-10-12）：第一版用「任一段是子串」⇒ ★ **概括性描述**
#:     （「换个材料」vs「用另一种材料」）被**误报** ✗ ——
#:     而误报会让门禁变成噪声、被人关掉。
#:   ⇒ ★ 判据改成**关键词命中**：★ 描述里的**实词**（≥2 字的汉字块）
#:     **至少一个**出现在需求里 ⇒ 放过；★ **一个都没有** ⇒ 报。
HAN = re.compile(r"[\u4e00-\u9fff]{2,}")


def _keywords(s: str) -> set:
    """★ 取实词 —— ★ **滑动 2-gram**（★ 连续 2 个汉字的所有窗口）。

    ⚠ 实测（2026-10-12）：第一版取**最长连续汉字串**当关键词 ⇒
      ★ 「真实梯形螺纹」被当成**一个** 6 字关键词
      ⇒ ★ 而需求是「给零件做**真实的**梯形螺纹几何」（中间多一个「的」）
      ⇒ ★ **匹配不上** ✗（★ 误报）。
    ⇒ ★ 判据改成 **2-gram 滑窗**：★ 「真实梯形螺纹」→
      {真实, 实梯, 梯形, 形螺, 螺纹} ⇒ ★ 「螺纹」命中 ✓
      ★ 这样对**中间插字**免疫（★ 而"插字"正是概括性描述的常态）。
    """
    out = set()
    for run in HAN.findall(s.replace("★", " ")):
        if len(run) == 2:
            out.add(run)
        else:
            out |= {run[i : i + 2] for i in range(len(run) - 1)}
    return out


def _matches(claim: str, requirement: str) -> bool:
    """★ 描述与需求**对不对得上**。

    ★ 判据（★ 2-gram 命中）：描述里**任一** 2-gram 在需求里出现 ⇒ 算对上。
    ★★ 为什么不用「整串相等」：★ 描述常是**概括**
      （「鼠标外壳」vs「给我建模一个鼠标外壳」）⇒ ★ 整串相等会把**对的说成错的**。
    ★★ 为什么 2-gram 够用：★ 本门禁要抓的是**编号错到另一条去了**
      （★ 描述与需求**毫无共同词**），★ 而不是措辞差异。
    """
    c = claim.replace("「", "").replace("」", "").strip()
    if c in requirement or requirement in c:
        return True
    kws = _keywords(c)
    if not kws:
        return False
    return any(k in requirement for k in kws)


def corpus() -> dict:
    """★ 读三份语料 ⇒ `{id: 需求文字}`。

    ⚠ 实测（2026-10-12）：三份语料的**字段名不一样** ——
      ★ L1 `task` · L2 `task` · L3 `requirement`
      ⇒ ★ 第一版只取 `requirement` ⇒ 读到 L1 就 `KeyError` ✗
      （★ 而「字段名不一致」看起来像「语料坏了」）。
    """
    out = {}
    for name in CORPUS:
        p = ROOT / "corpus" / name
        if not p.is_file():
            continue
        for x in yaml.safe_load(p.read_text(encoding="utf-8")):
            text = x.get("task") or x.get("requirement") or ""
            if x.get("id") and text:
                out[x["id"]] = text
    return out


def check(path: pathlib.Path = REVIEW) -> list:
    """★ 返回问题列表（★ 空 = 过）。"""
    if not path.is_file():
        return ["★ 没有 %s" % path]
    cps = corpus()
    text = path.read_text(encoding="utf-8")
    problems = []
    seen = 0
    for m in REF.finditer(text):
        qid, claim = m.group(1), m.group(2)
        seen += 1
        if qid not in cps:
            problems.append("★ %s **不存在**（★ 引用了不存在的编号）" % qid)
            continue
        if not _matches(claim, cps[qid]):
            problems.append(
                "★★ %s 的描述「%s」与它的需求「%s」对不上 ⇒ 编号或描述有一个错了"
                % (qid, claim, cps[qid])
            )
    #: ★★ 另一类：**裸编号**（没有括号描述）—— 只核存在性
    for m in re.finditer(r"`(L[123]-\d{3})`", text):
        qid = m.group(1)
        seen += 1
        if qid not in cps:
            problems.append("★ `%s` **不存在**（★ 反引号形态）" % qid)
    return problems


def selftest() -> bool:
    """★★ **负例自证**（★ 事实 62：门禁「写了」不等于「有效」）。

    ★ 判据：把**修复前的错编号**当输入 ⇒ 门禁**必须**报出来。
    """
    cps = corpus()
    #: ★ 修复前 §5 那 4 条（★ 编号错、描述对）
    before = [
        ("L3-025", "鼠标外壳"),
        ("L3-031", "真实梯形螺纹"),
        ("L3-050", "换个材料"),
        ("L3-060", "随便做个好看的"),
    ]
    caught = 0
    for qid, claim in before:
        if qid not in cps or not _matches(claim, cps[qid]):
            caught += 1
    if caught != 4:
        print("★★ 负例自证失败：修复前的 4 条错编号只抓到 %d 条" % caught)
        return False
    #: ★ 修复后（★ 正确编号）⇒ **不该**报
    after = [
        ("L3-037", "鼠标外壳"),
        ("L3-046", "真实梯形螺纹"),
        ("L3-060", "换个材料"),
        ("L3-053", "随便做个好看的"),
    ]
    bad = [(q, c) for q, c in after if q not in cps or not _matches(c, cps[q])]
    if bad:
        print("★★ 负例自证失败：修复后的正确编号被误报 %s" % bad)
        return False
    return True


def main() -> int:
    problems = check()
    print("★ 评审稿编号门禁 · 语料 %d 条" % len(corpus()))
    if not selftest():
        return 1
    print("★ 负例自证：过（★ 修复前的 4 条错编号都抓到了）")
    if problems:
        print("★★ 发现 %d 处：" % len(problems))
        for p in problems:
            print("   %s" % p)
        return 1
    print("★ [PASS] 评审稿里的编号引用全部对得上")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
