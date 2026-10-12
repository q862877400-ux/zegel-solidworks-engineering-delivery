"""★ 规格 324 验收入口：门禁清单四类 + 责任人 + 元门禁覆盖 tools/（Q16）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tools/run_s324_gates.py
# 定位:   规格 `specs/324-gate-inventory-and-meta-coverage` 的**验收入口**
# 官方依据: `output/PROJECT_STATUS_REVIEW_CONTINUATION.md` Q16（L329-347）逐字
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# -----------------------------------------------------------------------------
from __future__ import annotations

import json
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server"),
                str(ROOT / "tools")]

from scripts.engineering import gate_inventory as G                      # noqa: E402

OUT = ROOT / "output" / "s324"


def run_p() -> dict:
    """★ **P1~P9 逐条**。"""
    rows = []
    entries = G.load_classification().get("classification") or []
    inv = G.build_inventory()

    #: P1 四类枚举
    bad = [e.get("gate") for e in entries if e.get("kind") not in G.KINDS]
    rows.append({"p": "P1", "what": "kind ∈ 四类",
                 "ok": not bad and bool(entries),
                 "got": "%d 条 · 非法 %d" % (len(entries), len(bad))})

    #: P2 类别+理由+环境+责任人
    miss = []
    for e in entries:
        ent = G.GateEntry(**{k: v for k, v in e.items()
                             if k in G.GateEntry.__dataclass_fields__})
        if ent.missing():
            miss.append((ent.gate, ent.missing()))
    rows.append({"p": "P2", "what": "类别+理由+环境+责任人",
                 "ok": not miss, "got": "四项齐" if not miss else str(miss[:2])})

    #: P3 必需门禁接进 release
    static = [e for e in entries if e.get("kind") == G.RELEASE_STATIC]
    notwired = [e["gate"] for e in static if e.get("runs_in") != "release_check"]
    rows.append({"p": "P3", "what": "静态门禁接进 release",
                 "ok": not notwired,
                 "got": "%d 条静态 · 未接 %d" % (len(static), len(notwired))})

    #: P4 真机单独编排 · NOT_RUN
    rows.append({"p": "P4", "what": "真机单独编排 · NOT_RUN",
                 "ok": "not_run" in inv and "not_run_n" in inv,
                 "got": "NOT_RUN = %d（★ 如实报）" % inv["not_run_n"]})

    #: P5 诊断不是门禁
    diag = [e for e in entries if e.get("kind") == G.DIAGNOSTIC]
    alive = all((ROOT / "scripts" / e["gate"]).is_file()
                or (ROOT / e["gate"]).is_file() for e in diag)
    rows.append({"p": "P5", "what": "诊断保留且不是门禁",
                 "ok": bool(diag) and alive,
                 "got": "%d 条 · 都还在盘上=%s" % (len(diag), alive)})

    #: P6 retired 带 replaced_by
    ret = [e for e in entries if e.get("kind") == G.RETIRED]
    ok6 = all(e.get("replaced_by") for e in ret)
    rows.append({"p": "P6", "what": "retired 带 replaced_by",
                 "ok": ok6, "got": "%d 条（★ 0 条也如实报）" % len(ret)})

    #: P7 元门禁覆盖 scripts/ + tools/
    rows.append({"p": "P7", "what": "覆盖 scripts/ + tools/",
                 "ok": inv["scripts"]["n"] > 0 and inv["tools"]["n"] > 0,
                 "got": "scripts=%d · tools=%d"
                        % (inv["scripts"]["n"], inv["tools"]["n"])})

    #: P8 应执行 vs 实际
    rows.append({"p": "P8", "what": "应执行 vs 实际",
                 "ok": not inv["should_but_not_declared"]
                       and not inv["declared_but_no_file"],
                 "got": "应执行 %d · 漏登记 %d · 无文件 %d"
                        % (len(inv["should_run_in_release"]),
                           len(inv["should_but_not_declared"]),
                           len(inv["declared_but_no_file"]))})

    #: P9 tools/ 检查文件清点
    rows.append({"p": "P9", "what": "tools/ 检查文件清点",
                 "ok": len(inv["tools"]["checks"]) == inv["tools"]["n"],
                 "got": "%d 个已列" % inv["tools"]["n"]})

    return {"rows": rows, "ok": all(r["ok"] for r in rows)}


def run_w() -> dict:
    """★ **W1~W6 反向验证**。"""
    rows = []

    #: W1 删责任人 / 环境
    for fld in ("owner", "environment"):
        kw = {"gate": "check_x.py", "kind": G.RELEASE_STATIC, "reason": "r",
              "environment": "e", "owner": "o"}
        kw[fld] = ""
        try:
            G.GateEntry(**kw).validate()
            ok, got = False, "★ 没拒"
        except G.GateInventoryError as e:
            ok, got = e.code == "missing-field", e.code
        rows.append({"w": "W1", "what": "删掉 %s ⇒ 拒" % fld,
                     "ok": ok, "got": got})

    #: W2 第五种 kind
    try:
        G.GateEntry(gate="check_x.py", kind="release_software", reason="r",
                    environment="e", owner="o").validate()
        rows.append({"w": "W2", "what": "第五种 kind ⇒ 拒",
                     "ok": False, "got": "★ 没拒"})
    except G.GateInventoryError as e:
        rows.append({"w": "W2", "what": "第五种 kind ⇒ 拒",
                     "ok": e.code == "bad-kind", "got": e.code})

    #: W3 真机标成静态
    e3 = G.migrate_entry({"gate": "run_stage7_final_dod.py", "kind": "hard",
                          "reason": "★ 真机才能跑", "runs_in": "sw_guard"})
    rows.append({"w": "W3", "what": "真机标静态 ⇒ 检出",
                 "ok": e3.kind == G.RELEASE_HARDWARE and e3.not_run,
                 "got": "%s · not_run=%s" % (e3.kind, e3.not_run)})

    #: W4 只扫 scripts
    inv = G.build_inventory()
    rows.append({"w": "W4", "what": "只扫 scripts ⇒ tools 被漏",
                 "ok": inv["tools"]["n"] > 0,
                 "got": "tools=%d（★ 扫到了）" % inv["tools"]["n"]})

    #: W5 NOT_RUN 说成 pass
    hw = [e["gate"] for e in G.load_classification()["classification"]
          if e.get("kind") == G.RELEASE_HARDWARE]
    ok5 = all(g not in inv["actually_run_in_release"] for g in hw)
    rows.append({"w": "W5", "what": "NOT_RUN 不算 pass",
                 "ok": ok5, "got": "真机 %d 条都不在 release 通过集" % len(hw)})

    #: W6 retired 没 replaced_by
    try:
        G.GateEntry(gate="check_old.py", kind=G.RETIRED, reason="r",
                    environment="e", owner="o").validate()
        rows.append({"w": "W6", "what": "retired 无替代 ⇒ 检出",
                     "ok": False, "got": "★ 没拒"})
    except G.GateInventoryError as e:
        rows.append({"w": "W6", "what": "retired 无替代 ⇒ 检出",
                     "ok": e.code == "no-replaced-by", "got": e.code})

    return {"rows": rows, "ok": all(r["ok"] for r in rows)}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    p = run_p()
    w = run_w()
    inv = G.build_inventory()

    print("★ P1~P9：")
    for r in p["rows"]:
        print("   %s %-4s %-24s ⇒ %s" % ("✓" if r["ok"] else "✗", r["p"],
                                         r["what"], str(r["got"])[:52]))
    print()
    print("★ W1~W6 反向验证：")
    for r in w["rows"]:
        print("   %s %-4s %-26s ⇒ %s" % ("✓" if r["ok"] else "✗", r["w"],
                                         r["what"], str(r["got"])[:48]))
    print()
    print("★ 四类计数（★ 0 条也如实报）：")
    for k, v in inv["counts"].items():
        print("   %-20s %d" % (k, v))
    print("★ 豁免（★ 有理由的已知未接线）：%d 条 %s"
          % (inv["exempted_n"], inv["exempted"]))

    ev = {"p": p, "w": w, "inventory": inv,
          "finished": time.strftime("%H:%M:%S")}
    fp = OUT / "gates.json"
    fp.write_text(json.dumps(ev, ensure_ascii=False, indent=1), encoding="utf-8")
    print()
    print("★ P：%s · W：%s" % ("过" if p["ok"] else "不过",
                                "过" if w["ok"] else "不过"))
    print("★ 证据 → %s" % fp)
    return 0 if (p["ok"] and w["ok"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
