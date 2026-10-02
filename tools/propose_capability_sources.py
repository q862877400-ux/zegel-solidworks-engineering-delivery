r"""@brief 为 `capabilities[].source` 生成**有证据的提案**（不写文件，只打印）。

## 为什么不能直接写
已知事实 41 记着：A2 的真实缺口是「**29 条里 28 条未被分类**」，
而 `THIRD-PARTY-NOTICES.md` 自己警告过：
> 「把未并入的东西写成已并入，是**归属造假**，比遗漏更严重。」

**⇒ 所以本工具**只生成提案 + 附证据**，**不写任何文件**。**采纳与否由人定。**

## 证据链（每一环都是**可机械核验**的，不是判断）
```
① `capabilities[].id` / `label`  →  **关键词**
② `C:\swprojects\sw-skill-fork\scripts\*.py` 的文件名 / docstring  →  关键词命中 ⇒ **候选实现模块**
③ `git diff --name-only origin/main`  →  该模块是**上游就有**还是**我们新增的**（硬证据）
⇒ 判定：
   · 命中的模块**全在上游** ⇒ `source: upstream`（并入自 wyzn20051216/...）
   · 命中的模块**全是我们新增** ⇒ `source: original`
   · **混有两者** ⇒ `source: mixed`（**并列出两侧文件**）
   · **一个都没命中** ⇒ `source: undetermined`（**不猜**）

⚠ 关键词匹配**不是**归属证明 —— 它只是把「该看哪些文件」缩小到可人工复核的范围。
⚠ **收紧过两轮**：第一版用 `solidworks` 作关键词 + 扫文件体 ⇒ 某条命中 **87 个模块**、另一条
  只命中明显无关的 `dxf_preview_scene.py`。**⇒ 泛词丢弃 + 只按主干匹配。**
   **⇒ 输出里会把命中的文件名逐个列出**，供人核对。
```

# ── 来源 ──
# 仓库:   本项目自身（静态分析工具）
# 文件:   `capabilities.yaml`（`schema_version` 2.0，29 条 capability）
#         `scripts/*.py`（文件名与 docstring 里的关键词）
#         `git diff --name-only origin/main`（新增文件清单 —— 硬证据）
# 定位:   已知事实 41 的后续：A2 缺的是**分类标记**，而分类要靠证据。
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 纯静态（读文件 + 跑 `git diff`），**不连 SolidWorks**，**不写任何文件**。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(r"" + _ROOT_S + r"")
CAPS = REPO / "capabilities.yaml"


def upstream_files() -> set:
    """`origin/main` 上存在的 `scripts/*.py`（**硬证据**）。"""
    try:
        out = subprocess.run(
            ["git", "-C", str(REPO), "ls-tree", "-r", "--name-only", "origin/main"],
            capture_output=True, text=True, encoding="utf-8", timeout=120,
            stdin=subprocess.DEVNULL)
    except Exception:  # noqa: BLE001
        return set()
    return {Path(l.strip()).name for l in (out.stdout or "").splitlines()
            if l.strip().startswith("scripts/") and l.strip().endswith(".py")}


def our_files() -> list:
    return sorted(p for p in (REPO / "scripts").glob("*.py"))


#: 太泛的词 —— 它们会命中大半个仓库，**没有区分力**。
#: ⚠ 这是收紧匹配的关键：第一版用 `solidworks` 作关键词 ⇒ 命中 **87 个模块**。
GENERIC = {
    # ⚠ **`part` 不在泛词表里** —— 它对 `sw_part.py` 是强信号（第一版误列过）。
    "solidworks", "solidworks-com", "local", "python", "host", "addin",
    "features", "geometry", "general", "standard", "external", "updates",
    "local-python", "headless", "occt", "com", "sw", "skill", "tools",
}


def keywords(cap: dict) -> list:
    """从 id / label 生成关键词。

    ⚠ **第一版太松**：`solidworks` 这种词命中全仓 ⇒ 本版加两道闸：
      ① 丢掉 :data:`GENERIC` 里的泛词；② 只保留长度 >= 5 的英文词。
    """
    kws = set()
    for part in re.split(r"[_\s/与和的]+", cap["id"]):
        w = part.lower()
        # ⚠ 闸门 **4**（不是 5）：`part`/`mold` 都是 4 字符，且不在 GENERIC ⇒ 有区分力。
        #   第一版设 5 ⇒ `part_and_features` / `mold_tools` 双双漏掉。
        if len(w) >= 4 and w not in GENERIC:
            kws.add(w)
    for chunk in re.findall(r"[\u4e00-\u9fff]{2,}", cap.get("label", "")):
        if chunk not in GENERIC:
            kws.add(chunk)
    return sorted(kws)


def _variants(k: str) -> list:
    """关键词的**词形变体**（单复数）—— 有原则的归一，不是逐个凑。

    ⚠ 第一版只按原词匹配 ⇒ `weldments` 匹配不到 `sw_weldment`、
      `drawings` 匹配不到 `sw_drawing`、`holes` 匹配不到 `sw_hole_features`。
    **⇒ 同时试「原词 / 去尾 s / 加尾 s」三种。**
    """
    out = {k}
    if k.endswith("s") and len(k) > 3:
        out.add(k[:-1])
    else:
        out.add(k + "s")
    return sorted(out)


def stems_only(kws: list, files: list) -> list:
    """**只按文件名主干**匹配（不再扫文件体）。

    ⚠ 第一版还扫了文件体 ⇒ 命中面进一步失控。**同名主干才是强信号。**
    """
    hits = []
    for f in files:
        stem = f.stem.lower()
        for k in kws:
            # 英文关键词：作为主干的**片段**出现才算（如 `gear` ⊂ `sw_gear`）
            if re.fullmatch(r"[a-z]+", k):
                if len(k) >= 4 and any(v in stem for v in _variants(k)):
                    hits.append(f.name)
                    break
            elif k in f.name:            # 中文：直接出现在文件名里
                hits.append(f.name)
                break
    return sorted(set(hits))


# ⚑ 2026-10-01（轮 136）：这里曾有一个 `match_modules(kws, files)` ——
#   它是 `stems_only()` 的**旧版**（会**扫文件体**，命中面失控），已被取代但**一直留着**。
#   `tools/probe_uncalled_helpers.py` 扫出它**在整个仓库里 0 次调用** ⇒ 删除。
#   ⚠ 留这条注释而不是无声删掉：**读代码的人该知道这里发生过什么**。


#: 收尾说明（**每行独立字符串**，见事实 48）
NOTES = (
    "⚠ **本工具不写任何文件。** 理由：关键词匹配**不是归属证明**。",
    "★ **已被抽查验证**（2026-10-01）：`topology_optimization`/`simulation_and_fea` → `original`、",
    "  `sheet_metal`/`weldments` → `upstream`、`routing` → `mixed`，**逐条与硬证据相符**。",
    "  **⚠ 并且它纠正了我的一个误认**：`sw_weldment.py` / `sw_sheet_metal.py` **是上游文件**",
    "  （`git cat-file -e origin/main:scripts/sw_weldment.py` 通过）—— 我此前当成「我们新增的」。",
)


def main() -> int:
    d = json.loads(CAPS.read_text(encoding="utf-8"))
    caps = d["capabilities"]
    up = upstream_files()
    ours = our_files()
    print("上游 `origin/main` 的 scripts/*.py: **%d** 个" % len(up))
    print("当前工作树的 scripts/*.py:        **%d** 个" % len(ours))
    print("⇒ 我们新增的: **%d** 个" % len({f.name for f in ours} - up))
    print()

    proposals = []
    for c in caps:
        kws = keywords(c)
        hits = stems_only(kws, ours)   # ⚠ 收紧：只按文件名主干
        on_up = [h for h in hits if h in up]
        new = [h for h in hits if h not in up]
        if not hits:
            src, why = "undetermined", "关键词一个都没命中 ⇒ **不猜**"
        elif on_up and not new:
            src, why = "upstream", "命中的模块**全在上游**"
        elif new and not on_up:
            src, why = "original", "命中的模块**全是我们新增**"
        else:
            src, why = "mixed", "两侧都有"
        proposals.append((c["id"], src, why, kws, hits, on_up, new))

    print("=" * 78)
    print("**提案**（⚠ 只打印、**不写文件**；采纳与否由人定）")
    print("=" * 78)
    for cid, src, why, kws, hits, on_up, new in proposals:
        print()
        print("  %-30s → **%s**   （%s）" % (cid, src, why))
        print("      关键词: %r" % (kws[:6],))
        if hits:
            print("      命中模块 %d 个（上游 %d / 新增 %d）:" % (len(hits), len(on_up), len(new)))
            for h in hits[:8]:
                tag = "上游" if h in up else "**新增**"
                print("        [%s] %s" % (tag, h))
            if len(hits) > 8:
                print("        … 另有 %d 个" % (len(hits) - 8))
        else:
            print("      命中模块: **无**")

    print()
    print("=" * 78)
    import collections
    dist = collections.Counter(p[1] for p in proposals)
    print("**分布**：" + " · ".join("%s=%d" % (k, v) for k, v in dist.most_common()))
    print()
    # ⚠ 事实 48 定则①：长内容用**独立文件**或**短的单行字符串**，
    #   不要在补丁里跨行拼接 —— 这一处正是踩过的那次。
    for _line in NOTES:
        print(_line)
    print("⚠ 「命中模块」只是把「该看哪些文件」缩小到可人工复核的范围。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
