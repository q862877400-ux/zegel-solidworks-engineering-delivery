r"""@brief 探针：**工程图**上 `pdf` / `dwg` 能不能出 —— 补上轮矩阵里唯一没验的那格。

## 背景（轮 157 的尾巴）
```
轮 157 的导出格式矩阵：**9/10 名实相符**，唯一失败的是
  `export_to_pdf(零件, path)` ⇒ `AttributeError: <unknown>.GetSldWorksObject`
★ 而 `export_to_pdf(model, output_path, sheet_names=None)` 的签名里有 `sheet_names`
  ⇒ 语义上**是工程图的入口** ⇒ 本轮**做一张工程图**去补那一格。
```

## 判据
```
① 能否建出**工程图文档**（`new_document(sw, "drawing")`）—— 需要模板
② 能否**保存**（官方要求完整路径）
③ ★★ `export_to_pdf(工程图, path)` ⇒ **读魔数** `%PDF-` + **页数**（`/Type /Page` 计数）
④ ★ `export_to_dxf(工程图, .dwg)` ⇒ **读魔数** `AC10xx`（轮 156 只测了钣金件那条路）
⑤ ⚠ **建不出工程图就如实报"模板不可得"，不当成功能失败**
```

## ⚠ 安全
scratch 文档存到 `output/`（gitignored）；收尾**关件不保存** + **查模态框**。

# ── 来源 ──
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_pdf_on_drawing.py
# 定位:   给 Spec Kit `077` 补上轮矩阵里 `pdf` 那一格。
# 官方依据: `IModelDoc2`（工程图类型 = 3）· `IModelDocExtension.SaveAs3` · PDF 规范（`%P
#           DF-` / `/Type /Page`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if p not in sys.path:
        sys.path.insert(0, p)
sys.stdout.reconfigure(encoding="utf-8")

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "pdf-on-drawing.json")
DIR = Path(Path(__file__).resolve().parents[1] / "output" / "pdf-drawing")
DRW = Path(Path(__file__).resolve().parents[1] / "output" / "pdf-probe.slddrw")


def pdf_pages(path: Path) -> int:
    """数 PDF 里的 `/Type /Page`（**不含 `/Pages`**）—— 只看关键字，不解压流。"""
    blob = path.read_bytes()
    return len(re.findall(rb"/Type\s*/Page[^s]", blob))


def main() -> int:
    ev: dict = {"started": time.strftime("%Y-%m-%d %H:%M:%S")}
    sw = None
    doc = None
    try:
        import sw_connect
        from scripts import sw_export

        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass

        #: ① 建工程图（需模板）
        try:
            doc = sw_connect.new_document(sw, "drawing")
            ev["drawing_created"] = doc is not None
            print("  ① 工程图建出来了: %s" % (doc is not None))
        except Exception as exc:  # noqa: BLE001
            ev["drawing_created"] = False
            ev["drawing_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:140])
            print("  ① ⚠ **建不出工程图**：%s" % ev["drawing_error"])
            print("     ⇒ 如实报「模板不可得」，**不当成功能失败**")
            return 0
        if doc is None:
            print("  ① ⚠ new_document 返回 None ⇒ 如实报「模板不可得」")
            return 0

        try:
            ev["doc_type"] = int(sw_connect.safe_get_com_member(doc, "GetType"))
            print("     文档类型 = %s（3 = 工程图）" % ev["doc_type"])
        except Exception:  # noqa: BLE001
            pass
        try:
            ev["sheet_count"] = int(len(doc.GetSheetNames() or []))
            print("     图纸数 = %s" % ev["sheet_count"])
        except Exception as exc:  # noqa: BLE001
            print("     ⚠ 读图纸数失败: %s" % str(exc)[:60])

        #: ② 保存（官方要求完整路径）
        DIR.mkdir(parents=True, exist_ok=True)
        if DRW.exists():
            DRW.unlink()
        sw_connect.save_document(doc, str(DRW))
        print("  ② 已保存到 %s" % DRW.name)

        #: ③ pdf
        pdf = DIR / "probe-drawing.pdf"
        if pdf.exists():
            pdf.unlink()
        try:
            sw_export.export_to_pdf(doc, pdf)
            if pdf.is_file() and pdf.stat().st_size > 0:
                head = pdf.read_bytes()[:8]
                pages = pdf_pages(pdf)
                ev.update(
                    pdf_bytes=pdf.stat().st_size,
                    pdf_head=head.decode("ascii", "replace"),
                    pdf_pages=pages,
                )
                print(
                    "  ③ ★★ `pdf` 成功：%d 字节 · 头部 %r · **页数 = %d**"
                    % (pdf.stat().st_size, head.decode("ascii", "replace"), pages)
                )
                if head.startswith(b"%PDF-"):
                    print("     ⇒ **魔数 `%PDF-`** ✓ 且页数可数 ⇒ **定量证据**")
            else:
                print(
                    "  ③ ⚠ 没抛异常但**文件不在或为空**（照 `export_to_step` 的纪律挡住）"
                )
                ev["pdf_missing_after_success"] = True
        except Exception as exc:  # noqa: BLE001
            ev["pdf_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:140])
            print("  ③ ✗ `pdf` 失败：%s" % ev["pdf_error"])

        #: ④ dwg（轮 156 只测了钣金件那条路）
        dwg = DIR / "probe-drawing.dwg"
        if dwg.exists():
            dwg.unlink()
        try:
            sw_export.export_to_dxf(doc, dwg)
            if dwg.is_file() and dwg.stat().st_size > 0:
                head = dwg.read_bytes()[:8]
                ev.update(dwg_bytes=dwg.stat().st_size, dwg_head_hex=head.hex())
                kind = (
                    "DWG(%s)" % head[:6].decode("ascii", "replace")
                    if head[:2] == b"AC"
                    else "NOT-DWG"
                )
                print(
                    "  ④ ★ `dwg`：%d 字节 · 头部 %r ⇒ **%s**"
                    % (dwg.stat().st_size, head[:6].decode("ascii", "replace"), kind)
                )
                ev["dwg_kind"] = kind
            else:
                print("  ④ ⚠ `dwg` 没出文件")
        except Exception as exc:  # noqa: BLE001
            ev["dwg_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:140])
            print("  ④ ✗ `dwg` 失败：%s" % ev["dwg_error"])
    except Exception as exc:  # noqa: BLE001
        ev["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:180])
        print("  ⚠ 探针出错: %s" % ev["error"])
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        try:
            if doc is not None and sw is not None:
                t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
        except Exception:  # noqa: BLE001
            pass

    import sw_connect as _sc

    dialogs, _点掉, scanned = _sc.settle_residual_dialogs()
    print(
        "  收尾：扫了 %d 个窗口 · %s"
        % (scanned, "无模态框" if not dialogs else dialogs)
    )
    ev["modal_dialogs"] = dialogs
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("  证据: %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
