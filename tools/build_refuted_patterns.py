"""★ 建 `docs/refuted-patterns.json` —— ★ 让 `GATE-FINAL` 的 **C8** 真有可读对象。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   tools/build_refuted_patterns.py
# 定位:   ★ 阶段 1 的 A-3：★ 给 `GATE-FINAL` 的 C8 建「可读对象」。
#   ★★ C8 的判据逐字是：「`docs/refuted-patterns.json` 里每条的 `anchor_quote`
#      **必须逐字出现在 `docs/known-facts.md` 中**」⇒ ★ 所以本表**每条都逐字抄事实表**✓
#   ★★★ 而**为什么原来没有这张表**：★ 2026-10-04（接手轮）的 A-3 查出
#     —— ★ C8 自称「唯一常驻硬门禁」，★ **而它唯一依据的这个文件当时在仓里不存在**
#     ⇒ ★ 那条闸**没有可读对象、永远「通过」**（★ 与**事实 40**「存在但没人用的守卫」同族）✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(Path(__file__).resolve().parents[1])
sys.stdout.reconfigure(encoding="utf-8")
OUT = REPO / "docs" / "refuted-patterns.json"
FACTS = REPO / "docs" / "known-facts.md"

#: ★★★ 收录标准：★ 每条都是「**曾经被当成对的、后来被真机或复核推翻**」的东西 ——
#:   ★ 不是「注意事项」，★ 而是**已付出代价的记录** ✓
#: ★★ `anchor_quote` **必须逐字出现在 `known-facts.md` 里**（★ C8 就是核这个）✓
PATTERNS = [
    {
        "id": "name-only-matching",
        "claim": "★ 按**成员名**在官方表里查，就能判断一个成员是否废弃（一度以为可以）",
        "refuted_by": "★ 真机 + 官方页复核：同名成员**散在多个接口上**（事实 511）",
        "anchor_quote": "**事实 511**",
        "cost": "★ 一次扫描报出 870 处命中，头几名全是假阳性",
        "prevention": "★ 判据必须带**接口**维度；本仓用「所有接口都废弃」的安全桶收窄 ✓",
    },
    {
        "id": "coverage-inflation-by-docstrings",
        "claim": "★ 抽取器从源码抽成员名 ⇒ 覆盖率 76.9% → 91.3%、判据 21.30% → 8.66%，一度以为是大成功",
        "refuted_by": "★ **抽查 6 个工具**：每一个都含同一批成员（都来自某个被每个模块 import 的通用帮手的 docstring）",
        "anchor_quote": "**覆盖率从 76.9% 涨到 91.3%",
        "cost": "★ 差一点把假象写进事实表；真值只有 85.9% / 20.94%",
        "prevention": "★ 覆盖率读数必须**先抽查样本**才可信（事实 512）；从源码抽名字要**剥 docstring** ✓",
    },
    {
        "id": "strip-comments-means-strip-comments",
        "claim": "★ 「剥注释」就是剥掉 `#` 后面的东西（一度以为一句话就完事）",
        "refuted_by": "★ **负例自检**回 `(False, True)`：那些「注释」其实是 **docstring 的正文**",
        "anchor_quote": "**事实 513**",
        "cost": "★ 这一件事改了五版，前四版全错",
        "prevention": "★ 「剥注释」要同时想清三样：`#` 注释 · **docstring** · 普通字符串字面量；且**必须用负例验一次** ✓",
    },
    {
        "id": "deprecated-means-broken",
        "claim": "★ 官方标了 `Obsolete` 的成员，就该换掉（一度当成规则）",
        "refuted_by": "★ 真机逐条对照：`FeatureFillet(7 参)` **真的建成了**，而它的后继 `FeatureFillet3(15 参)` **连调都调不通**",
        "anchor_quote": "**事实 514**",
        "cost": "★ 若按「废弃就换」批量改，会把能用的换成不能用的",
        "prevention": "★ 换之前问**两个可核的问题**：① 旧的现在能不能用？② 新的能不能**做到同一件事**？✓",
    },
    {
        "id": "newer-generation-same-signature",
        "claim": "★ 后继的签名只要看起来一样，就能直接替换（一度以为是纯改名）",
        "refuted_by": "★ 真机：`GetSystemValue3` 回的是**数组**（官方例子逐字 `dimValue_1(0)`），而旧的 `GetSystemValue2` 回**标量** ⇒ 直接 `float()` **会 TypeError**",
        "anchor_quote": "**事实 514**",
        "cost": "★ 一族的命名升级**顺手也改了返回形态**，而签名页看不出来",
        "prevention": "★ 凡从属性/旧方法换到 `Get*2` / `Get*3` 家族，都要问「**它回标量还是数组？**」✓",
    },
    {
        "id": "guard-exists-means-guard-works",
        "claim": "★ 代码里有一个检查，就等于防住了（一度这么以为）",
        "refuted_by": "★ 真机：`_coerce_dispatch` **除 `None` 外什么都放行**（对 bound method，`Dispatch()` 失败后 **`return value` 原样返回**）",
        "anchor_quote": "**事实 40**",
        "cost": "★ 它让 `_get_pack_and_go` 把 **bound method 当对象**返回，而调用方看不出来",
        "prevention": "★ 「一个**存在但没人用**的守卫与没有守卫等价，**且更糟**」；守卫**必须被负例证伪过**才算守卫（事实 62）✓",
    },
    {
        "id": "whitelist-of-forms",
        "claim": "★ 枚举已知的几种写法就能覆盖全部（一度只在判据里列三种）",
        "refuted_by": "★ 实测本仓有 **6 种** `*com_member` 写法（`get_` · `set_` · `call_` · `safe_get_` · `_safe_` · `_optional_`）⇒ 旧判据**漏 63 处**",
        "anchor_quote": "**事实 511**",
        "cost": "★ 整个工程图族被算成抽不到成员，而矩阵据此把它们列成低密度格",
        "prevention": "★ 凡「认若干种已知写法」的判据，都要问「**有没有一个形态能覆盖全部**」✓",
    },
    {
        "id": "totals-match-details",
        "claim": "★ 一个脚本**打印的**总数与它**存下的**明细是同一个数（一度以为只是两处读法不同）",
        "refuted_by": "★ 真因是 `[...][:30]` **截断**：**打印 52、存 30**",
        "anchor_quote": "**事实 513**",
        "cost": "★ 我据此得出了「两个来源不一致」的**错误结论**，而它们读的是同一份数据",
        "prevention": "★ **总数**与**明细节数**要**同时可见**；若必须截断，要显式写明「前 N 个，共 M 个」✓",
    },
    {
        "id": "same-family-same-verdict",
        "claim": "★ 同一个接口上的同一族废弃成员，处置结论应当一样（一度按族排期）",
        "refuted_by": "★ 真机：`FeatureFillet` **旧的做到了**，而同族的 `FeatureLinearPattern3` **旧的做不到** ⇒ 两条结论相反",
        "anchor_quote": "**事实 514**",
        "cost": "★ 按族批量下结论会把两条相反的结论压成一条",
        "prevention": "★ **逐条真机判**；不许按族批量下「能/不能」的结论 ✓",
    },
    {
        "id": "scan-scope-equals-repo",
        "claim": "★ 扫 `scripts/` 与 `mcp-server/` 就等于扫了全部实现（一度以为如此）",
        "refuted_by": "★ `scripts/sw_drawing.py` 是一个**动态桥接**（29 行、`^def` 匹配 0 个），真现在 `subskills/solidworks-engineering-drawing/scripts/` 下",
        "anchor_quote": "**事实 51**",
        "cost": "★ 整个工程图族（30+ 工具）抽到的成员近 0，矩阵据此把它们列成低密度格",
        "prevention": "★ 扫描范围**本身是一个判据**：问「**这个仓库还有没有别的地方放着实现**」✓",
    },
]


def main() -> int:
    facts = FACTS.read_text(encoding="utf-8", errors="replace")
    bad = [p["id"] for p in PATTERNS if p["anchor_quote"] not in facts]
    payload = {
        "schema": "refuted-patterns/1",
        "note": "★ 本表给 GATE-FINAL 的 C8（唯一常驻硬门禁）提供**可读对象**。"
        "★ C8 的判据逐字是：本表里每条的 `anchor_quote` **必须逐字出现在 "
        "docs/known-facts.md 中**。",
        "why": "★ 2026-10-04（接手轮）的 A-3 查出：C8 自称「唯一常驻硬门禁」，"
        "而它唯一依据的这个文件**当时在仓里不存在** ⇒ 那条闸**没有可读对象、永远通过**"
        "（与**事实 40**「存在但没人用的守卫」同族）✓",
        "inclusion": "★ 每条都是「**曾经被当成对的、后来被真机或复核推翻**」的东西 —— "
        "不是注意事项，而是**已付出代价的记录** ✓",
        "patterns": PATTERNS,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print("★ 写出", OUT)
    print("★ 条数:", len(PATTERNS))
    print(
        "★ 自校（anchor_quote 逐字命中 known-facts.md）:",
        "★ 全部通过 ✓" if not bad else bad,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
