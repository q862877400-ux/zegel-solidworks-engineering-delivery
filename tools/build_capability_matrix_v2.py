"""★ **第二版矩阵**：用**真实映射**（工具 → COM 成员）填充，★ 重跑三个预先写死的判据。

★ 第一版为什么失效（★ 已诊断并修正）：
  ★★ 我按**工具名**（意图语言：`fillet` / `part_shell`）分类 ⇒ ★ **官方成员名是实现语言**
    （`FeatureFillet` / `InsertShellFeature`）⇒ ★★ **两套词汇不共享 token** ⇒ **0 命中**（判据① 100%）。
  ⇒ ★★★ 本版改用：★ `tools/map_tools_to_members.py` 抽出的
    **工具 → 它真正调的 COM 成员** ⇒ ★ 再对**成员名**分类 ⇒ ★ 矩阵才有真实填充 ✓
★ 判据与阈值**沿用第一版、未改**（★ 事实 510：判据先标定再接线；★ 改了阈值就失去了可比性）。
"""
from __future__ import annotations

import json
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(Path(__file__).resolve().parents[1])
SWAPI = Path(r"C:\swapi")
MAP = REPO / "output" / "tool-to-member-map.json"
OUT = REPO / "output" / "operation-object-matrix-v2.json"
sys.path.insert(0, str(REPO / "tools"))
from build_capability_matrix import OPS, OBJ_RULES, classify          # noqa: E402


