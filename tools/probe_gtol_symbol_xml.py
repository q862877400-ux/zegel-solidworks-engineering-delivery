r"""@brief 探针：绕开不通的 `AddIndicator`，试 **`IGtolFrame.SetSymbolXml`（XML 路径）**。

## 为什么值得试（轮 171）
```
轮 165：帧路径通了（ConvertFormat → AddFrame → GetFrame **拿到对象**）
轮 166：IGtolFrame.AddIndicator **20 组全 False**（border×tol 穷尽）⇒ 判「这条后端到不了」
★ 但官方还有**另一条**：IGtolFrame.SetSymbolXml(String) ——
  其 Remarks 只要求「Gtol 是 **2022 格式创建或转换过**」，而我们**确实 ConvertFormat 过了**。
```

## 官方依据（两源）
```
① C:/swapi/types/IGtolFrame/SetSymbolXml.md：
   "Sets the XML string for this Gtol frame." · Remark: "valid only for Gtols created in or
    converted to the SOLIDWORKS 2022 format"
② 同目录 GetSymbolXml.md ⇒ **能把当前帧的 XML 读出来** ⇒ ★ **不必猜 schema**（先读再改）
③ SetSymbolXml.md 的 See Also 指向 `ISldWorks::GetGtolFrameXMLSchema Method ()` ⇒ 官方有 schema
```

## 判据（能被空操作证伪）
```
① `GetSymbolXml()` 返回**非空字符串**（拿到"合法 XML 长什么样"）
② `SetSymbolXml(<原样读出的 XML>)` 返回 **True**（**空操作也应当成功**）
③ ★★ 改一处（把某个公差符号 / 数值换掉）后 `SetSymbolXml` 仍 **True**，且
   **再 `GetSymbolXml()` 读回能看到改动** ⇒ ★★ 这才是「**XML 路径真的可用**」的定量证据
```

## ⚠ 安全
只在新零件上；`CommandInProgress` 复位；收尾**轮询点掉**（兜底）+ 关件不保存。

# ── 来源 ──
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_gtol_symbol_xml.py
# 定位:   给 Spec Kit `091` 判定 `SetSymbolXml` 能否补上 `AddIndicator` 那半。
# 官方依据: `C:/swapi/types/IGtolFrame/{SetSymbolXml,GetSymbolXml}.md`；出厂反射
#          `Boolean SetSymbolXml(String)` / `String GetSymbolXml()`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if p not in sys.path:
        sys.path.insert(0, p)
sys.stdout.reconfigure(encoding="utf-8")

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "gtol-symbol-xml.json")


def main() -> int:
    ev: dict = {}
    sw = None
    doc = None
    try:
        import sw_connect
        from scripts import sw_gtol
        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:      # noqa: BLE001
            pass
        doc = sw_connect.new_document(sw, "part")

        gtol = sw_gtol.insert_gtol(doc)
        ev["insert_gtol"] = gtol is not None
        print("  ① `insert_gtol()` ⇒ %s" % ("有对象" if gtol is not None else "**None**"))
        if gtol is None:
            return 1

        #: 轮 165 的顺序：先转换，再加帧
        ev["can_convert"] = bool(sw_connect.safe_get_com_member(gtol, "CanConvertFormat"))
        try:
            sw_connect.safe_get_com_member(gtol, "ConvertFormat")
        except Exception as exc:      # noqa: BLE001
            print("     ConvertFormat 抛错: %s" % str(exc)[:60])
        ev["add_frame"] = bool(sw_connect.safe_get_com_member(gtol, "AddFrame"))
        ev["frame_count"] = int(sw_connect.safe_get_com_member(gtol, "GetFrameCount") or 0)
        print("  ② 转换=%s · AddFrame=%s · GetFrameCount=%s"
              % (ev["can_convert"], ev["add_frame"], ev["frame_count"]))

        frame = None
        for idx in (1, 2, 0):
            f = sw_connect.safe_get_com_member(gtol, "GetFrame", idx)
            if f is not None and not isinstance(f, str):
                frame = f
                ev["frame_index"] = idx
                break
        ev["frame"] = frame is not None
        print("  ③ 取到帧: %s（index=%s）" % (ev["frame"], ev.get("frame_index")))
        if frame is None:
            print("     ⚠ 没帧 ⇒ 后面的 XML 路径无从谈起")
            return 1

        #: ④ ★ 读出当前 XML —— **不必猜 schema**
        xml = sw_connect.safe_get_com_member(frame, "GetSymbolXml")
        ev["xml_len"] = len(xml) if isinstance(xml, str) else -1
        print("  ④ `GetSymbolXml()` ⇒ 长度 **%s**" % ev["xml_len"])
        if isinstance(xml, str) and xml.strip():
            print("     ── XML 前 400 字 ──")
            for i in range(0, min(400, len(xml)), 100):
                print("       %s" % xml[i:i + 100].replace("\n", " "))
            ev["xml_head"] = xml[:600]
        else:
            print("     ⚠ XML 是空的 ⇒ 这条路也不通")

        #: ⑤ 原样写回（**空操作也应当成功**）
        if isinstance(xml, str) and xml.strip():
            try:
                r = sw_connect.safe_get_com_member(frame, "SetSymbolXml", xml)
                ev["set_same"] = r
                print("  ⑤ `SetSymbolXml(原样)` ⇒ **%r**" % r)
            except Exception as exc:      # noqa: BLE001
                ev["set_same"] = "EXC:%s" % str(exc)[:60]
                print("  ⑤ `SetSymbolXml(原样)` 抛错: %s" % str(exc)[:80])

            #: ⑥ ★★ 改一处再写回 —— **定量证据**：读回能看到改动
            import re
            m = re.search(r">([^<]{1,20})<", xml)
            if m:
                old_txt = m.group(1)
                changed = xml[:m.start(1)] + ("0.05" if old_txt.strip() else "X") + xml[m.end(1):]
                try:
                    r2 = sw_connect.safe_get_com_member(frame, "SetSymbolXml", changed)
                    ev["set_changed"] = r2
                    back = sw_connect.safe_get_com_member(frame, "GetSymbolXml")
                    ev["readback_changed"] = (isinstance(back, str) and back != xml)
                    print("  ⑥ `SetSymbolXml(改动 %r→0.05)` ⇒ %r · 读回**变了**: %s"
                          % (old_txt[:14], r2, ev["readback_changed"]))
                except Exception as exc:      # noqa: BLE001
                    ev["set_changed"] = "EXC:%s" % str(exc)[:60]
                    print("  ⑥ 改动写回抛错: %s" % str(exc)[:80])

        #: ⑦ 顺带看官方 schema 入口在不在
        for cand in ("GetGtolFrameXMLSchema", "GetGtolFrameXmlSchema"):
            try:
                s = sw_connect.safe_get_com_member(sw, cand)
                ev["schema_" + cand] = "有" if s is not None else None
                print("  ⑦ `ISldWorks.%s` ⇒ %s" % (cand, "有" if s is not None else "None"))
            except Exception as exc:      # noqa: BLE001
                print("  ⑦ `ISldWorks.%s` ⇒ %s" % (cand, str(exc)[:50]))
    except Exception as exc:      # noqa: BLE001
        ev["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
        print("  ⚠ 探针出错: %s" % ev["error"])
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:      # noqa: BLE001
            pass
        try:
            if doc is not None and sw is not None:
                t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
        except Exception:      # noqa: BLE001
            pass

    import sw_connect as _sc
    found, dismissed, scanned = _sc.settle_residual_dialogs(settle_seconds=1.0)
    print("  收尾：发现 %d · 点掉 %d · 扫了 %d 个窗口" % (found, dismissed, scanned))
    ev["cleanup"] = {"found": found, "dismissed": dismissed, "scanned": scanned}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  证据: %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
