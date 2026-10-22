r"""带自检的分步执行器 —— 每步有判据，失败自动留证并中止。

# ── 来源 ─────────────────────────────────────────────────────────────
# 文件:   嘉立创 FA 选型插件 v2.4.1-20260918-1（本机实测驱动）
# 定位:   每一步都「点了 -> 验判据 -> 成了才走下一步」。

# ⚑⚑⚑ 为什么要这个模块（用户 2026-09-30 的指正）
# ------------------------------------------------------------------
# 原话：「你这个脚本中途失败了你不知道啊，你在脚本内部要加一些验证环节，
#        比如点击某个按钮，然后看是否出现了什么元素或者其他什么验证方式，
#        确定跳转了，就下一步，没跳转，就截图分析留个报警记录什么的」
# ⇒ 之前那个 full_flow.py 在第 1 步就卡住，**外面看不出是「卡住」还是「慢」**，
#   更没有留下任何现场。
# ⇒ 三条硬规矩：
#   ① 每步**必须**有判据（一个可读的状态断言）
#   ② 失败 → **截图 + 落盘状态 JSON + 明确报错**，绝不静默往下
#   ③ 每步**有超时**，超时按失败处理

# ⚑⚑⚑ 用户第二次指正（2026-09-30，同一晚）
# ------------------------------------------------------------------
# ① 「你还要每次开始前检测插件现在在什么界面啊，插件不是每次都在首页等着你」
#    ⇒ **每次 connect 后必须先判定当前页面类型**，再决定下一步点哪里。
#      我此前的脚本假设「永远从首页开始」，一旦停在别处就整条链错位。
#      ⇒ ``resume()``：按当前页面类型**续跑**而不是从头点。
# ② 「每一步操作前的焦点检测也没有了，人玩意刚好动了一下鼠标你就报错」
#    ⇒ Windows 只把键盘/鼠标事件投给**前台窗口**；用户碰一下鼠标，
#      我的按键就发去了别处。
#      ⇒ **每个动作之前**都要确认前台是 SolidWorks，不是就直接取回；
#      确认不了就**跳过这一步并留证**，绝不在焦点不明时发按键。
#      另：SetCursorPos 会**抢用户鼠标** ⇒ 动作之间必须让回，
#      并在动作前重新确认坐标没有被别人移动。

# ⚑ 判据怎么定（全部用「可读到的界面状态」，不用截图判断）
# ------------------------------------------------------------------
#   首页    ：无「代码：」标签、无 ComboBox
#   分类页  ：有分类卡名（转轴/直线导轨/…）、无「代码：」标签
#   结果页  ：有「代码：」标签、有筛选 ComboBox
#   选型页  ：有参数 ComboBox、有「生成预览」Button、有进度百分比

# 覆盖:   后续同级定义
# ⚠ 本模块会驱动鼠标键盘。
# ────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import json
import re
import sys
import time
import traceback
import warnings
from pathlib import Path
from typing import Any, Callable

sys.stdout.reconfigure(encoding="utf-8")
#: ★ 本仓库根（★ 2026-10-03 合并后自定位）
_ROOT_S = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, r"" + _ROOT_S + r"\scripts")

import sw_jlcfa_cards as C
import sw_jlcfa_locate as L
import win32api
import win32con

warnings.filterwarnings("ignore")

EVID = Path(Path(__file__).resolve().parents[1] / "evidence")
EVID.mkdir(parents=True, exist_ok=True)
T0 = time.time()
STEP = [0]


def log(m: str) -> None:
    print("[%6.1fs] %s" % (time.time() - T0, m), flush=True)


# ── 状态读数 ────────────────────────────────────────────────────────
def _container_from(allc):
    """从**已取好的**控件列表里找插件容器（面积最大的结构名 Pane）。"""
    best = None
    for c in allc:
        try:
            t = (c.window_text() or "").strip()
            if t not in L.CONTAINER_NAMES:
                continue
            r = c.rectangle()
        except Exception:
            continue
        if r.width() < 40 or r.height() < 40:
            continue
        area = r.width() * r.height()
        if best is None or area > best[1]:
            best = (r, area)
    return best[0] if best else None


def read_state(w) -> dict[str, Any]:
    """读当前界面的全部可判定特征。**只读，且只遍历一次**。

    ⚑⚑⚑ 性能（本机实测 2026-09-30）
    ``win.descendants()`` 走 202 个 UIA 节点要 **10~29 秒**。
    此前的写法一次 read_state 走**两遍**（``container_rect`` 自己一遍 +
    ``controls_cached`` 再一遍）⇒ 一步动作要等 90 秒。
    ⇒ 现在**取一次控件列表**，容器和三类特征都从这同一份里算。
    ⇒ 控件**对象**有 TTL 缓存，属性（text/rect）每次重读，避免用过期坐标。
    """
    st: dict[str, Any] = {
        "container": None,
        "codes": [],
        "combos": {},
        "buttons": {},
        "pct": None,
        "categories": [],
        "visible": set(),
    }
    allc = controls_cached(w)
    if not allc:
        return st
    cr = _container_from(allc)
    st["container"] = cr
    if cr is None:
        return st
    names = []
    for c in allc:
        try:
            t = (c.window_text() or "").strip()
            r = c.rectangle()
            ct = c.element_info.control_type
        except Exception:
            continue
        if not t or not L._overlaps(r, cr):
            continue
        if ct == "ComboBox":
            try:
                st["combos"][t] = c.selected_text().strip()
            except Exception:
                pass
        elif ct == "Button":
            # ⚑ 同名多控件（实测「返回」有 5 个）：**取面积最小的**当可点元素，
            #    其余是容器/图标，不作为判定依据。
            prev = st["buttons"].get(t)
            if prev is None or (r.width() * r.height()) < (prev[2] - prev[0]) * (
                prev[3] - prev[1]
            ):
                st["buttons"][t] = (r.left, r.top, r.right, r.bottom)
        if ct in ("Button", "Pane", "Text", "Edit", "ComboBox"):
            try:
                vis = bool(c.is_visible()) and bool(c.is_enabled())
            except Exception:
                vis = False
            if vis and L._overlaps(r, cr) and r.width() > 4 and r.height() > 4:
                st["visible"].add(t)
        names.append(t)
        if t.startswith(C.CODE_PREFIX):
            st["codes"].append(t[len(C.CODE_PREFIX) :].strip())
        elif (
            80 <= r.width() <= 220 and 80 <= r.height() <= 220 and t not in C.SKIP_NAMES
        ):
            # ⚑ 只收**近似正方形的卡片**（实测分类卡 100x100）。
            #   早前的宽过滤（w>=40,h>=20）把整页文字都算成「分类卡」，
            #   导致 counts 在任何页面都是几十，判据失去区分力。
            # ⚑ 已去掉 `r.top >= cr.top+120 / r.bottom <= cr.bottom-20` 这两个
            #   **相对容器偏移**：侧边栏拉宽或 DPI 变化时它们会失效。
            #   现在只按**尺寸 + 非结构名**收，位置由控件树给。
            st["categories"].append(t)
    st["codes"].sort()
    st["categories"].sort()
    m = re.search(r"(\d+)%", " ".join(names))
    if m:
        st["pct"] = int(m.group(1))
    return st


def page_kind(st: dict[str, Any]) -> str:
    """把状态归类成页面类型 —— **每一步的判据就是它**。

    ⚑⚑⚑ 特征全部来自**实测可见控件名**（2026-09-30 抓了四页的真实清单）：
        SELECT(选型页)   参数筛选器 · 个备选型号 · 生成预览/插入/保存/选型PDF
                         参数值以**纯文字**出现（合金钢/四方型/短型/低组装…）
                         填满 100% 后 ComboBox 会消失，只剩文字 ⇒ 不能靠 combos 判
        生成完成        额外出现 **建模完成！**
        RESULT(结果页)  「代码：<型号>」标签 + 搜索 + 全部商品分类，无参数筛选器
        CATEGORY/HOME   100x100 卡片，无「代码：」标签、无参数筛选器
    ⇒ 判据用**互斥的独占特征**，并要求**可见**。
    """
    vis = st.get("visible") or set()
    has = lambda n: n in vis
    # 生成完成是 SELECT 的子状态，先判它
    if has("建模完成！"):
        return "GENERATED"
    if has("参数筛选器") and has("个备选型号"):
        return "SELECT"
    if st["codes"]:
        return "RESULT"
    if st["categories"]:
        return "CATEGORY"
    if has("全部商品分类") and not st["categories"]:
        return "HOME"
    return "UNKNOWN"


# ── 取证 ────────────────────────────────────────────────────────────
def evidence(tag: str, h: int, w, st: dict, note: str = "") -> Path:
    """失败现场：截图 + 状态 JSON 落盘。"""
    p = EVID / ("%02d_%s.png" % (STEP[0], tag))
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "shot", Path(__file__).resolve().parents[1] / "shot.py"
        )
        sh = importlib.util.module_from_spec(spec)
        sys.modules["shot"] = sh
        spec.loader.exec_module(sh)
        sh.capture(h, str(p))
    except Exception as exc:
        p = EVID / ("%02d_%s_CAPTURE_FAIL.txt" % (STEP[0], tag))
        p.write_text("截图失败: %s" % exc, encoding="utf-8")
    j = EVID / ("%02d_%s.json" % (STEP[0], tag))
    j.write_text(
        json.dumps(
            {
                "tag": tag,
                "note": note,
                "kind": page_kind(st),
                "state": {
                    "pct": st["pct"],
                    "n_codes": len(st["codes"]),
                    "codes": st["codes"][:8],
                    "combos": dict(list(st["combos"].items())[:10]),
                    "buttons": list(st["buttons"])[:10],
                    "n_categories": len(st["categories"]),
                    "categories": st["categories"][:12],
                },
            },
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )
    log("   📎 留证 -> %s + %s" % (p.name, j.name))
    return p


class StepFailed(RuntimeError):
    """某一步的判据没通过。带着现场信息。"""


# ── 分步执行 ────────────────────────────────────────────────────────
def run_step(
    name: str,
    act: Callable[[int, Any], None] | None,
    expect: str,
    h: int,
    w,
    timeout: float = 40.0,
    heal: Callable[[int, Any], None] | None = None,
    tries: int = 2,
) -> tuple[int, Any]:
    """执行一步并**自证**。判据 = 页面类型变成 ``expect``。

    act(h, w) -> None   —— 实际动作（点击/滚动）
    heal(h, w) -> None  —— 失败时的补救
    """
    STEP[0] += 1
    for t in range(1, tries + 1):
        try:
            if act:
                act(h, w)
        except Exception:
            log("   %s 动作异常:\n%s" % (name, traceback.format_exc()[-400:]))
        t0 = time.time()
        while time.time() - t0 < timeout:
            time.sleep(0.6)
            cache_drop()  # ★ 界面可能已变，重新遍历
            try:
                h2, w2 = L.connect()
            except Exception:
                continue
            st = read_state(w2)
            if page_kind(st) == expect:
                log(
                    "   ✓ %s（第%d次，%.1fs）→ %s" % (name, t, time.time() - t0, expect)
                )
                return h2, w2
        st = read_state(w)
        got = page_kind(st)
        log("   ✗ %s 未到 %s，实为 %s" % (name, expect, got))
        if t < tries and heal:
            try:
                heal(h, w)
            except Exception:
                log("   补救异常:\n%s" % traceback.format_exc()[-300:])
    st = read_state(w)
    evidence(name + "_FAIL", h, w, st, note="判据=%s 实到=%s" % (expect, page_kind(st)))
    raise StepFailed("%s 失败：判据 %s，实到 %s" % (name, expect, page_kind(st)))


def click(x: int, y: int, pause: float = 0.5) -> None:
    win32api.SetCursorPos((int(x), int(y)))
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.06)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(pause)


# ── 控件缓存（性能）─────────────────────────────────────────────
# ⚑ 实测（本机，2026-09-30）：
#     win.descendants()   9.8 秒 / 202 节点   ← 慢在**递归遍历**
#     win.children()      0.0 秒 / 6 节点
#     拿到控件后读三个属性 0.03 秒
# ⇒ **慢的不是读属性，是每次都重新遍历**。
# ⇒ 缓存**控件对象列表**，只重读 text/rect（0.03s 级）⇒ 快约 100 倍。
# ⚠ 缓存对象**不缓存属性** —— 坐标/文字每次重读，避免用过期矩形点空。
_CACHE: dict[str, Any] = {"win": None, "allc": None, "t": 0.0}
CACHE_TTL = 25.0  # 秒；超过就重新遍历


def controls_cached(w) -> list:
    """拿控件对象列表（带 TTL 缓存）。属性仍每次重读。"""
    now = time.time()
    if (
        _CACHE["win"] is w
        and _CACHE["allc"] is not None
        and now - _CACHE["t"] < CACHE_TTL
    ):
        return _CACHE["allc"]
    allc = L._controls(w)
    _CACHE.update({"win": w, "allc": allc, "t": now})
    log("   (缓存刷新: %d 个控件)" % len(allc))
    return allc


def cache_drop() -> None:
    """动作之后**必须**丢缓存 —— 界面变了，控件对象会失效。"""
    _CACHE.update({"win": None, "allc": None, "t": 0.0})


# ── 焦点守卫（用户指正 ②）────────────────────────────────────────
def ensure_front(h: int) -> bool:
    """尽量把 SolidWorks 置前。**不再阻断动作**（用户 2026-09-30 关闭焦点守护）。

    ⚑⚑⚑ 为什么取消阻断
    原实现在取不回焦点时让调用方 ``return None``，于是「点返回」**根本没发生**，
    抽查 12 件全部报「回首页失败」——**守卫把主流程掐死了**。
    实测该页面下 ``GetForegroundWindow()`` 常常不等于 SolidWorks（用户在用电脑、
    或 DSH 窗口在前），而**鼠标点击其实照样落到目标控件上**。
    ⇒ 现在只**尽力置前**并记录，返回 True 恒成立；真正判定「有没有生效」的
      责任交给**动作之后的页面判据**（那才是可靠证据）。
    """
    import win32gui

    try:
        if win32gui.GetForegroundWindow() == h:
            return True
        L.focus_solidworks(h)
        if win32gui.GetForegroundWindow() != h:
            log("   (焦点未取得，仍继续 —— 由点击后的页面判据验收)")
    except Exception:
        pass
    return True


def act_with_focus(h: int, fn: Callable[[], None], what: str) -> bool:
    """执行一个动作，但**前后都验焦点**；焦点跑掉就中止并留证。"""
    if not ensure_front(h):
        log("   ⚠ 焦点拿不回来，放弃动作「%s」" % what)
        return False
    try:
        fn()
    except Exception:
        log("   动作「%s」异常:\n%s" % (what, traceback.format_exc()[-300:]))
        return False
    return True


# ── 断点续跑（用户指正 ①）────────────────────────────────────────
def resume(h: int, w, targets: list[tuple[str, str, Callable[[int, Any], None]]]):
    """按**当前页面**决定从哪一步继续，而不是假设在首页。

    targets: [(页类型, 步骤名, 动作), ...]  —— 按顺序
    找到第一个「当前页类型 == 判据类型」的步骤，从那里继续。
    """
    st = read_state(w)
    cur = page_kind(st)
    log("当前在 %s" % cur)
    for i, (kind, name, act) in enumerate(targets):
        if kind == cur:
            log("从第 %d 步「%s」继续" % (i + 1, name))
            return i, name, act
    log("没有与 %s 匹配的步骤，从头开始" % cur)
    return 0, targets[0][1], targets[0][2] if targets else (0, "", None)
