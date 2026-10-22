"""★ 规格 204 / SC-005：批 79 的真机验证 —— **FR-008 的两半**（爆炸视图 + 宏执行）。

★ 一正一反两个场景（本仓惯例）：
  · 爆炸视图：正例 = 真装配体上建爆炸视图并**回读数**；反例 = 对零件文档调它（应失败/不建）
  · 宏执行：正例 = 跑我们自己的 `.swb`；反例 = 不存在的路径（应回 False + 错误码 28）
⚠ 用户原件**只读**：先把装配体**复制**到 `output/` 再打开（本脚本只动副本）。
"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   `scripts/sw_assembly_doc.py`（本批新增的 9 个爆炸视图包装）· `scripts/sw_macro
# .py`（新建）
#         `C:\\swapi\\types\\IAssemblyDoc\\*.md` · `C:\\swapi\\types\\ISldWorks\\RunMacro2.md`
# 定位:   规格 `specs/204-tool-ramp/spec.md` 的 **SC-005**（FR-008 两块各至少 1 个工具
#           并**真机跑过**）
# 官方依据: 逐页见上面两个模块的来源块
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ⚠ 真机脚本：跑之前确认只有一个 SolidWorks 实例（已知事实 24）；
# ★ 一律这样起：`python tools/sw_guard.py --timeout 600 -- python tools/probe_fr008_expl
# ode_macro.py`
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.stdout.reconfigure(encoding="utf-8")

from scripts import sw_connect                                        # noqa: E402
from scripts import sw_assembly_doc as A                              # noqa: E402
from scripts import sw_macro as M                                     # noqa: E402

SRC_ASM = Path(Path(__file__).resolve().parents[1] / "AI Solidworks" / "模型" / "换刀主轴装配_BT30_ATC_Assembly.SLDASM")
COPY = ROOT / "output" / "fr008-assembly-copy.SLDASM"
SWB = ROOT / "subskills" / "solidworks-fillet-chamfer-cnc" / "scripts" / "native" / \
      "NativeHoldLineMacro.swb"
OUT = ROOT / "output" / "fr008-explode-macro-evidence.json"


def _flush():
    sys.stdout.flush()


def _active_config(doc) -> str:
    """★ 取活动配置名（爆炸视图的读数 API 要它）。"""
    for path in (("ConfigurationManager", "ActiveConfiguration", "Name"),):
        try:
            obj = doc
            for attr in path:
                obj = sw_connect.get_com_member(obj, attr)
            return str(obj or "")
        except Exception as exc:                                     # noqa: BLE001
            print("  ⚠ 取活动配置名失败:", type(exc).__name__, str(exc)[:80])
    return ""


def main() -> int:
    ev: dict = {"captured_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "_": "规格 204 / SC-005 —— FR-008 两半的真机证据", "steps": {}}
    sw = doc = None
    try:
        sw, doc, _meta = sw_connect.connect_solidworks(wait_seconds=30, return_metadata=True)
        print("★ SW:", _meta.get("revision") or _meta)

        #: ── ① 复制用户原件（★ 只动副本）──────────────────────────────
        COPY.parent.mkdir(parents=True, exist_ok=True)
        if not COPY.is_file():
            shutil.copy2(SRC_ASM, COPY)
        ev["steps"]["copy"] = {"src": str(SRC_ASM), "copy": str(COPY),
                              "copy_bytes": COPY.stat().st_size,
                              "★": "★ 用户原件**只读**：本探针只打开副本"}
        print("  [1] 副本:", COPY.name, COPY.stat().st_size, "bytes")

        #: ── ② 打开副本（装配）────────────────────────────────────────
        #: ★★★ **用仓里既有的 `sw_connect.open_document`，不手写 `OpenDoc6`** ——
        #:   ★ 我第一版手写 `OpenDoc6(path, 1, 0, "", 0, 0)` ⇒
        #: `com_error: (-2147352571, '类型不匹配。', None, 5)` ⇒ ★ **末两个是 `out Int32
        #: `**
        #: （`ISldWorks.OpenDoc6(..., Int32&, Int32&)` 6 参 —— `sw_com_traps.py:113` 早
        #: 就登记过）
        #:   ⇒ ★ 而 `sw_connect.open_document` 已经把那对 out 参、silent/read_only 选项、
        #:     **参考件加载的弹窗坑**（它注释里写着"SolidWorks 只能问用户要不要加载参考件"）
        #:     全部处理过了 ⇒ ★ 重写一遍就是把那些坑再踩一次（铁律 1：只缝合不发明）✓
        _doc = sw_connect.open_document(sw, COPY, silent=True)
        doc = _doc if _doc is not None else sw_connect.get_com_member(sw, "ActiveDoc")
        title = ""
        try:
            title = str(sw_connect.get_com_member(doc, "GetTitle") or "")
        except Exception:                                            # noqa: BLE001
            pass
        ev["steps"]["open"] = {"model_is_none": _doc is None, "title": title,
                              "gettype": (sw_connect.get_com_member(doc, "GetType")
                                          if doc is not None else None)}
        print("  [2] 打开副本:", title, "· GetType=", ev["steps"]["open"]["gettype"])
        if doc is None:
            ev["verdict"] = "装配副本打不开 ⇒ 本轮只做宏那半"
        else:
            cfg = _active_config(doc)
            ev["steps"]["config"] = cfg
            print("  [2b] 活动配置:", repr(cfg))

            #: ── ③ 正例：建爆炸视图 + **回读数** ──────────────────────
            before = A.get_exploded_view_count(doc, cfg)
            ok = A.create_exploded_view(doc)
            after = A.get_exploded_view_count(doc, cfg)
            names = A.get_exploded_view_names(doc, cfg)
            ev["steps"]["explode_create"] = {
                "count_before": before, "return_value": ok, "count_after": after,
                "names": names,
                "★": "★ 判据：**回读计数 +1**（不是那个 bool）」"}
            print("  [3] 建爆炸视图: 回 %s · 计数 %d → %d · 名字 %r"
                  % (ok, before, after, names))
            _flush()

            #: 显示切换（成对，无害）
            try:
                A.view_explode_assembly(doc)
                A.view_collapse_assembly(doc)
                ev["steps"]["view_toggle"] = {"ok": True}
                print("  [3b] 展开/收拢显示：两次调用都没抛")
            except Exception as exc:                                 # noqa: BLE001
                ev["steps"]["view_toggle"] = {"ok": False,
                                              "error": "%s: %s" % (type(exc).__name__,
                                                                   str(exc)[:120])}
                print("  [3b] 显示切换失败:", ev["steps"]["view_toggle"]["error"])

            #: 按名字显示（用回读到的名字，形成闭环）
            if names:
                try:
                    ok2 = A.show_exploded(doc, True, names[0])
                    A.show_exploded(doc, False, names[0])
                    ev["steps"]["show_exploded"] = {"ok": bool(ok2), "name": names[0]}
                    print("  [3c] 按名显示 %r ⇒ %s（随后已收起）" % (names[0], ok2))
                except Exception as exc:                             # noqa: BLE001
                    ev["steps"]["show_exploded"] = {"ok": False,
                                                    "error": "%s: %s" % (type(exc).__name__,
                                                                         str(exc)[:120])}
                    print("  [3c] 按名显示失败:", ev["steps"]["show_exploded"]["error"])

            #: ── ④ 反例：对**零件**文档调爆炸视图 ──────────────────────
            #: ★★★ 第一版这里踩了坑（**我自己的探针 bug，不是能力的问题**）：
            #:   我 `NewDocument(...)` 之后取 **`ActiveDoc`**，而那**仍是装配副本**
            #:   （★ 读数 `回 True · 计数 2` 与"装配上又建了一个"完全吻合：1 → 2）
            #: ⇒ ★★ 判据写"零件上也能建"会是**一条假事实** ⇒ 必须用 `NewDocument` 的**返
            #: 回值** ✓
            try:
                part = sw_connect.get_com_member(sw, "NewDocument", "", 0, 0.0, 0.0)
                ptype = (sw_connect.get_com_member(part, "GetType")
                         if part is not None else None)
                ev["steps"]["explode_negative_on_part"] = {
                    "newdoc_is_none": part is None, "newdoc_gettype": ptype,
                    "★": "★ 反例的**前置**：必须确认手上这个真的是**零件**（GetType=1）"}
                print("  [4] 反例前置: NewDocument 回 %s · GetType=%s"
                      % ("None" if part is None else "对象", ptype))
                if part is not None and ptype == 1:
                    try:
                        r = A.create_exploded_view(part)
                        cnt = A.get_exploded_view_count(part, "")
                        ev["steps"]["explode_negative_on_part"].update(
                            {"return_value": bool(r), "count": cnt})
                        print("  [4] 反例读数: 回 %s · 计数 %s" % (r, cnt))
                    except Exception as exc:                         # noqa: BLE001
                        ev["steps"]["explode_negative_on_part"]["raised"] = (
                            "%s: %s" % (type(exc).__name__, str(exc)[:160]))
                        print("  [4] 反例: 抛出/拒绝 ⇒",
                              ev["steps"]["explode_negative_on_part"]["raised"][:110])
                    sw_connect.get_com_member(sw, "CloseDoc", str(
                        sw_connect.get_com_member(part, "GetTitle") or ""))
                else:
                    ev["steps"]["explode_negative_on_part"]["★_note"] = (
                        "★ 拿到的不是零件（GetType≠1）⇒ **本反例未做**，如实记"
                        "（★ 宁可记'没做'，也不把装配上的读数冒充零件读数）")
                    print("  [4] ★ 反例未做：拿到的不是零件 ⇒ 如实记")
            except Exception as exc:                                 # noqa: BLE001
                ev["steps"]["explode_negative_on_part"] = {
                    "raised": "%s: %s" % (type(exc).__name__, str(exc)[:160])}
                print("  [4] 反例: 抛出 ⇒", ev["steps"]["explode_negative_on_part"]["raised"][:110])
            _flush()

        #: ── ⑤ 宏：反例（不存在的路径）────────────────────────────────
        neg = M.run_macro(sw, str(ROOT / "output" / "_no_such_macro_.swp"), "M", "main")
        ev["steps"]["macro_negative"] = neg
        print("  [5] 宏反例: ok=%s return=%s error=%s(%s) file_exists=%s"
              % (neg["ok"], neg["return_value"], neg["error_code"], neg["error_name"],
                 neg["file_exists"]))
        _flush()

        #: ── ⑥ 宏：正例（我们自己的 .swb，明文 VB.NET、含 `Sub main`）──
        pos = M.run_macro(sw, str(SWB), "", "main")
        ev["steps"]["macro_positive_swb"] = pos
        print("  [6] 宏正例(.swb): ok=%s return=%s error=%s(%s)"
              % (pos["ok"], pos["return_value"], pos["error_code"], pos["error_name"]))
        #: ★ 同一文件换个过程名 ⇒ 应当报 InvalidProcname(6)
        bad_proc = M.run_macro(sw, str(SWB), "", "_definitely_not_a_proc_")
        ev["steps"]["macro_bad_procedure"] = bad_proc
        print("  [6b] 宏换错过程名: ok=%s error=%s(%s)"
              % (bad_proc["ok"], bad_proc["error_code"], bad_proc["error_name"]))
        _flush()

        ev["verdict"] = "见各步读数（★ 判据：爆炸视图看计数增量 · 宏看 bool + error_name）"
    except Exception as exc:                                         # noqa: BLE001
        ev["★_异常"] = "%s: %s" % (type(exc).__name__, str(exc)[:400])
        print("★ 异常:", ev["★_异常"])
    finally:
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1), encoding="utf-8")
        print("★ wrote", OUT)
        if doc is not None:
            try:
                sw_connect.get_com_member(sw, "CloseDoc", str(sw_connect.get_com_member(
                    doc, "GetTitle") or ""))
                print("★ 已关副本（★ **不保存** ⇒ 用户原件与副本都保持原样）")
            except Exception:                                        # noqa: BLE001
                pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
