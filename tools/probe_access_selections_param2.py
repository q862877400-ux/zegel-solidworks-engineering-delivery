"""★ 真机：`AccessSelections` 的**第 2 参**到底要什么 —— `None` 还是空 Dispatch？"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_access_selections_param2.py
# 定位:   ★ 2026-10-03（轮 598）★ 执行**事实 473 留的第 ① 步**（★ 那是个**可测的问题**）。
#
#   ★★★ **为什么这一测是决定性的**（★ 事实 472 / 473）：
#     · `docs/toolbar-gaps-backend-limits.md` §2.2 说「本仓早已按新架构实现」；
#     · ★ 而那个架构的机理（`scripts/sw_pattern.py::_SelectionAccess`）是
#       ★ **`data.AccessSelections(model, **None**)`** + `ReleaseSelectionAccess()`；
#     · ★ 而**事实 47** 记的是 `ISketchedBendFeatureData.AccessSelections(model, **空 Dispatch**)`
#       ⇒ ★ **报 `类型不匹配`**。
#     ⇒ ★★ **故两者只差第 2 参** —— ★ **而它直接决定"指针族能不能留条活路"** ⚠
#
#   ★ **怎么取到真的 FeatureData**：★ `IFeatureManager.CreateDefinition(swFmFillPattern = **105**)`
#     （★ 值取自**本机反射 dump**，铁律 4；★ 那几个阵列的 FeatureData 都带 `AccessSelections`）。
#
#   ★ 判据：★ **回 `True` 且不报错** ⇒ 通过；★ 报错 ⇒ 记下**错误码与位置**（★ 那才是证据）。
#   ⚠ 全程走 `tools/sw_guard.py`。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

import pythoncom                                                     # noqa: E402
import win32com.client                                               # noqa: E402
from scripts import sw_connect as C                                   # noqa: E402

SW_FM_FILL_PATTERN = 105        #: ★ 反射 dump：`swFmFillPattern = 105`
SW_FM_TABLE_PATTERN = 106       #: ★ 反射 dump：`swFmTablePattern = 106`


def _forms():
    """★ 第 2 参的**四种形态**（★ 事实 47 试过前两种，★ 本轮加上后两种）。"""
    return [
        ("\u2605 **`None`**\uff08\u2605 `sw_pattern.py` \u7528\u7684\uff09", None),
        ("\u2605 **\u7a7a Dispatch**\uff08\u2605 \u4e8b\u5b9e 47 \u62a5\u9519\u7684\u90a3\u4e2a\uff09",
         win32com.client.VARIANT(pythoncom.VT_DISPATCH, None)),
        ("\u2605 \u7a7a\u53d8\u4f53", win32com.client.VARIANT(pythoncom.VT_VARIANT, None)),
        ("\u2605 byref \u7a7a Dispatch", win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_DISPATCH, None)),
    ]


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
          "_": "`AccessSelections` \u7684**\u7b2c 2 \u53c2**\u5230\u5e95\u8981\u4ec0\u4e48"
               "\uff08\u2605 \u5b83\u51b3\u5b9a\u6307\u9488\u65cf\u80fd\u4e0d\u80fd\u7559\u6761\u6d3b\u8def\uff09",
          "official": "`AccessSelections(TopDoc, IgnoreTopDoc)` \u2014\u2014 \u7b2c 2 \u53c2\u662f **`IgnoreTopDoc`**",
          "cases": []}
    for const, cname in ((SW_FM_FILL_PATTERN, "swFmFillPattern"),
                         (SW_FM_TABLE_PATTERN, "swFmTablePattern")):
        doc = None
        try:
            doc = C.new_document(sw, "part")
            fm = C.get_com_member(doc, "FeatureManager")
            data = None
            row = {"const": cname, "value": const, "forms": []}
            try:
                data = C.get_com_member(fm, "CreateDefinition", int(const))
                row["data"] = type(data).__name__ if data is not None else "None"
            except Exception as exc:                                      # noqa: BLE001
                row["create_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:120])
            if data is not None:
                for tag, arg2 in _forms():
                    r = {"form": tag}
                    try:
                        ok = C.get_com_member(data, "AccessSelections", doc, arg2)
                        r["returned"] = str(ok)
                        r["ok"] = bool(ok)
                    except Exception as exc:                              # noqa: BLE001
                        r["err"] = "%s" % str(exc)[:130]
                        r["ok"] = False
                    #: \u2605 \u82e5\u6210\u529f\uff0c**\u9a6c\u4e0a\u91ca\u653e**\uff08\u2605 \u4e0d\u8ba9\u4e8b\u52a1\u60ac\u7740\uff09
                    if r.get("ok"):
                        try:
                            C.get_com_member(data, "ReleaseSelectionAccess")
                            r["released"] = True
                        except Exception as exc:                          # noqa: BLE001
                            r["released"] = "%s" % str(exc)[:60]
                    row["forms"].append(r)
            ev["cases"].append(row)
        except Exception as exc:                                          # noqa: BLE001
            ev["cases"].append({"const": cname, "err": "%s: %s" % (type(exc).__name__, str(exc)[:140])})
        finally:
            if doc is not None:
                try:
                    t = str(C.get_com_member(doc, "GetTitle") or "")
                    if t:
                        C.get_com_member(sw, "CloseDoc", t)
                except Exception:                                         # noqa: BLE001
                    pass
    #: \u2605 \u5224\u8bfe\uff1a\u770b `None` \u90a3\u4e00\u683c
    none_ok = any(f.get("ok") for c in ev["cases"] for f in (c.get("forms") or [])
                  if "None" in str(f.get("form")))
    disp_ok = any(f.get("ok") for c in ev["cases"] for f in (c.get("forms") or [])
                  if "Dispatch" in str(f.get("form")) and "byref" not in str(f.get("form")))
    ev["none_works"] = none_ok
    ev["empty_dispatch_works"] = disp_ok
    ev["verdict"] = ("none_ok=%s_empty_dispatch_ok=%s" % (none_ok, disp_ok))
    p = R / "output" / "access-selections-param2-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  \u5224\u522b\uff1a**%s**" % ev["verdict"])
    for c in ev["cases"]:
        print("  ===== %s (%s) =====" % (c.get("const"), c.get("value")))
        print("     CreateDefinition \u2192 %s" % c.get("data"))
        for f in (c.get("forms") or []):
            print("     %-40s ok=%-6s \u56de=%s%s" % (
                f.get("form"), f.get("ok"), f.get("returned"), ("  err=" + str(f.get("err"))[:70]) if f.get("err") else ""))
        if c.get("create_err"):
            print("     create_err=%s" % str(c["create_err"])[:120])
        if c.get("err"):
            print("     err=%s" % str(c["err"])[:120])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
