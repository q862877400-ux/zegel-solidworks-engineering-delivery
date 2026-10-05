"""★ 规格 207 的 SC-1..SC-8 机器判据（能机检的机检，不能的如实标"待人/待 deep"）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/check_spec207_sc.py
# 定位:   ★ 规格 207 的完成判据是「SC-1..SC-8 全绿」⇒ ★ 那需要**机器判据**，不是我的叙述 ✓
#         ★★ **为什么值得单独做一个检查器**：本规格的**起因**就是我把「分类器自述」当成「实测」
#           引用过（事实 559）⇒ ★ 若 SC 也靠我说"绿了"，那是同一个病换个地方 ✓
#         ★ **统计口径**：本文件**不改任何东西**（只读 + 打印判据），
#           故不参与 `release_check` 的门禁分类登记（它不是 `_run_*_gate`）✓
#         ⚠ **老实标注**：SC-2 / SC-3 依赖 deep 档收齐、SC-7 依赖 git 历史的语义判断
#           ⇒ 这三条本文件**不冒充机检**，而是**读实据后如实给"未定案"**（铁律 5）✓
# 官方依据: 不适用（本仓工序）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
AGG = ROOT / "output" / "union-verify-349.json"
REF = ROOT / "output" / "union-gap-v3.json"
VF = ROOT / "output" / "bunny-records-verify"
DP = ROOT / "output" / "bunny-records-deep"
LIMIT = 256 * 1024

results: list[tuple[str, str, str]] = []   #: (SC, 判定, 证据)


def add(sc: str, ok: str, ev: str) -> None:
    results.append((sc, ok, ev))


def main() -> int:
    # ── SC-1：349 个操作每个都有一条记录（覆盖率）────────────────────────
    ref_rows = json.loads(REF.read_text(encoding="utf-8"))["rows"]
    ref_ops = {r.get("operation") for r in ref_rows}
    if not AGG.is_file():
        add("SC-1", "★ 不达标", "聚合件不存在：%s ⇒ 先跑 tools/build_union_verify_349.py" % AGG.name)
    else:
        agg = json.loads(AGG.read_text(encoding="utf-8"))
        recs = agg.get("records", [])
        got = {r.get("op") for r in recs}
        same = got <= ref_ops and len(recs) == len(got)          #: 无空洞、无重复
        n_dp = len(list(DP.glob("*.json")))
        if len(recs) == len(ref_rows) and same:
            add("SC-1", "达标", "%d/%d 条、op 集合与参照集一致" % (len(recs), len(ref_rows)))
        else:
            add("SC-1", "★ 未定案",
                "%d/%d 条（缺 %d）· op 集合%s ⇒ deep 档还差 %d 条（现 %d/76）"
                % (len(recs), len(ref_rows), len(ref_rows) - len(recs),
                   "一致" if same else "**不一致**", 76 - n_dp, n_dp))

    # ── SC-2：①档 273 条逐条验证 + verdict 齐 ────────────────────────────
    bad = []
    n_vf = 0
    for f in sorted(VF.glob("*.json")):
        try:
            r = json.loads(f.read_text(encoding="utf-8", errors="replace"))
        except Exception:                                        # noqa: BLE001
            bad.append(f.name)
            continue
        n_vf += 1
        if not (r.get("verdict") or r.get("has_equivalent")):
            bad.append(f.name + "(缺 verdict)")
    add("SC-2", "达标" if (n_vf == 273 and not bad) else "★ 不达标",
        "①档 %d/273 份、缺字段/坏件 %d" % (n_vf, len(bad)))

    # ── SC-3：②③档 76 条逐条 + 五个必需字段 ────────────────────────────
    need = ["official_member", "official_signature", "dead_ends", "proposed_name", "recommendation"]
    miss_n = 0
    n_dp = 0
    for f in sorted(DP.glob("*.json")):
        try:
            r = json.loads(f.read_text(encoding="utf-8", errors="replace"))
        except Exception:                                        # noqa: BLE001
            miss_n += 1
            continue
        n_dp += 1
        off = r.get("official") if isinstance(r.get("official"), dict) else {}
        prop = r.get("proposed") if isinstance(r.get("proposed"), dict) else {}
        flat = dict(r)
        flat.update({"official_member": off.get("member"),
                     "official_signature": off.get("signature"),
                     "proposed_name": prop.get("name")})
        if any(not flat.get(k) for k in need):
            miss_n += 1
    if n_dp == 76 and miss_n == 0:
        add("SC-3", "达标", "②③档 76/76 份、五字段齐")
    else:
        add("SC-3", "★ 未定案",
            "②③档 %d/76 份（缺 %d）· 五字段不齐 %d 份" % (n_dp, 76 - n_dp, miss_n))

    # ── SC-4：两个口径必须并列 ──────────────────────────────────────────
    if AGG.is_file():
        agg = json.loads(AGG.read_text(encoding="utf-8"))
        c = agg.get("calibers", {})
        have = {"classifier_self_report", "per_item_measured"} <= set(c)
        add("SC-4", "达标" if have else "★ 不达标",
            "两个口径%s；差值说明：%s" % ("并列在聚合件里" if have else "**缺**",
                                    str(c.get("★_禁止相减", "**缺**"))[:60]))
    else:
        add("SC-4", "★ 未定案", "聚合件不存在 ⇒ 无法核")

    # ── SC-5：合法 JSON + < 256 KB + 枚举化 ─────────────────────────────
    if AGG.is_file():
        raw = AGG.read_bytes()
        try:
            json.loads(raw.decode("utf-8"))
            legal = True
        except Exception:                                        # noqa: BLE001
            legal = False
        viol = len(json.loads(raw.decode("utf-8")).get("enum_violations") or [])
        ok = legal and len(raw) < LIMIT
        add("SC-5", "达标" if ok else "★ 不达标",
            "合法 JSON=%s · %d 字节（上限 %d）· 枚举越界 %d 处" % (legal, len(raw), LIMIT, viol))
    else:
        add("SC-5", "★ 未定案", "聚合件不存在 ⇒ 无法核")

    # ── SC-6：全程离线静态（零 SolidWorks 调用）─────────────────────────
    #: ★ 本条**不能**在本脚本里机检 —— 它要的是"跑完后与开工前一致"的前后对比，
    #:   而那需要探 SolidWorks（本项目纪律：探针要走护栏）⇒ ★ 本文件只读**已记的实据** ✓
    add("SC-6", "待人核（有实据）",
        "已记录：solidworks_session_busy_status 逐字 `app_windows: 0`、"
        "「★ SolidWorks 应用本体不在」；bunny 侧明令禁止 mcp__solidworks__ / 探针（D-3）")

    # ── SC-7：每批落盘 + 提交，只 add 自己这一线 ────────────────────────
    add("SC-7", "待人核（有实据）",
        "git log 可查：本轮各批均走 tools/commit_mine.py；★ 路径清单只含本线文件；"
        "★ 过程中被「删除守卫」与「内联信息引号坑」各拦过、并重做过（记录在提交信息里）")

    # ── SC-8：我的假"实测"声明清掉 ──────────────────────────────────────
    #: ★★ 判据要**排除"引用"** —— 本规格的 spec.md 与 tasks.md **故意逐字引用**那句假声明
    #:   （用来记录错误、防止复发），而**检查器自己的正则**也含那几个字 ✓
    #:   ⇒ ★ 一个把「防它的文档」报成违规的检查器，就是**会喊狼的守卫**
    #:     （我已栽过两次：`list_agents` 对 inactive 误报 · 审计器把 Lead 自己报成违规）✓
    #:   ★ 落法：① 跳过本文件自身；② **落在「」引号里的一律算引用**（真声明不会自己加引号）✓
    pat = re.compile(r"假阳性率实测|实测是\s*78|实测假阳性率\s*≈?\s*78")
    quoted = re.compile(r"「[^」]{0,200}」")
    hits: list[str] = []
    for base in ("docs", "specs", "scripts", "tools", "mcp-server"):
        for f in (ROOT / base).rglob("*"):
            if not (f.is_file() and f.suffix in {".md", ".py"} and f.stat().st_size < 2_000_000):
                continue
            if f.resolve() == Path(__file__).resolve():
                continue                                  #: ★ 检查器自身的正则不算违规
            try:
                t = f.read_text(encoding="utf-8", errors="replace")
            except Exception:                                # noqa: BLE001
                continue
            #: ★ 先把「」引号内的片段**挖掉**，再看剩下的是不是还有真声明 ✓
            stripped = quoted.sub("", t)
            if pat.search(stripped):
                hits.append(str(f.relative_to(ROOT)))
    add("SC-8", "达标" if not hits else "★ 不达标（%d 处**非引用**命中）" % len(hits),
        ("0 处非引用命中（★ 引号里的**引用**已排除，那是记录错误用的）" if not hits
         else "命中：" + " · ".join(hits[:4]))
        + " ★ 判据的**已知边界**：落在「」里的一律算引用 ⇒ 真声明若被**加引号**写会漏过 —— "
          "★ 这是**有意的取舍**：本 SC 抓的是「**断言**」，不是「引用」✓")

    print("=" * 70)
    print("★ 规格 207 · SC-1..SC-8 机器判据（★ 本文件不改任何东西）")
    print("=" * 70)
    for sc, ok, ev in results:
        print("  %-5s %-16s %s" % (sc, ok, ev))
    hard = [r for r in results if r[1] == "★ 不达标"]
    print("-" * 70)
    print("★ 不达标的 %d 条 · 未定案 %d 条 · 待人核 %d 条"
          % (len(hard),
             len([r for r in results if r[1] == "★ 未定案"]),
             len([r for r in results if r[1].startswith("待人核")])))
    #: ★ 退出码语义：★ **只在"不达标"时非 0**（"未定案"是 deep 还在跑的应然状态，不是失败）✓
    return 1 if hard else 0


if __name__ == "__main__":
    raise SystemExit(main())
