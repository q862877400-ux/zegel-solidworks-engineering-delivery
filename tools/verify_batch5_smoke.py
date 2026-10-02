r"""@brief 真机冒烟：`tool_specs_batch5` 的 5 个新工具（轮 91，Spec Kit `012`）。

## 为什么
`012` 的验收只做了**静态**核对（声明 vs 签名一致）。**那不能证明工具真能用。**
本脚本**真连 SolidWorks**，把 5 个函数各跑一次，落证据。

## 安全（铁律 2）
* 先 `CommandInProgress = True`（抑制模态弹窗挂起）；
* 每个调用独立计时，超时不重试；
* 收尾：`CommandInProgress = False`、关掉**我自己开的**文档、释放引用。

# ── 来源 ──
# 仓库:   本项目自身（真机验收）
# 文件:   tools/verify_batch5_smoke.py
# 定位:   给 `tool_specs_batch5.py` 的 5 条声明取真机证据。
# 官方依据: 不适用（调的是本仓库自己的包装函数）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if p not in sys.path:
        sys.path.insert(0, p)
sys.stdout.reconfigure(encoding="utf-8")

OUT = Path(r"D:\AI\SW\output\batch5-smoke-evidence.json")


def main() -> int:
    ev: dict = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "checks": {}}
    checks: list = []

    def chk(name, ok, detail):
        checks.append(bool(ok))
        ev["checks"][name] = {"ok": bool(ok), "detail": str(detail)[:400]}
        print("   %s %-40s %s" % ("✓" if ok else "**✗**", name, str(detail)[:88]))

    import sw_connect
    sw = None
    created = None
    try:
        # ⚠ `connect_solidworks()` 返回 **(sw, 元数据)** 元组，不是单个对象
        #   （第一版直接当对象用 ⇒ `'tuple' object has no attribute 'ActiveDoc'`）。
        connected = sw_connect.connect_solidworks(wait_seconds=10)
        sw = connected[0] if isinstance(connected, tuple) else connected
        chk("连接 SolidWorks", sw is not None, "ok")
        try:
            sw.CommandInProgress = True
        except Exception as exc:      # noqa: BLE001
            print("   ⚠ CommandInProgress 设置失败（继续）：%s" % exc)

        doc = sw.ActiveDoc
        if doc is None:
            created = sw_connect.new_document(sw, "part")
            doc = created
            chk("新建测试零件（原本无文档）", doc is not None, "已建")
        else:
            # ⚠ `GetTitle` 在 pywin32 迟到绑定下**有时是属性、有时是方法**
            #   ⇒ 直接 `doc.GetTitle()` 会报 `'str' object is not callable`。
            #   用仓库自带的 `get_com_member` 兼容两种形态（**不自己造**）。
            _title = sw_connect.get_com_member(doc, "GetTitle")
            chk("复用已有文档", True, str(_title))
        if doc is None:
            print("   ✗ 没有可用文档，冒烟无法继续")
            return 1

        from scripts import sw_render_material, sw_review, sw_selection_spec

        def timed(label, fn):
            t0 = time.time()
            try:
                r = fn()
                return True, r, (time.time() - t0)
            except Exception as exc:      # noqa: BLE001
                return False, "%s: %s" % (type(exc).__name__, str(exc)[:150]), (time.time() - t0)

        print()
        print("=== 5 个新工具 ===")
        ok, r, dt = timed("list_render_materials", lambda: sw_render_material.list_render_materials(doc))
        chk("list_render_materials", ok, "%s · %d 个材质 · %.2fs"
            % ("ok" if ok else r, len(r) if ok and hasattr(r, "__len__") else -1, dt))

        ok, r, dt = timed("collect_appearance_evidence", lambda: sw_render_material.collect_appearance_evidence(doc))
        chk("collect_appearance_evidence", ok and isinstance(r, dict),
            ("dict %d 键" % len(r)) if ok and isinstance(r, dict) else r)

        ok, r, dt = timed("current_selection", lambda: sw_selection_spec.current_selection(doc))
        chk("current_selection", ok, "%d 项 · %.2fs" % (len(r) if ok and hasattr(r, "__len__") else -1, dt))

        ok, r, dt = timed("clear_selection", lambda: sw_selection_spec.clear_selection(doc))
        chk("clear_selection", ok, "ok · %.2fs" % dt)

        ok, r, dt = timed("set_standard_view", lambda: sw_review.set_standard_view(doc, "isometric"))
        chk("set_standard_view", ok, "ok · %.2fs" % dt)

        # ── ★ 强证据（2026-10-01 轮 92 补）──────────────────────────────
        # ⚠ 上面那两条**证据偏弱**：`list_render_materials` 在原文档上返回 **0 个材质**
        #   ⇒ 只证明"不报错"，**没验到"有材质时"**；`collect_appearance_evidence` 只回 3 个键
        #   ⇒ **没核键的含义对不对**。
        # ⇒ 本节**造一个带外观的新件**，再验一次：数量必须 > 0，且参数**必须不是恒定 0**。
        print()
        print("=== 强证据：造带外观的件，再验 ===")
        from scripts import sw_appearance

        fresh = sw_connect.new_document(sw, "part")
        if fresh is None:
            chk("新建带外观的件", False, "new_document 返回 None")
        else:
            created = fresh          # 记下来，finally 里关掉
            ok_a, r_a, _ = timed("set_document_appearance",
                                 lambda: sw_appearance.set_document_appearance(fresh, "#3366CC"))
            chk("set_document_appearance 生效", ok_a, "ok" if ok_a else r_a)

            mats = sw_render_material.list_render_materials(fresh)
            chk("★ list_render_materials **有材质时**返回 > 0",
                ok_a and len(mats) > 0, "材质数 = %d（原文档是 0）" % len(mats))

            evi = sw_render_material.collect_appearance_evidence(fresh)
            # ⚠ 键名是 **`appearances`**，不是 `rows`（第一版猜错了 ⇒ 断言取到 None）。
            #   实测结构：{"appearance_count": int, "appearances": [{ambient,diffuse,…}], "has_appearance": bool}
            rows = evi.get("appearances") if isinstance(evi, dict) else None
            chk("★ `appearance_count` 与实际材质数一致",
                isinstance(evi, dict) and evi.get("appearance_count") == len(mats),
                "appearance_count=%r · 实际=%d"
                % (evi.get("appearance_count") if isinstance(evi, dict) else None, len(mats)))
            diff = rows[0].get("diffuse") if isinstance(rows, list) and rows else None
            chk("★ `appearances[0].diffuse` **不是恒定 0**（证明真读到了材质参数）",
                diff is not None and diff > 0.0, "diffuse=%r" % diff)
            chk("★ `has_appearance` 与材质数一致",
                isinstance(evi, dict) and evi.get("has_appearance") == (len(mats) > 0),
                "has_appearance=%r" % (evi.get("has_appearance") if isinstance(evi, dict) else None))
            ev["strong_evidence"] = {
                "materials": len(mats), "diffuse": diff,
                "evidence_keys": sorted(evi.keys()) if isinstance(evi, dict) else None,
            }

    except Exception as exc:      # noqa: BLE001
        chk("整体冒烟", False, "%s: %s" % (type(exc).__name__, str(exc)[:200]))
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:      # noqa: BLE001
            pass
        try:
            if created is not None and sw is not None:
                # ⚠ `created.Close(False)` 在迟到绑定下报「**无效的参数数目**」（轮 92 实测）
                #   ⇒ 改用 `ISldWorks.CloseDoc(标题)`，**只在按标题能找到时**关。
                # ⚠ 只关**我自己刚建的**那个（`created`），绝不按名单批量关。
                _t = str(sw_connect.safe_get_com_member(created, "GetTitle") or "")
                if _t:
                    sw.CloseDoc(_t)
                    print("   （已关闭本轮新建的测试零件 %s，未保存）" % _t)
        except Exception as exc:      # noqa: BLE001
            print("   ⚠ 收尾关文档失败（**不影响判定**，但请人工确认没有残留）：%s" % str(exc)[:100])

    ev["passed"] = sum(1 for c in checks if c)
    ev["total"] = len(checks)
    ev["verdict"] = "pass" if checks and all(checks) else "fail"
    ev["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print()
    print("  ── %d/%d · verdict: %s ──" % (ev["passed"], ev["total"], ev["verdict"]))
    print("  证据: %s" % OUT)
    return 0 if ev["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
