r"""@brief 探针：拿官方 `ISldWorks.GetGtolFrameXMLSchema()`，看它要求什么结构。

## 为什么（轮 171）
```
`IGtolFrame.GetSymbolXml()` 在**新建+转换过**的 Gtol 上返回**空串** ⇒ 「先读再改」这条路断了
★ 但官方还有 `ISldWorks.GetGtolFrameXMLSchema()`（`SetSymbolXml.md` 的 See Also 指向它）——
  实测**可调到** ⇒ ★★ **从官方 schema 出发**，而不是猜 XML 结构。
```

## 判据
```
① schema **非空** ⇒ 拿到官方结构说明（这是"缝合"，不是"发明"）
② schema 里能读出发音：**根元素名 / 必需子元素 / 允许的值** ⇒ 据此构造最小 XML
③ `SetSymbolXml(<按 schema 构造的 XML>)` 的返回值（**如实报，不美化**）
```

## ⚠ 安全
只在新零件上；`CommandInProgress` 复位；收尾**轮询点掉**；关件不保存。

# ── 来源 ──
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_gtol_xml_schema.py
# 定位:   给 Spec Kit `091` 判定 XML 路径有没有可行起点。
# 官方依据: `C:/swapi/types/IGtolFrame/SetSymbolXml.md` 的 See Also：
#          `ISldWorks::GetGtolFrameXMLSchema Method ()`；出厂反射
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

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "gtol-xml-schema.json")
SAVE = Path(Path(__file__).resolve().parents[1] / "output" / "gtol-frame-xml-schema.txt")


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

        #: ① 拿 schema（官方产物）
        schema = None
        for cand in ("GetGtolFrameXMLSchema", "GetGtolFrameXmlSchema"):
            try:
                s = sw_connect.safe_get_com_member(sw, cand)
                if isinstance(s, str) and s.strip():
                    schema = s
                    ev["schema_from"] = cand
                    break
            except Exception as exc:      # noqa: BLE001
                print("  %s 抛错: %s" % (cand, str(exc)[:60]))
        ev["schema_len"] = len(schema) if schema else 0
        print("  ① schema 长度 = **%s**（来源 %s）" % (ev["schema_len"], ev.get("schema_from")))
        if schema:
            SAVE.parent.mkdir(parents=True, exist_ok=True)
            SAVE.write_text(schema, encoding="utf-8")
            print("     已存: %s" % SAVE)
            #: ★ 从 schema 里抽结构要素（不猜）
            import re
            els = sorted(set(re.findall(r"<(?:xs:)?element[^>]*name=\"([^\"]+)\"", schema)))
            attrs = sorted(set(re.findall(r"<(?:xs:)?attribute[^>]*name=\"([^\"]+)\"", schema)))
            ev["schema_elements"] = els
            ev["schema_attributes"] = attrs
            print("     元素 (%d): %s" % (len(els), els[:14]))
            print("     属性 (%d): %s" % (len(attrs), attrs[:14]))

        #: ③ 按 schema 构造最小 XML 并试 SetSymbolXml
        doc = sw_connect.new_document(sw, "part")
        gtol = sw_gtol.insert_gtol(doc)
        if gtol is not None:
            sw_connect.safe_get_com_member(gtol, "ConvertFormat")
            sw_connect.safe_get_com_member(gtol, "AddFrame")
            frame = None
            for idx in (1, 2, 0):
                f = sw_connect.safe_get_com_member(gtol, "GetFrame", idx)
                if f is not None and not isinstance(f, str):
                    frame = f
                    break
            ev["frame"] = frame is not None
            print("  ③ 帧 = %s" % ev["frame"])
            if frame is not None and ev.get("schema_elements"):
                root = ev["schema_elements"][0]
                #: 最小试探：只用**根元素**（schema 里的第一个 element 名）
                for tag, label in ((root, "根元素名"), ("GtolFrame", "猜的名字(对照)")):
                    xml = "<%s/>" % tag
                    try:
                        r = sw_connect.safe_get_com_member(frame, "SetSymbolXml", xml)
                        print("     `SetSymbolXml(<%s/>)` [%s] ⇒ **%r**" % (tag, label, r))
                        ev.setdefault("set_xml_trials", []).append({"xml": xml, "ret": repr(r)})
                    except Exception as exc:      # noqa: BLE001
                        print("     `SetSymbolXml(<%s/>)` [%s] 抛错: %s" % (tag, label, str(exc)[:50]))
                        ev.setdefault("set_xml_trials", []).append(
                            {"xml": xml, "exc": "%s: %s" % (type(exc).__name__, str(exc)[:60])})
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
