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
#: ★★ 每一类配一个**已知会改它**的写操作 —— ★ 值是 **MCP 工具名**（★ 按 `ToolSpec` 契约调）✓
#:   ★ 我第一版是**手调能力层函数**（`sw_part.xxx`）⇒ ★ 形状不对、抛 `TypeError` ✗
#:   ★★ 本仓纪律原话：「写探针验能力时：**按 `ToolSpec` 的契约调**，别手调内部实现」✓
#:   ★ 空串 = 本轮**没给这一类配写操作** ⇒ ★ 记 `untested`（★ **不许**说成「看不见」）✓
KNOWN_WRITERS = {
    "selection": "solidworks_clear_selection",
    "edit_mode": "solidworks_sketch_start",
    #: ★★ 真机实测：`sketch_start` **确实进了编辑态**（`edit_mode` = sensitive）
    #:   ★ 而 `GetSaveFlag` **没动** ⇒ ★ **进草图编辑态不算「脏」**（★ 要改几何才脏）
    #:   ⇒ ★ 所以给 `dirty` 换一个**真的改文档**的写操作 ✓
    "dirty": "solidworks_config_create",
    "features": "solidworks_extrude_boss",
    "bodies": "solidworks_extrude_boss",
    "faces": "solidworks_extrude_boss",
    "display": "",              # ★ 没有"改显示状态"的现成工具 ⇒ 记 untested
    "config": "solidworks_config_create",
    "rebuild": "solidworks_session_rebuild",
}

#: ★ 每个写操作要传的形参（★ 名字与声明一致；★ 没给的用声明里的默认值）✓
WRITER_PARAMS = {
    "solidworks_clear_selection": {},
    "solidworks_sketch_start": {},
    #: ★ 真机实测：★ `sketch_name`/`depth_mm` 的 `default` 是 `Ellipsis`（= 必填）
    #:   ⇒ ★ 必须**主动给值**，否则底层报「缺 2 个位置实参」✗
    "solidworks_extrude_boss": {"sketch_name": "Sketch1", "depth_mm": 10.0},
    "solidworks_config_create": {"name": "标定用配置"},
    "solidworks_session_rebuild": {},
}


def _connect():
    import sw_connect
    sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    return sw


def _new_part(sw):
    import sw_connect
    return sw_connect.new_document(sw, "part")


def act(sw, model, name):
    """★ 执行一个「已知会改状态」的写操作 —— ★ **按 `ToolSpec` 契约调工具** ✓

    ★ 契约（读 `tool_registry.make_tool_function` 得知）：★ 底层函数按 **kwargs** 调，
      形参名与声明一致，★ 注入对象用 **`inject` 声明的那个名字**传进去 ✓
    ★★ **拿不到 / 缺参数 / 抛异常 ⇒ 回 `(False, 原因)`** —— ★ 调用方据此记 `untested`，
      ★ **绝不许**把"没调成"说成"这一类不可见" ✗
    """
    import tool_caller
    params = dict(WRITER_PARAMS.get(name) or {})
    return tool_caller.call(name, inject_objects={"model": model, "sw": sw}, **params)


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
    #: ★★★ 第 0 格改成**三次读数、比第 2 与第 3 次** —— ★ 原因（真机现场）：
    #:   ★ 刚建好的零件**还在自行稳定**（首次读数会赶上正在变化的那一瞬）⇒
    #:   ★★ 只比第 1 与第 2 次会把"**文档自己没稳**"误判成"**读数有副作用**" ✗
    #:   ★ 正解：★ 让第 1 次读数**当"加热"用**，★ **只比第 2 与第 3 次**（★ 期间不做任何事）✓
    r1 = FP.read(model, sw)
    r2 = FP.read(model, sw)
    r3 = FP.read(model, sw)
    same = r2["readings"] == r3["readings"]
    report["step0_readonly"] = {
        "equal": same,
        "read1": r1["readings"], "read2": r2["readings"], "read3": r3["readings"],
        "read1_differs_from_2": r1["readings"] != r2["readings"],
        "missing": r2["missing"],
        "usable": r2.get("usable"),
    }
    print("★ 第 0 格（读数只读）：比**第 2 与第 3 次** ⇒ %s"
          % ("完全相等 ✓" if same else "★ 不相等 ⇒ 指纹有副作用 ✗"))
    if r1["readings"] != r2["readings"]:
        print("   （第 1 与第 2 次不同 ⇒ ★ 文档刚建好**还没稳**，★ 所以第 1 次只当加热用）")
    if not r2.get("usable"):
        print("   ★★ 指纹**失效**：%s" % r2.get("unusable_why"))
    if r2["missing"]:
        print("   读不到的类：%s" % "、".join(sorted(r2["missing"])))

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
        ok, note = act(sw, model, writer)
        if not ok:
            #: ★★ **没调成 ⇒ 记 `untested`**（★ 不许说成"不可见"）✓
            report["classes"][cls] = {"verdict": "untested", "writer": writer, "why": note}
            print("   %-10s ⇒ ★ untested（写操作没调成：%s）" % (cls, note[:70]))
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
                                  "writer_note": note[:120],
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
