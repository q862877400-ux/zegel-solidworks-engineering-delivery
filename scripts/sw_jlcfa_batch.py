r"""批量抽查 —— **搜索式**取件，逐件自检留证。

# ── 来源 ─────────────────────────────────────────────────────────────
# 文件:   嘉立创 FA 选型插件 v2.4.1-20260918-1（本机实测驱动）
# 定位:   「每类抽查若干件」的执行层。

# ⚑⚑⚑ 为什么用搜索而不是分类导航（2026-09-30 本机实测，走了很多弯路）
# ------------------------------------------------------------------
# 分类导航的死路：插件**滚动内容区在 UIA 里报虚拟坐标**
#   · 容器 rect (1955,115,2563,1361) 是视口坐标（对）
#   · 但 125 张卡片 y = 2509…8975（远超容器）⇒ **卡片 rect 不能点**
#   · 窄侧边栏(608px)下 `搜索`/`全部商品分类` 甚至从 UIA 树消失
#   · 「返回」只退一级；退到某层是「全部商品分类」展开菜单，page_kind 认不出
# ⇒ 反复“回首页”空转，抽查 0/12。
#
# **搜索路径**实测一次通（12 秒）：
#   ① 搜索框在**固定头部**，PrintWindow 截图与屏幕 **1:1** ⇒ 坐标可靠
#   ② 数字会被逐键输入吃掉（EGH25SAZ0C → EGHSAZC）⇒ **必须剪贴板粘贴**
#   ③ Enter 不触发 ⇒ 点右侧**「搜索」按钮**
#   ④ 结果卡的横坐标从**截图**量 ⇒ 与侧边栏宽度无关
#   ⑤ 结果页 → 选型页 → 100% → 「生成预览」→ 「建模完成！」

# ⚑ 安全约束
# ------------------------------------------------------------------
# · **不点「插入」「保存」** ⇒ 不产生文件
# · 逐件留证（截图 + 状态 JSON）
# · 单件超时 / 总件数上限 ⇒ 不无限跑

# 覆盖:   后续同级定义
# ⚠ 会驱动鼠标键盘。
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
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")

import sw_jlcfa_grid as G
import sw_jlcfa_locate as L
import sw_jlcfa_fill as FILL
import sw_jlcfa_search as SR
import sw_jlcfa_select as SEL
import sw_jlcfa_steps as S

warnings.filterwarnings("ignore")

REPORT = Path(r"D:\AI\SW\batch_report.json")
EV = Path(r"D:\AI\SW\batch_evidence")
EV.mkdir(parents=True, exist_ok=True)


def _conn():
    h, w = L.connect()
    if L._modal().modal_report(h)["count"]:
        L._modal().close_modals(h, rounds=2)
        h, w = L.connect()
    S.cache_drop()
    return h, w


def _shot(h: int, w, tag: str):
    try:
        pane, _cr = G._capture(h, w)
        if pane is not None:
            pane.save(str(EV / ("%s.png" % tag)))
    except Exception:
        pass


def _wait_generated(h: int, w, secs: int = 26):
    """等「建模完成！」出现。返回 (h, w, done)。"""
    t0 = time.time()
    while time.time() - t0 < secs:
        time.sleep(1.5)
        S.cache_drop()
        try:
            h, w = L.connect()
            st = S.read_state(w)
        except Exception:
            continue
        if "建模完成！" in st["visible"]:
            return h, w, True
    return h, w, False


def run_one(cat: str, sub: str, code: str) -> dict[str, Any]:
    """搜索 → 结果 → 填参 → 生成。返回结果字典。"""
    rec: dict[str, Any] = {"cat": cat, "sub": sub, "code": code, "ok": False,
                           "stage": "", "pct": None, "title": "", "secs": 0.0}
    t0 = time.time()
    h, w = _conn()

    # ① 搜索
    rec["stage"] = "search"
    if not SR.search(h, w, code):
        rec["stage"] = "搜索框不可用"
        _shot(h, w, "FAIL_nosearch_%s" % code)
        rec["secs"] = time.time() - t0
        return rec
    # 等结果出现（判据：内容区出现大白块）
    pt = None
    for _ in range(14):
        time.sleep(1.0)
        S.cache_drop()
        try:
            h, w = L.connect()
        except Exception:
            continue
        pt = SR.first_result_point(w)
        if pt:
            break
    if not pt:
        rec["stage"] = "无搜索结果"
        _shot(h, w, "FAIL_noresult_%s" % code)
        rec["secs"] = time.time() - t0
        return rec
    rec["stage"] = "result"

    # ② 点首个结果卡
    S.ensure_front(h)
    S.click(pt[0], pt[1], 2.5)
    S.cache_drop()
    h, w = _conn()
    st = S.read_state(w)

    # ⚑⚑ 必须校验**型号行含目标型号**（2026-09-30 抓到的假阳性）：
    #   实测「搜 BMHA-0.4 后型号行仍是 BSGY-C7-25-…」——
    #   导航没生效，脚本又生成了一遍**上一个型号**，却被判成功。
    #   ⇒ 型号行对不上就是没进去，重试；仍对不上则判失败。
    def _code_ok(ww) -> bool:
        return FILL.code_present(ww, code)

    for _attempt in range(4):
        if S.page_kind(st) in ("SELECT", "GENERATED") and _code_ok(w):
            break
        S.log("      型号行未对上「%s」（现 %r），重试导航"
              % (code, FILL.model_line(w)[:38]))
        S.cache_drop()
        h, w = _conn()
        pt2 = SR.first_result_point(w)
        if pt2:
            S.ensure_front(h)
            S.click(pt2[0], pt2[1], 2.5)
        for _ in range(6):
            time.sleep(1.0)
            S.cache_drop()
            h, w = _conn()
            st = S.read_state(w)
            if S.page_kind(st) in ("SELECT", "GENERATED") and _code_ok(w):
                break
    if S.page_kind(st) not in ("SELECT", "GENERATED"):
        rec["stage"] = "未进选型页(%s)" % S.page_kind(st)
        _shot(h, w, "FAIL_noselect_%s" % code)
        rec["secs"] = time.time() - t0
        return rec
    if not _code_ok(w):
        rec["stage"] = "型号行未对上(%s)" % FILL.model_line(w)[:24]
        _shot(h, w, "FAIL_wrongmodel_%s" % code)
        rec["secs"] = time.time() - t0
        return rec
    rec["stage"] = "select"

    # ③ 填参数（下拉用鼠标点选；输入框用**真键盘逐键**）
    # ⚑ 判据是**插件自己的型号行**（`【去填写】` 个数），
    #   不是进度百分比、也不是「输入框里有没有字」——
    #   实测 ValuePattern 能让框里有字而插件不登记。
    h, w, left = FILL.fill_all(h, w)
    rec["pct"] = S.read_state(w)["pct"]
    rec["unfilled"] = left
    # ⚑⚑ **不再回退到 ``SEL.fill_to_100``**（2026-09-30）
    #   实测那条旧路径里写着 ``str(int(rg[0]))``，
    #   对范围 ``[0.5~20]/0.001`` 会算出 **0**（低于下限）⇒ 插件拒收
    #   ⇒ 就是用户看到的「一直重复输入 0」。
    #   修好的取值逻辑只在 ``FILL.fill_all`` 里，回退等于把老 bug 请回来。
    if left != 0:
        rec["stage"] = ("型号行读不到" if left < 0 else "参数未齐(缺%d)" % left)
        _shot(h, w, "FAIL_not100_%s" % code)
        rec["secs"] = time.time() - t0
        return rec

    # ④ 生成预览
    # ⚑ 刚填完参数时按钮可能**尚未渲染**（实测第 2 件就因此报「无生成按钮」，
    #   而几秒后同一控件 vis=True 在容器内）⇒ 必须**轮询等它出现**。
    S.cache_drop()
    h, w = _conn()
    btn = None
    for _ in range(10):
        btn = L.locate(w, "生成预览", "Button")
        if btn is not None:
            break
        time.sleep(1.0)
        S.cache_drop()
        h, w = _conn()
    if btn is None:
        # ⚑ 放宽查找：``L.locate`` 要求 ``is_visible()``，而该按钮
        #   **经常报不可见**（实测 BHJF 参数已全齐 `BHJF-D6-L55-M3-N3`，
        #   仍读不到按钮 ⇒ 走到截图兜底 ⇒ 点偏 ⇒ 「未出现建模完成」）。
        #   按钮只要**在插件容器内 + 名字对 + 类型对**就点它。
        for c in S.controls_cached(w):
            try:
                if (c.window_text() or "").strip() != "生成预览":
                    continue
                if c.element_info.control_type != "Button":
                    continue
                r = c.rectangle()
                cr = L.container_rect(w)
                if cr and L._overlaps(r, cr):
                    btn = c
                    S.log("      放宽查找命中生成按钮 %s"
                          % ((r.left, r.top, r.right, r.bottom),))
                    break
            except Exception:
                continue
    if btn is None:
        # ⚑ 再放宽：**连容器判定也不要**（容器 rect 在重绘瞬间可能不准），
        #   只要求「名字 + 类型」对，且坐标落在屏幕可见范围内。
        for c in S.controls_cached(w):
            try:
                if (c.window_text() or "").strip() != "生成预览":
                    continue
                if c.element_info.control_type != "Button":
                    continue
                r = c.rectangle()
                if r.width() > 0 and r.height() > 0 and r.top > 0:
                    btn = c
                    S.log("      极宽查找命中生成按钮 %s"
                          % ((r.left, r.top, r.right, r.bottom),))
                    break
            except Exception:
                continue
    # ⚑ 只用 UIA 定位按钮 —— 并集遍历修好后 ``L.locate`` 已能稳定拿到
    #   （实测 `Button '生成预览' (2362,1271,2445,1303)`）。
    #   **不再有截图兜底**：截图是症状级补丁，根因是遍历漏节点，已修。
    if btn is None:
        rec["stage"] = "无生成按钮"
        _shot(h, w, "FAIL_nobtn_%s" % code)
        rec["secs"] = time.time() - t0
        return rec
    r_btn = btn.rectangle()
    cands = [((r_btn.left + r_btn.right) // 2, (r_btn.top + r_btn.bottom) // 2)]
    # ⑤ **逐个试候选 + 验收**：点了看有没有「建模完成！」，
    #    没有就换下一个（按钮在 UIA 里时有时无，位置也只能靠截图估）。
    done = False
    for i, pt in enumerate(cands[:4], 1):
        S.log("      试生成按钮候选 #%d %s" % (i, pt))
        S.ensure_front(h)
        S.click(pt[0], pt[1], 1.0)
        h, w, done = _wait_generated(h, w, 22)
        if done:
            break
    rec["title"] = (w.window_text() or "")[:90]
    # ⚑ 判据：**建模完成！** 出现，或标题换成了新模型（含该型号前缀）
    key = code.split("-")[0][:8].lower()
    title_hit = key in (rec["title"] or "").lower()
    rec["ok"] = done or title_hit
    rec["stage"] = "生成完成" if rec["ok"] else "未出现建模完成"
    _shot(h, w, ("OK_" if rec["ok"] else "FAIL_gen_") + code)
    rec["secs"] = time.time() - t0
    return rec


def main(plan: list[tuple[str, str, str]]):
    results = []
    t_all = time.time()
    for i, (cat, sub, code) in enumerate(plan, 1):
        S.STEP[0] = 0
        S.log("═══ %d/%d  %s / %s / %s" % (i, len(plan), cat, sub, code))
        try:
            rec = run_one(cat, sub, code)
        except Exception:
            rec = {"cat": cat, "sub": sub, "code": code, "ok": False,
                   "stage": "异常:" + traceback.format_exc()[-160:], "secs": 0.0}
        results.append(rec)
        S.log("  => %s  %-22s %.0fs  %s"
              % ("✓" if rec["ok"] else "✗", rec["stage"], rec["secs"],
                 rec.get("title", "")[:44]))
        REPORT.write_text(json.dumps(results, ensure_ascii=False, indent=1),
                          encoding="utf-8")
    S.log("════ 汇总（总 %.0fs）════" % (time.time() - t_all))
    for r in results:
        S.log("  %s %-10s %-14s %-14s %.0fs  %s"
              % ("✓" if r["ok"] else "✗", r["cat"][:9], r["sub"][:13],
                 r["code"][:13], r.get("secs", 0), r["stage"][:30]))
    ok = sum(1 for r in results if r["ok"])
    S.log("成功 %d/%d" % (ok, len(results)))
    return results
