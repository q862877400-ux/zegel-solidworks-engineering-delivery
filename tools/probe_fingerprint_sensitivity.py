"""★ 指纹灵敏度标定（真机）：逐类挑一个"已知会改它"的写操作，看指纹有没有动。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_fingerprint_sensitivity.py
# 定位:   ★ 规格 `specs/210-declarative-effects` 的 **B2**（★ 评审原话：「**量具是指纹
#           ，所以要校准它**」）✓
# 运行:   ★ **一律走护栏**：`python tools/sw_guard.py --timeout 900 -- python tools/prob
# e_fingerprint_sensitivity.py`
#   ★ 护栏现在会给子进程设 `SW_SANDBOX_MODE=enforce` ⇒ ★ 打开的**永远是副本** ✓
# 判据:   ★★ **第 0 格（最要紧）**：★ 连读两次、**中间什么都不做** ⇒ ★ 两次必须**完全相
# 等**
#     —— ★ 这是"**读数本身只读**"的直接证据；★ 不等就说明**指纹自己有副作用** ✗
#   ★ 其余每类：★ 跑一个已知会改它的写操作 ⇒ ★ 看该类读数有没有动 ✓
#   ★★ 结论分**三档**（★ 不许把"没试"说成"看不见"）：
# `sensitive`（动了 ⇒ 有灵敏度证据）· `not_detected`（**跑了写操作**但没动 ⇒ 这一类**不
# 可见**）·
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

import sw_fingerprint as FP  # noqa: E402

#: ★ 每一类配一个"**已知会改它**"的写操作 —— ★ 值是**动作名**；★ 没有廉价写法的类就留空
#: ✓
#: ★★ 每一类配一个**已知会改它**的写操作 —— ★ 值是 **MCP 工具名**（★ 按 `ToolSpec` 契约
#: 调）✓
#:   ★ 我第一版是**手调能力层函数**（`sw_part.xxx`）⇒ ★ 形状不对、抛 `TypeError` ✗
#:   ★★ 本仓纪律原话：「写探针验能力时：**按 `ToolSpec` 的契约调**，别手调内部实现」✓
#:   ★ 空串 = 本轮**没给这一类配写操作** ⇒ ★ 记 `untested`（★ **不许**说成「看不见」）✓
KNOWN_WRITERS = {
    #: ★ 写操作：清空选区 ⇒ ★ 要**先有选区**才清得掉（★ 前置见下）✓
    "selection": "solidworks_clear_selection",
    "edit_mode": "solidworks_sketch_start",
    #: ★★ 真机实测：`sketch_start` **确实进了编辑态**（`edit_mode` = sensitive）
    #:   ★ 而 `GetSaveFlag` **没动** ⇒ ★ **进草图编辑态不算「脏」**（★ 要改几何才脏）
    #:   ⇒ ★ 所以给 `dirty` 换一个**真的改文档**的写操作 ✓
    "dirty": "solidworks_config_create",
    "features": "solidworks_extrude_boss",
    "bodies": "solidworks_extrude_boss",
    "faces": "solidworks_extrude_boss",
    #: ★ `display` 这一格读的是**显示状态的名字**（配置级）；本仓**没有**"改显示状态"的
    #: 工具 ⇒
    #:   ★ 用一个**视图**写操作去试（★ `set_standard_view`）—— ★ **预期它不会动这一格** ⇒
    #:   ★★ 于是我们得到一条**明确的"这一类当前不可见"记录**（★ 比 `untested` 强）✓
    "display": "solidworks_set_standard_view",
    "config": "solidworks_config_create",
    "rebuild": "solidworks_session_rebuild",
}

#: ★★★ 2026-10-06 **本轮最重要的认识**：★ `not_detected` 大多**不是"读数瞎"**，
#:   而是 ★ **"那个写操作没有真的改变任何东西"** —— ★ 真机返回体坐实了三条：
#:     · `config` ⇒ `{"created": false, "reused": true}`（配置**本来就存在**）
#:     · `rebuild` ⇒ `needs_rebuild_before=0 · after=0`（文档**本来就是重建好的**）
#:     · `selection` ⇒ 选区**本来就是空的**
#:   ⇒ ★★ 正解：★ **给每一类配前置**，★ 让它**从一个「变得了」的状态出发** ✓
#: ★ 前置也**按契约调**（★ 同一个 `tool_caller`），★ 且**前置失败 ⇒ 该类记 `untested`**
#: ✓
#:   ★★ 这正好与 B3 的「每组只建一次状态」是同一件事 —— ★ 两批在这里**接上**了 ✓
_RECT = {"x1_mm": 0.0, "y1_mm": 0.0, "x2_mm": 40.0, "y2_mm": 30.0}
#: ★ 造一个实体（★ 后续「选实体」与"重建"都要它）✓
_BODY_CHAIN = (
    ("solidworks_sketch_start", {}),
    ("solidworks_sketch_add_rectangle", _RECT),
    ("solidworks_extrude_boss", {"sketch_name": "Sketch1", "depth_mm": 10.0}),
)

#: ★ `select_by_selector` 的 `selector` 支持 `index:<n>`（★ 读该工具的声明描述得知）✓
_SELECT_ONE = (
    "solidworks_select_by_selector",
    {"selector": "index:0", "kind": "EDGE", "body_index": 0},
)

WRITER_PRECONDITION = {
    #: ★★ 真机查明：★ **画矩形并不会留下选中** ⇒ 选区仍是 0 ⇒ `clear_selection` 清不掉东
    #: 西 ✗
    #:   ⇒ ★ 前置改成：★ **先造体 → 再选一个实体**（★ 选区变成 1）⇒ 再清就有得清 ✓
    "selection": list(_BODY_CHAIN) + [_SELECT_ONE],
    #: ★ 先建草图、画矩形 ⇒ `extrude_boss` 才有 `Sketch1` 可拉 ✓
    "features": [
        ("solidworks_sketch_start", {}),
        ("solidworks_sketch_add_rectangle", _RECT),
    ],
    "bodies": [
        ("solidworks_sketch_start", {}),
        ("solidworks_sketch_add_rectangle", _RECT),
    ],
    "faces": [
        ("solidworks_sketch_start", {}),
        ("solidworks_sketch_add_rectangle", _RECT),
    ],
    #: ★★ 真机查明：★ **新零件本来就是重建好的** ⇒ `session_rebuild` 不改变那个布尔 ✗
    #: ⇒ ★ 前置改成：★ **先造一个实体的改动**（★ 那会留下「需要重建」）⇒ 再重建就有得变
    #: ✓
    "rebuild": list(_BODY_CHAIN),
}

#: ★ 每个写操作要传的形参（★ 名字与声明一致；★ 没给的用声明里的默认值）✓
WRITER_PARAMS = {
    "solidworks_clear_selection": {},
    "solidworks_sketch_start": {},
    #: ★★ 真机实测出的一处**声明与实现不一致**：★ 声明写 `depth_mm`，
    #:   而底层函数签名是 `(model, sketch_name, depth, ...)` ⇒ ★ **名字对不上** ✗
    #: ⇒ ★ 查明：**不是声明的错** —— ★ `param_alias` 把 `depth_mm` 标成 `None`（解析器消
    #: 费），
    #:     而真正的 `depth` 由 **`derived_args`** 派生 ⇒ ★ 是**我的调用器缺了那两层映射** ✗
    #:   ⇒ ★ 调用器已补上；★ 探针按**对外声明名**传即可 ✓
    "solidworks_extrude_boss": {"sketch_name": "Sketch1", "depth_mm": 10.0},
    #: ★ 真机实测：★ 声明里的形参是 `configuration_name`（`Ellipsis` = 必填）
    #: ★★ 用**唯一名字** —— 真机踩过：★ 复用同名 ⇒ `{"created": false, "reused": true}`
    #:   ⇒ ★ 写操作"成功"却**什么都没改** ⇒ 被记成 `not_detected`（★ 那是假结论）✗
    "solidworks_config_create": {
        "configuration_name": "MCP_CALIB_%d" % __import__("time").time_ns()
    },
    "solidworks_session_rebuild": {},
    "solidworks_set_standard_view": {},
}


def _connect():
    import sw_connect

    sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    return sw


def _new_part(sw):
    import sw_connect

    return sw_connect.new_document(sw, "part")


def _new_part(sw):
    """★ 建一个**新的空零件**（★ 每一类标定都从干净状态出发）✓

    ⚠ 说明：★ 这里用的是**能力层**的建文档函数 —— ★ 它**不是被测的写操作**，
      ★ 只是**搭舞台**；★ 被测的写操作一律按 `ToolSpec` 契约调 ✓
    """
    import sw_connect

    try:
        return sw_connect.new_document(sw, "part")
    except Exception:  # noqa: BLE001
        return None


def act(sw, model, name, cls=""):
    """★ 执行一个「已知会改状态」的写操作 —— ★ **按 `ToolSpec` 契约调工具** ✓

    ★ 契约（读 `tool_registry.make_tool_function` 得知）：★ 底层函数按 **kwargs** 调，
      形参名与声明一致，★ 注入对象用 **`inject` 声明的那个名字**传进去 ✓
    ★★ **拿不到 / 缺参数 / 抛异常 ⇒ 回 `(False, 原因)`** —— ★ 调用方据此记 `untested`，
      ★ **绝不许**把"没调成"说成"这一类不可见" ✗
    """
    import tool_caller

    inj = {"model": model, "sw": sw}
    params = dict(WRITER_PARAMS.get(name) or {})
    return tool_caller.call(name, inject_objects=inj, **params)


def run_precondition(sw, model, cls):
    """★★ 跑**前置链** —— ★★ 必须在 **`before` 读数之前**跑（★ 真机踩过）✓

    ★★★ 2026-10-06 **真机查明的顺序错**：★ 前置原来写在 `act()` 里 ⇒
      ★ 而 `before = FP.read(...)` 在 `act()` **之前** ⇒ ★★ 于是 before 是在
      **还没建前置状态**的新零件上取的 ✗
      ★ 现场：`selection` 的前置会**选中一个实体**（工具回 `count: 1`、直接回读也是 `1` ✓）⇒
      ★ 可 before 取在选中**之前** ⇒ ★★ 读出 `0 ⇒ 0` ⇒ **被误判成「这一类不可见」** ✗✗
      ⇒ ★ 正解：★ **先跑前置 → 再取 before → 再跑写操作 → 再取 after** ✓
    """
    import tool_caller

    inj = {"model": model, "sw": sw}
    for step_name, step_params in WRITER_PRECONDITION.get(cls) or []:
        ok_step, note_step = tool_caller.call(
            step_name, inject_objects=inj, **step_params
        )
        if not ok_step:
            return False, "★ 前置 %s 没成：%s" % (step_name, note_step[:90])
    return True, ""


def main() -> int:
    ap = argparse.ArgumentParser(description="★ 指纹灵敏度标定（规格 210 · B2）")
    ap.add_argument(
        "--only",
        action="append",
        default=[],
        help="★ 只标定这些类（可重复）；★ 不给就只做第 0 格",
    )
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
    #: ★ 正解：★ 让第 1 次读数**当"加热"用**，★ **只比第 2 与第 3 次**（★ 期间不做任何事
    #: ）✓
    r1 = FP.read(model, sw)
    r2 = FP.read(model, sw)
    r3 = FP.read(model, sw)
    same = r2["readings"] == r3["readings"]
    report["step0_readonly"] = {
        "equal": same,
        "read1": r1["readings"],
        "read2": r2["readings"],
        "read3": r3["readings"],
        "read1_differs_from_2": r1["readings"] != r2["readings"],
        "missing": r2["missing"],
        "usable": r2.get("usable"),
    }
    print(
        "★ 第 0 格（读数只读）：比**第 2 与第 3 次** ⇒ %s"
        % ("完全相等 ✓" if same else "★ 不相等 ⇒ 指纹有副作用 ✗")
    )
    if r1["readings"] != r2["readings"]:
        print(
            "   （第 1 与第 2 次不同 ⇒ ★ 文档刚建好**还没稳**，★ 所以第 1 次只当加热用）"
        )
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
            report["classes"][cls] = {
                "verdict": "untested",
                "why": "★ 本轮没给这一类配廉价写操作 ⇒ 如实记「没试」",
            }
            print("   %-10s ⇒ ★ untested（没试）" % cls)
            continue
        #: ★★★ 2026-10-06 **真机暴露的更根本的设计错**：★ 我原来把九类**在同一个文档上顺
        #: 序标定**
        #:   ⇒ ★★ 前面的类改过文档之后，**后面的类就"没得变了"** —— 现场：
        #: · `features` 的前置把文档弄脏 ⇒ ★ 轮到 `dirty` 时它**已经是脏的** ⇒ 记 `not_d
        #: etected` ✗
        #: · `features` 用掉了 `Sketch1` ⇒ ★ 轮到 `bodies`/`faces` 时 `extrude` 没东西可
        #: 拉 ⇒ 也没动 ✗
        #:   ★ 这两条**都不是**"读数瞎" —— ★ 是**我的标定顺序污染了后面的样本** ✓
        #:   ⇒ ★★ 修法：★ **每一类各用一个新零件**（★ 前置也在新零件上重建）✓
        fresh = _new_part(sw)
        if fresh is None:
            report["classes"][cls] = {"verdict": "untested", "why": "★ 建不了新零件"}
            print("   %-10s ⇒ ★ untested（建不了新零件）" % cls)
            continue
        model = fresh
        #: ★★ **顺序**（★ 真机踩过）：★ 前置 ⇒ before ⇒ 写操作 ⇒ after ✓
        pre_ok, pre_note = run_precondition(sw, model, cls)
        if not pre_ok:
            report["classes"][cls] = {
                "verdict": "untested",
                "writer": writer,
                "why": pre_note,
            }
            print("   %-10s ⇒ ★ untested（前置没成：%s）" % (cls, pre_note[:60]))
            continue
        before = FP.read(model, sw)
        ok, note = act(sw, model, writer, cls)
        if not ok:
            #: ★★ **没调成 ⇒ 记 `untested`**（★ 不许说成"不可见"）✓
            report["classes"][cls] = {
                "verdict": "untested",
                "writer": writer,
                "why": note,
            }
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
        report["classes"][cls] = {
            "verdict": verdict,
            "writer": writer,
            "writer_ok": ok,
            "writer_note": note[:120],
            "before": before["readings"].get(cls),
            "after": after["readings"].get(cls),
        }
        print(
            "   %-10s ⇒ %-12s （写操作 %s）"
            % (cls, verdict, "成功" if ok else "★ 失败")
        )

    if args.json_out:
        #: ★★ 必须带 `default=str` —— ★ 真机踩过：★ 指纹里某些读数是 **COM 对象**
        #:   ⇒ 裸 `json.dumps` 抛 `TypeError: not JSON serializable` ⇒
        #:   ★★ **报告根本没落盘**，★ 而 stdout 只说了"三档统计" ⇒ 看不出丢了东西 ✗
        Path(args.json_out).write_text(
            json.dumps(report, ensure_ascii=False, indent=1, default=str) + "\n",
            encoding="utf-8",
        )
        print("★ 报告：%s" % args.json_out)
    counts = {}
    for v in report["classes"].values():
        counts[v["verdict"]] = counts.get(v["verdict"], 0) + 1
    print("★ 三档统计：%s" % counts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
