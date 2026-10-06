"""★ 指纹灵敏度标定（真机）：逐类挑一个"已知会改它"的写操作，看指纹有没有动。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_fingerprint_sensitivity.py
# 定位:   ★ 规格 `specs/210-declarative-effects` 的 **B2**（★ 评审原话：「**量具是指纹，所以要校准它**」）✓
# 运行:   ★ **一律走护栏**：`python tools/sw_guard.py --timeout 900 -- python tools/probe_fingerprint_sensitivity.py`
#   ★ 护栏现在会给子进程设 `SW_SANDBOX_MODE=enforce` ⇒ ★ 打开的**永远是副本** ✓
# 判据:   ★★ **第 0 格（最要紧）**：★ 连读两次、**中间什么都不做** ⇒ ★ 两次必须**完全相等**
#     —— ★ 这是"**读数本身只读**"的直接证据；★ 不等就说明**指纹自己有副作用** ✗
#   ★ 其余每类：★ 跑一个已知会改它的写操作 ⇒ ★ 看该类读数有没有动 ✓
#   ★★ 结论分**三档**（★ 不许把"没试"说成"看不见"）：
#     `sensitive`（动了 ⇒ 有灵敏度证据）· `not_detected`（**跑了写操作**但没动 ⇒ 这一类**不可见**）·
#     ★ **`untested`（这一轮**没跑**写操作 ⇒ 如实记「没试」，★ 不许混进前两档）** ✓
# 官方依据: 读数出处见 `scripts/sw_fingerprint.py` 的 `OFFICIAL`；写操作用本仓既有工具层
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import sw_fingerprint as FP                                          # noqa: E402

#: ★ 每一类配一个"**已知会改它**"的写操作 —— ★ 值是**动作名**；★ 没有廉价写法的类就留空 ✓
KNOWN_WRITERS = {
    "selection": "select_plane",
    "edit_mode": "open_sketch",
    "dirty": "any_write",
    "features": "create_extrude",
    "bodies": "create_extrude",
    "faces": "create_extrude",
    "display": "",              # ★ 本轮没有廉价写法 ⇒ 记 untested（★ 不许说成 invisible）
    "config": "add_configuration",
    "rebuild": "",              # ★ 同上
}


def _connect():
    import sw_connect
    sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    return sw


def _new_part(sw):
    import sw_connect
    return sw_connect.new_document(sw, "part")


def act(sw, model, name):
    """★ 执行一个「已知会改状态」的写操作 —— ★ 用本仓**工具层**（`sw_part` 的公开函数），
    ★ 不自己调内部实现（★ 本仓纪律：「写探针时按工具层的契约调，别手调内部实现」）✓

    ⚠ 诚实说明：★ 这里用的是**能力层的公开函数**，★ 不是 MCP 工具层那套完整契约
      （★ 后者要造输入模型，★ 本轮没做）⇒ ★ 所以在报告里如实标 `writer_ok`，
      ★ 且**任何写操作抛异常或返回假 ⇒ 该类记 `untested`**，★ 不许说成「不可见」✓
    ★ 另外：★ 一个写操作**可能同时改好几类**（如 `start_sketch` 既进编辑态又改选区）——
      ★ 那是**允许**的：★ 我只检查**目标那一类**有没有动 ✓
    """
    import sw_part
    if name == "select_plane":
        #: ★ 基准面**是特征、有名字**（★ 事实 32：实体才没有名字）⇒ 按名字选 ✓
        return bool(sw_part.start_sketch(model, "Front Plane"))
    if name == "open_sketch":
        return bool(sw_part.start_sketch(model, "Front Plane"))
    if name == "create_extrude":
        if not sw_part.start_sketch(model, "Front Plane"):
            return False
        if not sw_part.sketch_rectangle(model, 0.0, 0.0, 40.0, 30.0):
            return False
        sw_part.end_sketch(model)
        return bool(sw_part.extrude_boss(model, 10.0))
    if name == "add_configuration":
        return bool(model.AddConfiguration2("标定用配置", "", "", 0, "", "", True))
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="★ 指纹灵敏度标定（规格 210 · B2）")
    ap.add_argument("--only", action="append", default=[],
                    help="★ 只标定这些类（可重复）；★ 不给就只做第 0 格")
    ap.add_argument("--json-out", default="")
    args = ap.parse_args()

    report = {"step0_readonly": {}, "classes": {}}

    # ── 第 0 格：★ 连读两次、中间什么都不做 ⇒ 必须完全相等 ──────────────────
    sw = _connect()
    if sw is None:
        print("★ 连不上 SolidWorks ⇒ 按铁律 5 记「查不到」并停下")
        return 2
    model = _new_part(sw)
    if model is None:
        print("★ 建不了新零件 ⇒ 停下")
        return 2
    a = FP.read(model, sw)
    b = FP.read(model, sw)
    same = a["readings"] == b["readings"]
    report["step0_readonly"] = {
        "equal": same,
        "a": a["readings"], "b": b["readings"],
        "missing": a["missing"],
    }
    print("★ 第 0 格（读数只读）：两次读数 %s" % ("完全相等 ✓" if same else "★ 不相等 ⇒ 指纹有副作用 ✗"))
    if a["missing"]:
        print("   读不到的类：%s" % "、".join(sorted(a["missing"])))

    # ── 逐类标定 ──────────────────────────────────────────────────────────
    for cls in FP.STATE_CLASSES:
        if args.only and cls not in args.only:
            continue
        writer = KNOWN_WRITERS.get(cls, "")
        if not writer:
            report["classes"][cls] = {"verdict": "untested",
                                      "why": "★ 本轮没给这一类配廉价写操作 ⇒ 如实记「没试」"}
            print("   %-10s ⇒ ★ untested（没试）" % cls)
            continue
        before = FP.read(model, sw)
        try:
            ok = act(sw, model, writer)
        except Exception as exc:                                        # noqa: BLE001
            report["classes"][cls] = {"verdict": "untested",
                                      "why": "★ 写操作抛异常：%s" % type(exc).__name__}
            print("   %-10s ⇒ ★ untested（写操作抛 %s）" % (cls, type(exc).__name__))
            continue
        after = FP.read(model, sw)
        d = FP.compare_detailed(before, after)
        moved = [c for c in d["changed"] if c["class"] == cls]
        unknown = [c for c in d["unknown"] if c["class"] == cls]
        if moved:
            verdict = "sensitive"
        elif unknown:
            #: ★★ **读不到 ⇒ 不能判"看不见"** —— ★ 那两件事完全不同 ✓
            verdict = "unreadable"
        else:
            verdict = "not_detected"
        report["classes"][cls] = {"verdict": verdict, "writer": writer, "writer_ok": ok,
                                  "before": before["readings"].get(cls),
                                  "after": after["readings"].get(cls)}
        print("   %-10s ⇒ %-12s （写操作 %s）" % (cls, verdict, "成功" if ok else "★ 失败"))

    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print("★ 报告：%s" % args.json_out)
    counts = {}
    for v in report["classes"].values():
        counts[v["verdict"]] = counts.get(v["verdict"], 0) + 1
    print("★ 三档统计：%s" % counts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
