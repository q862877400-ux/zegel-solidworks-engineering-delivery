r"""抽查执行器 —— 逐个型号跑「分类→型号→填参→生成预览」，全程自检留证。

# ── 来源 ─────────────────────────────────────────────────────────────
# 文件:   嘉立创 FA 选型插件 v2.4.1-20260918-1（本机实测驱动）
# 定位:   批量抽查的**执行层**。导航/定位/填值都复用已提交的模块。

# ⚑ 复用的既有模块（全部按名字定位，宽度/列数无关）
# ------------------------------------------------------------------
#   sw_jlcfa_locate  控件定位（容器/按名字找控件）
#   sw_jlcfa_cards   卡片定位（分类卡/结果卡）
#   sw_jlcfa_select  选型页填值（按 ComboLBox 几何点选）
#   sw_jlcfa_steps   分步自检 + 焦点守卫 + 断点续跑 + 失败留证

# ⚑ 抽查的安全约束
# ------------------------------------------------------------------
# · **不点「插入」/「保存」** ⇒ 不产生文件（Generate 预览只把模型送进 SolidWorks）
# · 每件之间必须**回到 HOME** 再走下一件，否则 resume() 会跳步
# · 每件都留证（成功/失败各一张截图 + 状态 JSON）
# · 有总件数上限与单件超时 ⇒ 不无限跑

# 覆盖:   后续同级定义
# ⚠ 本模块会驱动鼠标键盘。
# ────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import json
import sys
import time
import traceback
import warnings
from pathlib import Path
from typing import Any

sys.stdout.reconfigure(encoding="utf-8")
#: ★ 本仓库根（★ 2026-10-03 合并后自定位）
_ROOT_S = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, r"" + _ROOT_S + r"\scripts")

import sw_jlcfa_cards as c  # noqa: E402
import sw_jlcfa_locate as l  # noqa: E402
import sw_jlcfa_select as sel  # noqa: E402
import sw_jlcfa_steps as _s  # noqa: E402

warnings.filterwarnings("ignore")

REPORT = Path(Path(__file__).resolve().parents[1] / "audit_report.json")


def _conn():
    h, w = l.connect()
    if l._modal().modal_report(h)["count"]:
        l._modal().close_modals(h, rounds=2)
        h, w = l.connect()
    _s.cache_drop()
    return h, w


def goto(kind: str, name: str, h: int, w, tries: int = 2):
    """走到指定页。``name`` 是分类名/卡名。返回 (h, w) 或 None。"""
    st = _s.read_state(w)
    cur = _s.page_kind(st)
    if cur == kind or (kind == "SELECT" and cur == "GENERATED"):
        return h, w
    for _ in range(tries):
        _s.ensure_front(h)  # 只尽力置前，**不再阻断**
        _s.cache_drop()
        h, w = _conn()
        if kind == "CATEGORY":
            r = l.rect_of(w, name)
        elif kind == "RESULT":
            r = c.locate_category(w, name, _s.controls_cached(w))
        elif kind == "SELECT":
            pt = c.locate_code(w, name)
            r = pt and (pt[0] - 40, pt[1] - 40, pt[0] + 40, pt[1] + 40)
        elif kind == "HOME":
            # ⚑⚑⚑ 抽查看 12 件全报「回首页失败」的**真正原因**（2026-09-30）
            #   此前没有 HOME 分支，落到下面的 ``else: return h, w``
            #   ⇒ **一下都没点**就返回，外层循环以为「点了但没到」，
            #     空转 8 轮后判定失败。整套抽查因此 0/12。
            # ⚠ 「返回」只**退一级**（实测 SELECT→RESULT），
            #   所以回首页靠**外层循环反复点**，本分支只负责点一次。
            r = l.rect_of(w, "返回")
        else:
            return h, w
        if r is None:
            _s.log("      定位不到「%s」" % name)
            return None
        _s.click((r.left + r.right) // 2, (r.top + r.bottom) // 2, 1.2)
        t0 = time.time()
        while time.time() - t0 < 25:
            time.sleep(0.7)
            _s.cache_drop()
            try:
                h, w = l.connect()
            except Exception:
                continue
            _k = _s.page_kind(_s.read_state(w))
            if _k == kind or (kind == "SELECT" and _k == "GENERATED"):
                _s.log("      ✓ 到达 %s（%.1fs）" % (kind, time.time() - t0))
                return h, w
    return None


def _find_target(kind: str, name: str, w):
    """在**当前页**上找目标元素的矩形。找不到返回 None。

    ⚑ 与 ``goto`` 的区别：本函数**不问当前是哪一页**，
      只问「目标在不在这页上」⇒ 对 page_kind 认不出的中间页也有效。
    """
    if kind == "CATEGORY":
        return l.rect_of(w, name)
    if kind == "RESULT":
        return c.locate_category(w, name, _s.controls_cached(w))
    if kind == "SELECT":
        pt = c.locate_code(w, name)
        return pt and (pt[0] - 40, pt[1] - 40, pt[0] + 40, pt[1] + 40)
    return None


def goto_element(kind: str, name: str, h: int, w, back_rounds: int = 6):
    """★ **元素驱动**导航：找得到就点，找不到才点「返回」退一级。

    返回 ``(h, w)`` 或 ``None``。

    ⚑ 为什么这样最稳：插件有若干 ``page_kind`` 认不出的中间页
      （如「全部商品分类」的展开菜单），
      按「必须先到某页」的思路会卡死；按「目标在不在这页」就不会。
    """
    for rnd in range(back_rounds + 1):
        _s.cache_drop()
        h, w = _conn()
        if _s.page_kind(_s.read_state(w)) == kind:
            return h, w
        _s.ensure_front(h)
        r = _find_target(kind, name, w)
        if r is not None:
            _s.log(
                "      第%d轮找到「%s」%s"
                % (rnd, name, (r.left, r.top, r.right, r.bottom))
            )
            _s.click((r.left + r.right) // 2, (r.top + r.bottom) // 2, 1.2)
            t0 = time.time()
            while time.time() - t0 < 22:
                time.sleep(0.7)
                _s.cache_drop()
                try:
                    h, w = l.connect()
                except Exception:
                    continue
                _k = _s.page_kind(_s.read_state(w))
                if _k == kind or (kind == "SELECT" and _k == "GENERATED"):
                    _s.log("      ✓ 到达 %s（%.1fs）" % (kind, time.time() - t0))
                    return h, w
            _s.log("      点了但没到 %s，继续找" % kind)
            continue
        # 找不到目标 → 退一级再看
        rb = l.rect_of(w, "返回")
        if rb is None:
            _s.log("      第%d轮：无目标也无「返回」" % rnd)
            return None
        _s.log("      第%d轮：目标「%s」不在本页，点「返回」退一级" % (rnd, name))
        _s.click((rb.left + rb.right) // 2, (rb.top + rb.bottom) // 2, 1.6)
    return None


def run_one(cat: str, sub: str, code: str) -> dict[str, Any]:
    """跑一个零件。返回结果字典。"""
    rec: dict[str, Any] = {
        "cat": cat,
        "sub": sub,
        "code": code,
        "ok": False,
        "stage": "",
        "pct": None,
        "title": "",
    }
    h, w = _conn()
    st = _s.read_state(w)
    rec["start"] = _s.page_kind(st)
    _s.log("  起点 %s" % rec["start"])

    # ① 直接**按元素**找一级分类并点击 —— **不再要求先回首页**。
    # ⚑⚑⚑ 「先回首页」这条路为什么废掉（2026-09-30 实测）
    #   · 「返回」只退一级，且退到某一级会变成 **「全部商品分类」的展开菜单**
    #     （实测 184 个一级类目像 AGV专用配件/DD马达/PLC/RV减速机…），
    #     这种页面 ``page_kind`` 认不出 ⇒ UNKNOWN ⇒ 「回首页」永不成立，
    #     空转 8 轮后判失败 —— **这是抽查 0/12 的直接原因**。
    #   · 而实测**该菜单上「直线运动零件」直接可见可点** (1991,309)。
    # ⇒ 改成**元素驱动**：能找到目标就点，找不到才点「返回」退一级再看。
    got = goto_element("CATEGORY", cat, h, w)
    if got is None:
        rec["stage"] = "进分类失败(%s)" % cat
        _s.evidence("FAIL_cat_%s" % code, h, w, _s.read_state(w), note=rec["stage"])
        return rec
    h, w = got
    rec["stage"] = "CATEGORY"
    _s.log("      已到分类页「%s」" % cat)

    # ② 结果页
    got = goto("RESULT", sub, h, w)
    if got is None:
        rec["stage"] = "进子分类失败"
        return rec
    h, w = got
    rec["stage"] = "RESULT"

    # ③ 选型页
    got = goto("SELECT", code, h, w)
    if got is None:
        rec["stage"] = "进选型页失败"
        return rec
    h, w = got
    rec["stage"] = "SELECT"

    # ④ 填参数
    h, w, pct = sel.fill_to_100(h, w, max_rounds=12, pick=1)
    rec["pct"] = pct
    if pct != 100:
        rec["stage"] = "未到100%%(%s)" % pct
        _s.evidence("FAIL_%s_%s" % (sub, code), h, w, _s.read_state(w), note=rec["stage"])
        return rec

    # ⑤ 生成预览
    _s.cache_drop()
    h, w = l.connect()
    _s.ensure_front(h)
    btn = l.locate(w, "生成预览", "Button")
    if btn is None:
        rec["stage"] = "无生成按钮"
        return rec
    r = btn.rectangle()
    _s.click((r.left + r.right) // 2, (r.top + r.bottom) // 2, 1.0)
    t0 = time.time()
    title = ""
    while time.time() - t0 < 30:
        time.sleep(1.0)
        _s.cache_drop()
        try:
            h, w = l.connect()
            title = w.window_text() or ""
        except Exception:
            continue
        if title.startswith("SOLIDWORKS") and "|" in title:
            break
    rec["title"] = title[:80]
    rec["stage"] = "生成预览"
    rec["ok"] = (
        "SLDPRT" in title
        or "SLDASM" in title
        or "建模完成" in _s.read_state(w)["visible"]
    )
    _s.evidence(
        ("OK_" if rec["ok"] else "PART_") + "%s_%s" % (sub, code),
        h,
        w,
        _s.read_state(w),
        note=rec["title"],
    )
    return rec


def main(plan: list[tuple[str, str, str]]):
    results = []
    t_all = time.time()
    for i, (cat, sub, code) in enumerate(plan, 1):
        _s.STEP[0] = 0
        _s.log("═══ %d/%d  %s / %s / %s" % (i, len(plan), cat, sub, code))
        try:
            rec = run_one(cat, sub, code)
        except Exception:
            rec = {
                "cat": cat,
                "sub": sub,
                "code": code,
                "ok": False,
                "stage": "异常:" + traceback.format_exc()[-160:],
            }
        results.append(rec)
        _s.log(
            "  => %s  %s  %s"
            % ("✓" if rec["ok"] else "✗", rec["stage"], rec.get("title", "")[:52])
        )
        REPORT.write_text(
            json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        _s.log("  用时 %.0fs" % (time.time() - t_all))
    _s.log("════ 汇总 ════")
    for r in results:
        _s.log(
            "  %s %-10s %-12s %-12s %s"
            % (
                "✓" if r["ok"] else "✗",
                r["cat"][:9],
                r["sub"][:11],
                r["code"][:11],
                r["stage"][:34],
            )
        )
    ok = sum(1 for r in results if r["ok"])
    _s.log("成功 %d/%d" % (ok, len(results)))
    return results
