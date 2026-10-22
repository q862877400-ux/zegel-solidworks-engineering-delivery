r"""@brief 生成 `docs/harvest-digest.md` —— **交付报告的状态摘要（生成段）**。

## 为什么需要一个**生成**的摘要（2026-10-01 轮 68）
`AGENTS.md §一 A8` 要求报告「写明**并入了什么、仍空缺什么、为什么空缺**」。
实测发现 `docs/harvest-report.md` 的 §二 正文写的是「**截至第 12 轮**」，
而**轮 13–68 的产出没有系统写进去**（全仓只有 13/54/63/67 四个零散引用）。

⚠ 但**再手写一份「轮 13–68 干了什么」会立刻腐坏**（本项目已多次记录：
手写状态表跟不上代码）。⇒ **改成本文件的做法：从真源生成。**

**数据源（都是硬依据，不是叙述）**：
1. `capabilities.yaml` —— 每条能力的 `level` / `source` / `evidence` / `limitations`
2. `git log` —— 提交数与主题分布（`feat` / `fix` / `docs` / …）
3. `scripts/check_*.py` + `scripts/release_check.py` —— 门禁栈
4. `docs/union-not-doing.json` —— 「不做 + 原因」（A1 的另一半）

**新鲜度**：`scripts/check_digest_freshness.py`（重跑本生成器 ⇒ 必须逐字节相同）。

# ── 来源 ──
# 仓库:   本项目自身（生成器，非第三方移植）
# 文件:   tools/gen_harvest_digest.py
# 定位:   承接 `AGENTS.md §一 A8`（报告要写「并入了什么 / 仍空缺什么 / 为什么」）
#         与 §五 第 4 步（标等级与出处）。**只读真源、只写一个生成物**。
# 官方依据: 不适用（本项目内部工具，不调 SolidWorks API）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "harvest-digest.md"
ANCHOR = "origin/main"

#: 五级能力枚举（与 `check_union_conventions.py` 的 `LEVELS` 同源口径；
#: 这里**复制常量而非 import**，因为生成器要能独立跑 —— 一致性由新鲜度门禁兜底）。
LEVEL_ORDER = ("verified", "source_verified", "stitched", "indexed", "not_implemented")


def _git(*args: str) -> str:
    p = subprocess.run(
        ["git", *args],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return p.stdout if p.returncode == 0 else ""


def _commits_at_head() -> int:
    """⇒ **已提交**的提交数（`HEAD`，**不含**尚未提交的改动）。

    ⚠⚠ **这里绕了一圈，值得记下来**（2026-10-01 轮 68 实测）：
      * **第一版**：直接数 `HEAD` ⇒ **每提交一次就滞后 1**（门禁永远 FAIL）；
      * **第二版**：借用 `check_report_freshness` 的「`git status` 非空就 `+1`」预测 ⇒
        **提交数对了，但「主题分布」照样滞后** —— 因为
        **digest 无法预测「生成它的那次提交」的主题是什么**（`feat`/`docs`/… 由人写）。
        实测：提交后 `feat` 从 **97 变 98** ⇒ 新鲜度门禁照样 FAIL。
      * **第三版（本函数）**：**放弃预测，全部基于 `HEAD`**，并把口径**写进生成物**：
        「**不含生成本文件的那次提交（自指）**」。
    ★ **根因是自指**：一个统计「提交构成」的产物，**无法把产生它自己的那次提交算进去**。
      强行预测只会得到一个**看起来新鲜、实际靠猜**的数字 —— 那正是本项目反复记录的坏做法。
    ⇒ 代价：digest **落后一次提交**（那一次就是提交 digest 自己的那次）—— **写明即可，不谎报**。
    ⇒ 流程：**先提交代码 → 再生成 digest → 再提交 digest**。
    """
    return int(_git("rev-list", "--count", f"{ANCHOR}..HEAD").strip() or 0)


def _display(path: Path) -> str:
    """把路径显示成「相对 ROOT」——**但 OUT 可能被指向临时目录**。

    ⚠⚠ **这是被门禁逼出来的修正**（2026-10-01 轮 68）：`check_digest_freshness.py`
      的手法是把 `OUT` 指到**临时路径**再跑一遍生成器（**绝不覆盖真文件**）。
      而我原先直接写 `OUT.relative_to(ROOT)` ⇒ 临时目录**不在 ROOT 下** ⇒
      `ValueError: … is not in the subpath of …` ⇒ **整条门禁崩掉**。
    ⇒ 定则：**生成器对「OUT 在哪」不能做假设**，因为它的调用者会改这个变量。
    """
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def main() -> int:
    raw = (ROOT / "capabilities.yaml").read_text(encoding="utf-8")
    caps = json.loads(raw)["capabilities"]
    not_doing = []
    nd_path = ROOT / "docs" / "union-not-doing.json"
    if nd_path.is_file():
        not_doing = (
            json.loads(nd_path.read_text(encoding="utf-8")).get("not_doing") or []
        )

    # ⚠ **不再统计主题分布**（`kinds` / `subjects` 已删）：见 §一 的说明 ——
    #   那类量**每提交一次就变**，而生成物要求逐字节可复现 ⇒ 放进来必然滞后（自指）。
    #   `n_commits` 只用于 **stdout 的进度提示**，**不进生成物**。
    n_commits = _commits_at_head()

    gates = sorted(p.name for p in (ROOT / "scripts").glob("check_*.py"))
    wired = (ROOT / "scripts" / "release_check.py").read_text(encoding="utf-8")

    item: list = []
    a = item.append
    a("# 交付状态摘要（**生成物**）")
    a("")
    a("> ⚑ **本节不要手改** —— 由 `tools/gen_harvest_digest.py` 从真源生成；")
    a("> 新鲜度由 `scripts/check_digest_freshness.py` 守（重跑必须逐字节相同）。")
    a(">")
    a(
        "> **为什么单独出一份**：`AGENTS.md §一 A8` 要求报告写「并入了什么 / 仍空缺什么 / 为什么」，"
    )
    a(
        "> 而 `harvest-report.md` 的 §二 正文停在「截至第 12 轮」。**手写续写会立刻腐坏** ——"
    )
    a("> 所以状态这部分**从真源生成**，报告本体只链接本文件。")
    a(">")
    a("> 数据源：`capabilities.yaml`（能力/等级/出处/证据）· `git log`（提交构成）·")
    a("> `scripts/check_*.py`（门禁栈）· `docs/union-not-doing.json`（不做 + 原因）·")
    a("> `docs/family-coverage.json`（官方接口族的**零调用缺口**，见 §4.3）。")
    a("")

    a("## 一 提交构成（**怎么看** —— 本节刻意不放假数字）")
    a("")
    a(
        "> ⚠⚠ **本节不放「提交数 / 主题分布」**（2026-10-01 轮 68 实测出的结论，值得记下来）："
    )
    a(
        "> 本文件是**生成物 + 新鲜度门禁**（重跑必须逐字节相同），而那两个量**每提交一次就变**，"
    )
    a("> 且**产生本文件的那次提交无法自计**（自指）。")
    a(">")
    a("> **走过的三条路，全部失败**：")
    a("> 1. 直接数 `HEAD` ⇒ 每提交一次**滞后 1**；")
    a("> 2. 借用「`git status` 非空就 `+1`」预测 ⇒ **提交数对了，主题分布照样滞后**")
    a(">    （生成器**无法预测**「生成它那次提交」的主题是 `feat` 还是 `docs`）；")
    a(
        "> 3. 「全部基于 `HEAD`」+ 写明口径 ⇒ **提交本文件后 `HEAD` 又变了** ⇒ 门禁照样 FAIL。"
    )
    a(">")
    a("> ★ **根因**：本文件的内容**依赖提交历史**，而它自己**会改变提交历史**。")
    a("> ⇒ **正解不是再换一种口径，而是不把易变量放进这个产物里** ——")
    a(">   **不靠预测去凑一个看起来新鲜的数字**（那正是本项目反复记录的坏做法）。")
    a("")
    a("**要知道提交构成，跑这两条**（数字永远是当下真的）：")
    a("")
    a("```bash")
    a("git rev-list --count origin/main..HEAD          # 相对上游的提交数")
    a(
        "git log --format=%s -400 | sed 's/(.*//;s/:.*//' | sort | uniq -c | sort -rn  # 主题分布"
    )
    a("```")
    a("")
    a(
        "> ⚑ 本项目**只做本地提交**，未推任何远端（见 `docs/union-not-doing.json` 的「对外发布」条）。"
    )
    a(
        "> ⚑ 报告本体的偏离数字（文件数 / 行数 / 提交数）由 `scripts/check_report_freshness.py` 用"
    )
    a(
        ">   **「`git add -a && git commit` 之后会变成什么」** 的口径守着 —— 那三个量**可预测**"
    )
    a(
        ">   （`git status` 非空就 `+1`），所以放报告正文是稳的；而**主题分布不可预测**，哪里都不放。"
    )
    a("")
    a("## 二 能力状态（硬依据：`capabilities.yaml`）")
    a("")
    a("共 **%d** 条能力。" % len(caps))
    a("")
    a("| `level` | 条数 | 含义 |")
    a("|---|---|---|")
    meaning = {
        "verified": "**有我们自己的运行证据**（`evidence` 非空）",
        "source_verified": "来源派生且有 provenance 四字段",
        "stitched": "已缝合，**缺我们自己的运行证据**",
        "indexed": "只登记了索引，未实现",
        "not_implemented": "明确未实现",
    }
    lv = Counter(c.get("level") for c in caps)
    for name in LEVEL_ORDER:
        if lv.get(name):
            a("| `%s` | %d | %s |" % (name, lv[name], meaning.get(name, "")))
    a("")
    a("| `source` | 条数 | 含义 |")
    a("|---|---|---|")
    smeaning = {
        "upstream": "上游 `wzyn20051216/solidworks-automation-skill`",
        "mixed": "多家来源混合",
        "original": "**本项目自研**（护城河域等）",
        "undetermined": "**归属未定**（按铁律 5 不猜）",
        "merged": "并入而来",
    }
    sc = Counter(c.get("source") for c in caps)
    for name, n in sc.most_common():
        a("| `%s` | %d | %s |" % (name, n, smeaning.get(name, "")))
    a("")

    a("## 三 `verified` 的逐条运行证据（**A4 的硬证据**）")
    a("")
    a(
        "`level: verified` 的定义是「**有我们自己的运行证据**」——不是「代码是我们写的」。"
    )
    a("下表逐条给出那条证据（可跑的命令 / 可读的文件）。")
    a("")
    a("| 能力 | 运行证据 |")
    a("|---|---|")
    for c in caps:
        if c.get("level") != "verified":
            continue
        ev = c.get("evidence") or []
        cell = (
            "<br>".join("· `%s`" % e for e in ev)
            if ev
            else "**（缺证据 ⇒ 与 verified 矛盾）**"
        )
        a("| `%s` | %s |" % (c.get("id"), cell))
    a("")

    a("## 四 **仍空缺什么、为什么**（A8 的正面回答）")
    a("")
    a(
        "### 4.1 未达 `verified` 的能力（%d 条）"
        % sum(1 for c in caps if c.get("level") != "verified")
    )
    a("")
    a("| 能力 | `level` | `source` | 为什么还没到 `verified`（取 `limitations` 首条）|")
    a("|---|---|---|---|")
    for c in caps:
        if c.get("level") == "verified":
            continue
        lim = c.get("limitations") or []
        first = next((x for x in lim if str(x).strip()), "**（未写明原因）**")
        a(
            "| `%s` | `%s` | `%s` | %s |"
            % (c.get("id"), c.get("level"), c.get("source"), str(first)[:200])
        )
    a("")

    a("### 4.2 明确「不做」的（%d 条，A1 的另一半）" % len(not_doing))
    a("")
    if not_doing:
        a("| 不做 | 原因 |")
        a("|---|---|")
        for it in not_doing:
            a("| %s | %s |" % (it.get("subject", ""), it.get("reason", "")))
        a("")
        a(
            "> 完整依据（可核的命令/文件）见 `docs/union-not-doing.json`，"
            "形状由 `check_union_conventions.py` 的 **R14** 守。"
        )
    else:
        a(
            "> ⚠ **清单为空** —— 一个「不做」都没登记（那通常意味着**还没逐域确证**，而不是「全都做」）。"
        )
    a("")

    #: ⚑⚑⚑ **官方接口族级的缺口**（A8 的「仍空缺什么」在**族**这一层的定量版）。
    #:   2026-10-01（轮 187）加，理由是一条**实测出来的腐坏**：
    #:   `harvest-report.md` 的 §三 是**手写**的，数字停在早期轮次 —— 一份外部评审据此把
    #:   **已经实现的东西**读成缺口（它引 §三 说「拓扑优化 10 个约束接口…不做半成品」，
    #: 而它们现已在 `scripts/sw_topology.py` 里实现，台账里 `ICWTopology*Constraint` 均
    #: 已 `used>=1`）。
    #: ⇒ ★ **手写的缺口清单必腐坏**（与 §二 正文停在「第 12 轮」同一个病）⇒ 这一段**从台
    #: 账生成**。
    #:   ⚠ 台账本身也是生成物（`tools/gen_family_coverage.py`）——
    #:     ★ 2026-10-01（轮 210 / Spec Kit `129`）**已从工作区仓库搬进本仓库**：
    #: 此前它在 `D:/AI/SW/tools/` 下，而产物在本仓库 ⇒ clone 本仓库的人**有产物、没生成
    #: 器**
    #:     （ROADMAP 早先把它记成「**跨仓库滞后风险**」；搬迁即为消除该风险）。
    #:     本文件只**读**它的产物；两者要一起提交，否则本门禁会拦下（逐字节比对）。
    fc_path = ROOT / "docs" / "family-coverage.json"
    fc = json.loads(fc_path.read_text(encoding="utf-8")) if fc_path.is_file() else []

    a(
        "### 4.3 官方接口族的**零调用**缺口（**从台账生成**，A8 的「仍空缺什么」在族这一层）"
    )
    a("")
    if not fc:
        a(
            "> ⚠⚠ **`docs/family-coverage.json` 不在** ⇒ 这一段**没有数据**，"
            "不是「没有缺口」。先跑 `python tools/gen_family_coverage.py`。"
        )
        a("")
    else:
        _tot = sum(r["members"] for r in fc)
        _hit = sum(r["hit"] for r in fc)
        _gat = sum(r["gated"] for r in fc)
        _use = sum(r["used"] for r in fc)
        _zero = sorted(
            (r for r in fc if r["hit"] > 0 and r["used"] == 0),
            key=lambda r: (-r["members"], r["family"]),
        )
        _bydom: dict = {}
        for _r in _zero:
            _e = _bydom.setdefault(_r["domain"], [0, 0])
            _e[0] += 1
            _e[1] += _r["members"]
        _pct = lambda v: (100.0 * v / _tot) if _tot else 0.0  # noqa: E731
        a(
            "> 数据源：`docs/family-coverage.json`（**生成物**，从 `C:\\swapi\\types\\` 的成员目录 +"
        )
        a("> 本仓库静态扫描得出；**未执行代码、未连 SolidWorks**）。")
        a("> ★⭐⭐ **三列口径不同，不可合并**（合并就是误导）：")
        a("")
        a("| 列 | 值 | 含义 |")
        a("|---|---|---|")
        a(
            "| 官方接口族 / 成员 | **%d** / **%s** | 全量 |"
            % (len(fc), f"{_tot:,}")
        )
        a(
            "| 编目录 | %s（%.0f%%）| 名字在代码里出现过 —— **含只写在 API 名登记表里的** |"
            % (f"{_hit:,}", _pct(_hit))
        )
        a(
            "| 护栏可调 | %s（%.0f%%）| 登记在某模块能力表里，**且有可达调用路径** |"
            % (f"{_gat:,}", _pct(_gat))
        )
        a(
            "| **直接调** | **%s（%.0f%%）** | 静态上**看得见字面量**的调用 |"
            % (f"{_use:,}", _pct(_use))
        )
        a(
            "| ⇒ **编进目录但从未直接调** | **%d 族 / %s 成员** | 本节的清单 |"
            % (len(_zero), "{:,}".format(sum(r["members"] for r in _zero)))
        )
        a("")
        a("#### 按域（`hit > 0` 且 `used == 0`）")
        a("")
        a("| 域 | 族 | 成员 |")
        a("|---|---|---|")
        for _d, (_n, _m) in sorted(_bydom.items(), key=lambda kv: (-kv[1][1], kv[0])):
            a("| %s | %d | %s |" % (_d, _n, f"{_m:,}"))
        a("")
        a("#### 最大的 10 个零调用族（**要动就先看这些**）")
        a("")
        a("| 族 | 成员 | 域 |")
        a("|---|---|---|")
        for _r in _zero[:10]:
            a("| `%s` | %d | %s |" % (_r["family"], _r["members"], _r["domain"]))
        a("")
        a("> ⚠⚠⚠ **读这一段的四条纪律（从台账继承，不遵守必误判）**：")
        a("> 1. **三列不可合并** —— 「编目录 100%」只证明「这份 API 清单做完了」，")
        a(">    **不等于「这些 API 都能用了」**。")
        a("> 2. **`used == 0` ≠ 没实现** —— 反例就在台账里：`IGtolFrame` 曾 `used=0`，")
        a(
            ">    而 `scripts/sw_gtol.py` 确实调它（成员名字面量）；台账重算后已变 `used=1`。"
        )
        a(">    走**变量**传成员名的调用静态看不见。")
        a("> 3. **台账是静态解析** ⇒ 它证明「静态可见性」，**不证运行期可用性**。")
        a("> 4. ★ **「该不该做」不在台账里** —— 有的零调用族是**故意不做**的")
        a(">    （需许可证 / 需加载项 / 官方仅支持进程内非托管 C++）。")
        a(">    这类**不做的原因**登记在 `capabilities.yaml` 的 `backend_catalog` 与")
        a(">    §4.2 的「明确不做」清单里，**不要**从本节的数字直接推优先级。")
        a(">")
        a("> ★ **已知的一条实例**：`ISafeArrayUtility`（21 成员，本节仍在零调用里）")
        a(
            "> 经真机穷尽实测**不可达**（`used=0` 是正确的）—— 见 `backend_catalog` 的限制段。"
        )
        a("")

    a("## 五 门禁栈（**方法论沉淀**：把判定交给机器，而不是靠人记得）")
    a("")
    a(
        "`scripts/check_*.py` 共 **%d** 道；其中接进 `release_check.py`（发布前硬失败）的："
        % len(gates)
    )
    a("")
    a("| 门禁 | 接进 `release_check`？ |")
    a("|---|---|")
    for g in gates:
        a("| `scripts/%s` | %s |" % (g, "✅" if g in wired else "—"))
    a("")
    a("> 还有两个**生成器 + 新鲜度门禁**配对（生成物不许手改）：")
    a(
        "> `tools/build_union_map.py` ⇄ `check_union_conventions.py` 的「地图与来源同步」段；"
    )
    a("> `scripts/gen_level_audit.py` ⇄ 同门禁的 R8 段；")
    a(
        "> `tools/gen_harvest_digest.py` ⇄ `scripts/check_digest_freshness.py`（本文件）。"
    )
    a("")

    OUT.write_text("\n".join(item) + "\n", encoding="utf-8")
    print("  已写 %s（%d 字节 / %d 行）" % (_display(OUT), OUT.stat().st_size, len(item)))
    print(
        "  提交 %d 个 · 能力 %d 条（verified %d）· 门禁 %d 道 · 不做 %d 条"
        % (n_commits, len(caps), lv.get("verified", 0), len(gates), len(not_doing))
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