def main() -> int:
    started = time.time()
    m = json.loads(MAP.read_text(encoding="utf-8", errors="replace"))
    rows = m["行"]
    fams = {}
    for d in sorted(p for p in (SWAPI / "types").iterdir() if p.is_dir()):
        ms = sorted(p.stem for p in d.glob("*.md"))
        if ms:
            fams[d.name] = ms
    member_to_fam = {}
    for fam, ms in fams.items():
        for x in ms:
            member_to_fam.setdefault(x, fam)
    cmds = [x for x, _ in re.findall(
        r"^\|\s*(sw[A-Za-z0-9_]+)\s*\|\s*([^|]*?)\s*\|",
        (SWAPI / "enums" / "swCommands_e.md").read_text(encoding="utf-8", errors="replace"), re.M)]

    #: ★ 工具 → 它成员所在格子的集合
    tool_cells: dict = {}
    unplaced = []
    for r in rows:
        cells = set()
        for mem in r["com_members"]:
            fam = member_to_fam.get(mem, "")
            if not fam and mem not in member_to_fam:
                continue
            cells.add((classify(mem, OPS), classify(fam + " " + mem, OBJ_RULES)))
        tool_cells[r["tool"]] = cells
        if not cells:
            unplaced.append({"tool": r["tool"], "members": r["com_members"][:4]})

    ops = [o for o, _ in OPS]
    objs = [o for o, _ in OBJ_RULES]
    total_cells = len(ops) * len(objs)
    covered = set()
    for cs in tool_cells.values():
        covered |= cs
    #: ★ 官方成员的格子占用（★ 分母侧）
    official_cells = Counter()
    for mem, fam in member_to_fam.items():
        official_cells[(classify(mem, OPS), classify(fam + " " + mem, OBJ_RULES))] += 1

    r1 = 100.0 * len(unplaced) / max(1, len(rows))
    r2 = 100.0 * (total_cells - len(covered)) / total_cells
    member_tokens = set()
    for mem in member_to_fam:
        member_tokens |= {w.lower() for w in re.findall(r"[A-Za-z]{3,}", mem)}
    hit = sum(1 for c in cmds
              if ({w.lower() for w in re.findall(r"[A-Za-z]{3,}", re.sub(r"^swCommands?_?", "", c))}
                  & member_tokens))
    r3 = 100.0 * hit / max(1, len(cmds))

    def band(v, good, ok, hi=False):
        if hi:
            return "★ 好" if v >= good else ("可接受" if v >= ok else "★★ 难看")
        return "★ 好" if v <= good else ("可接受" if v <= ok else "★★ 难看")

    R = {"at": time.strftime("%Y-%m-%d %H:%M:%S"), "版本": "v2（真实映射）",
         "规模": {"工具": len(rows), "有成员的": len(rows) - len(unplaced),
                  "官方族": len(fams), "官方成员": len(member_to_fam), "官方命令": len(cmds)},
         "矩阵": {"操作": ops, "对象": objs, "格子总数": total_cells,
                  "被工具覆盖的格子": len(covered),
                  "有官方成员的格子": len([c for c, n in official_cells.items() if n])},
         "判据①无处可放率": {"值": round(r1, 2), "分子": len(unplaced), "分母": len(rows),
                             "判定": band(r1, 10, 20)},
         "判据②空格率": {"值": round(r2, 2), "判定": band(r2, 60, 80), "注": "参考项"},
         "判据③双源一致率": {"值": round(r3, 2), "判定": band(r3, 50, 30, True), "注": "上界"},
         #: ★★★ 2026-10-03（接手轮）**去掉 `[:30]`** ——
         #:   ★ 病灶：★ 矩阵的**判定**（判据① 18.77% = 52/277）用的是 `len(unplaced)`（★ **全部**），
         #:     ★★ 而**这份 JSON 只存了前 30 个** ⇒ ★★★ **两个读者拿到两个数** ✓
         #:   ★ 实证：★ 矩阵打印「无处可放 **52**」、★ 而 `tools/classify_unplaced_tools.py`
         #:     （★ 读这份 JSON）打印「**30**」⇒ ★★ **我上一轮把它记成了"两个来源不一致"**，
         #:     ★★★ **其实是同一份数据被截断了** ✓
         #:   ★★ 可复用判据：★ **凡"打印一个总数、却只存一部分明细"的地方，
         #:     下游一定会把明细数当成总数**（★ 与**事实 513**那句"读数要带版本"同族）✓
         "无处可放": [x["tool"].replace("solidworks_", "") for x in unplaced],
         "无处可放_总数": len(unplaced),
         "工具覆盖的格子": sorted([list(c), n] for c, n in Counter(
             c for cs in tool_cells.values() for c in cs).most_common()),
         "官方成员最多的格子": sorted([list(c), n] for c, n in official_cells.most_common(20)),
         }
    #: ★★★ 空格清单 = 有官方成员、但没有工具覆盖 —— ★★ 这就是"缺口地图"
    gap = [c for c, n in official_cells.items() if n and c not in covered]
    R["★_有功能但无工具的格子"] = sorted([[list(c), official_cells[c]] for c in gap],
                                         key=lambda x: -x[1])
    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1), encoding="utf-8")

    print("★ 规模：工具 **%d**（★ 有成员的 **%d**）· 官方 **%d** 族 / **%d** 成员 / **%d** 命令"
          % (len(rows), len(rows) - len(unplaced), len(fams), len(member_to_fam), len(cmds)))
    print("★ 矩阵 %d×%d = **%d** 格 ⇒ 工具覆盖 **%d** 格 · 有官方成员的 **%d** 格"
          % (len(ops), len(objs), total_cells, len(covered), len([c for c, n in official_cells.items() if n])))
    print()
    print("★★★ 三个判据（★ 与第一版**同一套阈值**，★ 未改）：")
    print("   ① 无处可放率 = **%.2f%%**（%d/%d）⇒ %s ★（第一版是 100%%）"
          % (r1, len(unplaced), len(rows), R["判据①无处可放率"]["判定"]))
    print("   ② 空格率     = **%.2f%%** ⇒ %s（参考项）" % (r2, R["判据②空格率"]["判定"]))
    print("   ③ 双源一致率 = **%.2f%%**（%d/%d，上界）⇒ %s"
          % (r3, hit, len(cmds), R["判据③双源一致率"]["判定"]))
    print()
    print("★ 工具覆盖的格子（前 14）：")
    for c, n in Counter(c for cs in tool_cells.values() for c in cs).most_common(14):
        print("   %-8s × %-14s %d" % (c[0], c[1], n))
    print()
    print("★★★ 「有官方功能、但我们没工具」的格子（★ 前 14 —— ★ 这就是缺口地图）：")
    for c in sorted(gap, key=lambda x: -official_cells[x])[:14]:
        print("   %-8s × %-14s 官方 %d 个成员" % (c[0], c[1], official_cells[c]))
    print()
    print("★ 产出:", OUT, "（%.1f s）" % (time.time() - started))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
