r"""@brief 签名审计表新鲜度门禁：`signature-audit.md` 的**逐模块调用点数**必须与实跑一致。

## 为什么要有它（**实测出的痛点**）
`docs/signature-audit.md` 是 **A5**（「每个新增文件里每个 COM 调用的参数顺序与类型与官方签名对齐」）的制品。
它在「修正后的全量结果」一节里给出一张**逐模块**表：

```
| 模块 | 调用点 | 通过 | 存疑 | 查不到 |
| `sw_mold.py` | 17 | **17** | 0 | 0 |
| `sw_topology.py` | 45 | **45** | 0 | 0 |
| `sw_simulation.py` | 34 | **34** | 0 | 0 |
…
```

**而这张表**会随着代码增长而失真**：
```
2026-10-01（轮 55）实跑（按文档自己的复跑方式，传全 iface_*.txt）：
  sw_mold.py        17  （文档 17）✓
  sw_topology.py    49  （文档 45）✗  ← 轮 51 给该模块加了 4 个 COM 调用
  sw_simulation.py  44  （文档 34）✗  ← +10
  sw_weldment.py    71  （文档 71）✓
  sw_connect.py     21  （文档 21）✓
⇒ **2/5 已失真**，而 `release_check.py` 只查这份文档**存在**。
```
**⇒ 与 `harvest-report.md` 是**同一类**缺口（「存在但数字失真」）——
本门禁是 `check_report_freshness.py` 的**姐妹**，管的也是「数字要跟得上代码」。**

## 判据
1. 从 `docs/signature-audit.md` 抽出**逐模块表**（模块名 → 调用点数）
2. 对每个模块**实跑** `scripts/audit_call_arity.py <模块> <全部 iface_*.txt>`
3. **逐项比对**；不符则报「哪个模块、文档写多少、实际多少」，并给出修法行

## 便携性守卫（**必须**）
需要两样本机资源：`D:\AI\SW\_raw` 下的 `iface_*.txt`，以及那些模块文件。
**任一缺失 ⇒ SKIP 并 exit 0** —— 否则别的机器上无条件红。

## 不做的事
* **不改文档**（表里那些数是历史记录，改由人/脚本按报出的修法行做）。
* 不判「存疑/查不到」是否已裁定（那是**内容**判断，不是**新鲜度**判断）。

# ── 来源 ──
# 仓库:   本项目自身（门禁实现）
# 文件:   scripts/check_signature_audit_freshness.py —— 本文件自身
#         tests/test_signature_audit_freshness_gate.py（契约测试 + 负例）
# 定位:   把 A5 的制品从「存在即可」升级为「**逐模块数字也要对**」；
#         依据是 2026-10-01（轮 55）实测到的 **2/5 失真**。
# 官方签名依据: 不适用（纯静态：读 markdown + 跑本仓库的静态审计工具，**不连 SolidWorks**）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

#: 2026-10-03（接手轮）强制 stdout 为 UTF-8 —— 本门禁会 print 中文与箭头/勾这类符号，
#:   而 stdout 是管道时（测试正是用管道抓输出）默认按 locale（本机 GBK）编码
#:   ⇒ UnicodeEncodeError: 'gbk' codec can't encode character … ⇒ 门禁自己崩掉。
#:   known-facts 58 那一族（中文 Windows 上两侧默认编码不一致 —— 病灶在输出侧）；
#:   而测试那侧的 subprocess.run 已经带了 encoding='utf-8'。
sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[1]
DOC = REPO / "docs" / "signature-audit.md"
RAW = Path(Path(__file__).resolve().parents[1] / "_raw")

#: 表行形态： ``| `sw_mold.py` | 17 | **17** | 0 | 0 |``
TABLE_ROW = re.compile(
    r"^\|\s*`([\w./]+\.py)`\s*\|\s*\*{0,2}(\d+)\*{0,2}\s*\|\s*\*{0,2}(\d+)\*{0,2}\s*\|")


def parse_table(doc: Path = DOC) -> dict:
    """⇒ ``{模块相对路径: {"calls": n, "passed": n}}``（文档里那张逐模块表）。"""
    out: dict = {}
    if not doc.is_file():
        return out
    for line in doc.read_text(encoding="utf-8", errors="replace").splitlines():
        m = TABLE_ROW.match(line)
        if m:
            mod = m.group(1).replace("\\", "/")
            out[mod] = {"calls": int(m.group(2)), "passed": int(m.group(3))}
    return out


def reflection_files(raw: Path = RAW) -> list:
    """⇒ 全部 `iface_*.txt` 的**绝对路径**（去重保序）。"""
    if not raw.is_dir():
        return []
    seen, out = set(), []
    for p in sorted(raw.rglob("iface_*.txt")):
        key = p.name.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(str(p))
    return out


def resolve_module(name: str, repo: Path = REPO) -> Path | None:
    """把文档表里的模块名解析成仓库内的真实路径 ⇒ 找不到返回 ``None``。

    ⚠⚠ **表里用的是裸文件名**（`sw_mold.py` / `drawing_workflow.py`），
    而它们分散在 `scripts/` 与 `subskills/**/`；
    直接 `repo / name` **一个都找不到**（轮 55 首跑就撞上：6/6 全报「跑不了」⇒ 误 SKIP）。
    ⇒ 解析顺序：① 带路径的按原样；② `scripts/<name>`；③ `subskills/**/<name>`；
      ④ 全仓 `rglob`（**取唯一命中**；多个同名 ⇒ 返回 `None`，不瞎猜）。
    """
    if "/" in name or "\\" in name:
        p = repo / name.replace("\\", "/")
        return p if p.is_file() else None
    direct = repo / "scripts" / name
    if direct.is_file():
        return direct
    # ⚠ 排除**桌面内嵌快照**（`apps/*/resources/skill/**`，构建产物、gitignore）
    # —— 否则 `drawing_workflow.py` 会有 2 个命中（源 + 快照）⇒ 解析器判「不唯一」而放弃
    # 。
    hits = [p for p in repo.rglob(name)
            if p.is_file() and "__pycache__" not in p.parts and ".git" not in p.parts
            and "resources" not in p.parts]
    return hits[0] if len(hits) == 1 else None


def actual_calls(module: Path, refs: list, repo: Path = REPO) -> int | None:
    """跑 `audit_call_arity.py` ⇒ 调用点数（跑不通 ⇒ ``None``）。"""
    tool = repo / "scripts" / "audit_call_arity.py"
    if not (tool.is_file() and module.is_file()):
        return None
    proc = subprocess.run([sys.executable, str(tool), str(module), *refs],
                          check=False, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", cwd=str(repo))
    m = re.search(r"^调用点:\s*(\d+)", proc.stdout or "", re.M)
    return int(m.group(1)) if m else None


#: ⚑ **合计行 / 小计行的识别**（2026-10-01 轮 69 加）——
#: `AGENTS.md §一 A5` 的判据是这份审计表，而表里的**汇总数字是手工数出来的**：
#: ```
#: **小计：7 不通过 · 9 通过**            （批次 1）
#: | **合计** | **711** | **696** | **2** | **0** |   （全量审计覆盖）
#: **累计查出并修复的签名缺陷：7 处**
#: ```
#: ⇒ **手工数字没有门禁** ⇒ 改一行表体，合计不会自己跟着变
#:   （**与 A8 的 `harvest-report` 同型缺口**：只查存在、不查数字）。
#: ⚠ 本门禁只判**纯机器可判**的那一件：**带「合计」/「小计」的行必须是它上方表体的列和**
#: 。
#:   它**不判**「表体内容对不对」（那要人核），但算术自洽是**必要**条件，
#:   且**它能抓到最常见的腐坏方式**（改了行数忘改合计）。
TOTAL_ROW = re.compile(r"^\|\s*\*{0,2}(合计|小计)\*{0,2}\s*\|")


def _cells(line: str) -> list:
    """把 `| a | b |` 切成 `['a','b']`（去空白与粗体标记）。"""
    return [p.strip().replace("**", "") for p in line.strip().strip("|").split("|")]


def _num(text: str):
    """能取出一个纯数就返回，否则 `None`（`—` / `新增即合规` 之类不算数）。"""
    m = re.fullmatch(r"(\d+)", text.replace(",", "").strip())
    return int(m.group(1)) if m else None


def _is_separator(line: str) -> bool:
    """分隔行（`|---|---|`）——⚠ **必须逐格判**。

    ⚠⚠ 不能写 `set(line.strip().strip("|")) <= set("-: ")`：`strip("|")` 只去**首尾**，
      而分隔行**中间**全是 `|` ⇒ 集合里含 `'|'` ⇒ **判不出** ⇒ 分隔行被当成表体
      ⇒ 每一列都"有非数字格" ⇒ **门禁静默地什么都没查**
      （**「量太少本身就是假绿」** —— 2026-10-01 轮 69 实测踩过）。
    """
    if not line.startswith("|"):
        return False
    cells = _cells(line)
    return bool(cells) and all(c and set(c) <= set("-:") for c in cells)


def check_totals(doc: Path) -> tuple:
    """⇒ `(错误列表, 校验的列和个数)` —— 每个「合计/小计」行必须是上方表体的列和。"""
    lines = doc.read_text(encoding="utf-8").splitlines()
    bad: list = []
    checked = 0
    for i, line in enumerate(lines):
        if not TOTAL_ROW.match(line):
            continue
        total = _cells(line)
        body: list = []
        j = i - 1
        while j >= 0:
            prev = lines[j]
            if not prev.startswith("|"):
                break
            if _is_separator(prev):
                j -= 1
                continue
            if TOTAL_ROW.match(prev):
                break
            body.append(_cells(prev))
            j -= 1
        body.reverse()
        if body and all(_num(c) is None for c in body[0]):
            body = body[1:]                       # 去掉表头
        if not body:
            continue
        # ⚑ **列数一致性**（2026-10-01 轮 69 加）—— 被一次**假阳性**逼出来的：
        #   我在负例里手写替换合计行时**多打了一个 `|`** ⇒ 列错位 ⇒ 门禁报出
        #   「第 4 列：表体 2 + 0 + 0 + 0 = 2，而合计写 696」这类**看不懂的对比**。
        #   ⚠ 报「列错位」比报「算术不符」**更接近真因**。
        widths = {len(r) for r in body} | {len(total)}
        if len(widths) > 1:
            bad.append("L%d 的合计行**列数与前表不一致**（合计 %d 格 vs 表体 %s 格）"
                       "⇒ 多半是多打/漏打了一个 `|`，不是算术问题"
                       % (i + 1, len(total), sorted(len(r) for r in body)))
            continue
        for c in range(1, min(len(total), max(len(r) for r in body))):
            tval = _num(total[c])
            if tval is None:
                continue
            vals = [(_num(r[c]) if c < len(r) else None) for r in body]
            if any(v is None for v in vals):
                continue
            checked += 1
            if sum(vals) != tval:
                bad.append("L%d 的合计行第 %d 列：表体 %s = %d，而合计写 %d"
                           % (i + 1, c + 1, " + ".join(str(v) for v in vals),
                              sum(vals), tval))
    return bad, checked


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="签名审计表新鲜度门禁（逐模块调用点数）")
    ap.add_argument("--repo", default=str(REPO))
    ap.add_argument("--doc", default=str(DOC))
    ap.add_argument("--raw", default=str(RAW))
    a = ap.parse_args(argv)
    repo, raw = Path(a.repo), Path(a.raw)

    #: ⚑ **首行自带分母**（轮 192）：先解析出「文档列了几个模块」再打印首行 ——
    #:   否则首行只有个文件名，读者看不出这道门禁要逐项比多少个模块。
    #:   ⚠ 打印顺序仍**在**「文档损坏 / SKIP」那些分支之前（它们要读得到表头）。
    claimed = parse_table(Path(a.doc))
    print("签名审计表新鲜度门禁 · %s（文档列了 **%d** 个模块，逐个实跑比对）"
          % (Path(a.doc).name, len(claimed)))

    if not claimed:
        # ⚠⚠ **这里曾经无条件 `SKIP`，那是假绿**（2026-10-01 轮 83 系统排查发现）：
        #   与轮 82 修掉的 `check_report_freshness` **完全同型** ——
        #   `--doc` 默认指向**本仓库的** `docs/signature-audit.md`，
        #   所以「**文档里找不到逐模块表**」是**输入坏了**，不是「数据源不可用」。
        # 实测（轮 82 那次的报告行就是被脚本写坏的）：**产物被写坏 ⇒ 门禁 SKIP ⇒ 全绿**
        # 。
        # ⇒ **区分两件事**：① 文档**不存在** ⇒ SKIP（便携性，别的机器上不该无条件红）；
        #   ② 文档在、但**逐模块表读不出来** ⇒ **FAIL**（那份产物坏了就是坏了）。
        if Path(a.doc).is_file():
            print("  [FAIL] 文档**存在**，但读不出「逐模块表」⇒ 产物已损坏或被写坏")
            print("  ⚠ 这与「数据源不可用」**不是一回事**：文档在，就该能读出表 ——")
            print("     读不出来说明**那张表丢了**，而那正是本门禁要守的东西。")
            print("     表形态见本文件 docstring；修好后本门禁会重新逐模块比对。")
            return 1
        print("  **SKIP** —— 文档不存在（%s）" % Path(a.doc))
        print("  （**便携性守卫**：产物不在本机时不应无条件红）")
        return 0
    refs = reflection_files(raw)
    if not refs:
        print("  **SKIP** —— 拿不到 `iface_*.txt`（%s）" % raw)
        print("  （**便携性守卫**：没有反射转储的机器上不应无条件红）")
        return 0

    print("  反射文件 **%d** 份（已去重）· 文档列了 **%d** 个模块" % (len(refs), len(claimed)))
    print()
    stale, checked, skipped = [], 0, []
    for mod, want in sorted(claimed.items()):
        path = resolve_module(mod, repo)
        got = actual_calls(path, refs, repo) if path else None
        if got is None:
            skipped.append(mod)
            continue
        checked += 1
        mark = "OK " if got == want["calls"] else "**失真**"
        if got != want["calls"]:
            stale.append((mod, want["calls"], got))
        print("    %-22s 文档=%-4d 实际=%-4d %s" % (mod, want["calls"], got, mark))

    print()
    # ⚑ **合计行算术自洽**（2026-10-01 轮 69 加）—— **在任何 SKIP 之前判**：
    #   它只读文档、不碰代码/反射 ⇒ **没有便携性问题**，不该被后面的 SKIP 跳过。
    tbad, tchecked = check_totals(Path(a.doc))
    if tchecked == 0:
        print("  ⚠ 合计行校验：**0 个列和**被校验 ⇒ 判据可能失效（不是好事，喊出来）")
    elif tbad:
        print("  [FAIL] 合计行 %d 处与表体不符：" % len(tbad))
        for b in tbad:
            print("    · %s" % b)
        print()
        print("  修法：把合计行改成表体各列的和（**或**改表体 —— 但先确认哪个才是对的）")
        return 1
    else:
        print("  [PASS] 合计行 %d 个列和逐项相符" % tchecked)
    print()

    if skipped:
        print("  ⚠ %d 个模块跑不了（文件不在）：%s" % (len(skipped), ", ".join(skipped)))
    if checked == 0:
        # ⚠⚠ **这里曾经无条件 `SKIP`，那是假绿**（2026-10-01 轮 84 查证）：
        # 能走到这里 ⇒ `refs` **必然非空**（L238 已把「拿不到反射转储」那条 SKIP 掉了）
        # 。
        #   而表里的模块是**本仓库自己的 `.py`**（`scripts/*.py` / `subskills/**/*.py`）——
        #   **一个都解析不出来**只可能是：**路径解析坏了** 或 **仓库残缺**。
        # ★ **轮 55 首跑就撞上过这个形态**：`resolve_module` 当时写法不对 ⇒ 6/6 全报「跑
        # 不了」
        #     ⇒ 被这条 SKIP 放成"便携性守卫"，**全绿**（当时靠人发现才修）。
        #   ⇒ 实测（`tools/probe_checked_zero_skip.py`）：把 `--repo` 指向**空目录**、
        #     `--raw` 用真反射 ⇒ 复现出「反射 13 份在、6 个模块全跑不了 ⇒ SKIP ⇒ exit 0」。
        #   ⇒ 真实语义是 **FAIL**（反射在、模块却在仓库里找不到 = 解析坏了/仓库残缺）。
        print("  [FAIL] 反射转储**在**（%d 份），但表里 **%d** 个模块**一个都解析不出来**"
              % (len(refs), len(claimed)))
        print("  ⚠ 这与「便携性」**不是一回事**：那些模块是**本仓库自己的 `.py`** ——")
        print("     映射由 `scripts/<name>` 与 `subskills/**/<name>` 的解析顺序给出，")
        print("     全区找不到只可能是**解析坏了**或**仓库残缺**。")
        print("     修法：确认 `scripts/` 与 `subskills/` 完整；或核 `resolve_module` 的解析顺序。")
        if skipped:
            print("     本次解析失败的模块：%s" % ", ".join(skipped))
        return 1
    if stale:
        print("  [FAIL] %d/%d 个模块的数字已失真：" % (len(stale), checked))
        for mod, was, now in stale:
            print("    · `%s`  文档 %d → **实际 %d**" % (mod, was, now))
        print()
        print("  修法：把 `docs/signature-audit.md` 那张表里对应行改成：")
        for mod, _was, now in stale:
            print("    | `%s` | %d | **%d** | 0 | 0 |" % (mod, now, now))
        print()
        print("  ⚠ 口径：调用点数**会随代码增长**（新增 COM 调用即变）⇒ 这是**应该**的；")
        print("    门禁要的是「**文档跟得上代码**」，不是「数字永远不变」。")
        return 1
    print("  [PASS] %d 个模块逐项相符" % checked)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
