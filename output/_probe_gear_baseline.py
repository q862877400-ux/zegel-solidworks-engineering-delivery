"""最小真机探针 v4（定稿）：连通 / 版本 / 建零件 / 选基准面 / 画矩形 / 读完全定义 / 不保存关闭。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   output/_probe_gear_baseline.py
# 定位:   业主指令第 3 步「实际测试一下」。验证建模基线，不建齿轮（齿轮已判为方法、无工具）。
# 官方依据: 事实 33（Callout 传空 VARIANT）；事实 9（基准面候选名）；
#         scripts/sw_part.py L1091-L1110（GetConstrainedStatus 的正确读法：只传成员名再按需调用）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
import json, sys, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, "scripts")

out = {"ok": False, "steps": []}
t0 = time.time()
doc = None
title = None
try:
    import sw_connect as sc
    from sw_connect import get_com_member
    sw = sc.connect_solidworks(return_metadata=True)[0]
    out["steps"].append({"step": "connect", "ok": sw is not None})
    out["version"] = sc.get_sw_version(sw)

    doc = sc.new_document(sw, "part", sc.find_template(sw, "part"))
    out["steps"].append({"step": "new_document", "ok": doc is not None})
    title = get_com_member(doc, "GetTitle")

    callout = sc.create_empty_dispatch_variant()
    ok_plane, used = False, None
    for nm in ("Front Plane", "前视基准面", "Front"):
        if doc.Extension.SelectByID2(nm, "PLANE", 0, 0, 0, False, 0, callout, 0):
            ok_plane, used = True, nm
            break
    out["plane_used"] = used
    out["steps"].append({"step": "select_plane", "ok": ok_plane, "used": used})

    if ok_plane:
        doc.SketchManager.InsertSketch(True)
        doc.SketchManager.CreateLine(0, 0, 0, sc.mm(50), 0, 0)
        doc.SketchManager.CreateLine(sc.mm(50), 0, 0, sc.mm(50), sc.mm(30), 0)
        doc.SketchManager.CreateLine(sc.mm(50), sc.mm(30), 0, 0, sc.mm(30), 0)
        doc.SketchManager.CreateLine(0, sc.mm(30), 0, 0, 0, 0)
        sk = doc.SketchManager.ActiveSketch
        # ★ 按 sw_part.py L1097-L1110 的正确读法
        st = None
        for member in ("GetConstrainedStatus", "GetConstrainedStatus2"):
            try:
                v = get_com_member(sk, member)
            except Exception:
                continue
            try:
                v = v() if callable(v) else v
            except Exception:
                continue
            if isinstance(v, (int, float)):
                st = int(v)
                break
        out["sketch_constrained_status"] = st
        out["status_meaning"] = {0: "未知/无解", 1: "过定义", 2: "欠定义", 3: "完全定义"}.get(st, "未识别")
        doc.SketchManager.InsertSketch(True)
        out["steps"].append({"step": "sketch_rect", "ok": True, "status": st, "meaning": out["status_meaning"]})
except Exception as e:
    out["error"] = f"{type(e).__name__}: {e}"
finally:
    try:
        if title:
            sw.CloseDoc(title)
            out["steps"].append({"step": "close_doc_no_save", "ok": True})
    except Exception as e:
        out["steps"].append({"step": "close_doc_no_save", "ok": False, "err": str(e)[:70]})
    out["ok"] = "error" not in out
    out["elapsed_s"] = round(time.time() - t0, 2)
    print(json.dumps(out, ensure_ascii=False, indent=1))
