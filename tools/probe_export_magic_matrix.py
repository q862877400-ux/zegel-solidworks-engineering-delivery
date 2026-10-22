r"""@brief 探针：**导出格式矩阵** —— 逐个格式**读魔数**，判「名实相符」与否。

## 为什么做这个
轮 156 用**读魔数**证明了 `.dwg` 是真 DWG（`AC1015`）⇒ ★ 那个手法**可以一次覆盖全部格式**。
⇒ 本探针产出一张**可复用的矩阵**：每个格式的**文件头签名** + 大小 + 判定。

## 判据（每个格式一行）
```
① 文件生成且非空
② ★★ **文件头魔数**落在该格式的已知签名集里
③ ⚠ 有前置条件的（如 DXF/DWG 要钣金件）**如实记前置条件**，不当成功能失败
```

## ⚠ 安全
**只在一个钣金 scratch 件上跑**（存到 `output/`，gitignored）；收尾**关件不保存** + **查模态框**。

# ── 来源 ──
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_export_magic_matrix.py
# 定位:   给 Spec Kit `076` 产出「导出格式 ↔ 魔数」矩阵（事实 96 的扩展）。
# 官方依据: 各格式规范：STEP(`ISO-10303-21`) · STL(`solid`/二进制长度字段) · IGES(`S`/`1
#           H`) ·
#          Parasolid(`**ABCDEFGH`/文本) · PDF(`%PDF-`) · DXF(文本 `0/SECTION`) ·
#          DWG(`AC10xx`) · PNG(`\x89PNG`) · JPEG(`\xff\xd8\xff`) · BMP(`BM`)
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
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

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "export-magic-matrix.json")
DIR = Path(Path(__file__).resolve().parents[1] / "output" / "magic-matrix")
PART = Path(Path(__file__).resolve().parents[1] / "output" / "magic-matrix-part.sldprt")
def classify(b: bytes) -> str:
    """按文件头判格式（**只看头，不解内容**）。"""
    if b[:8] == b"\x89PNG\r\n\x1a\n":
        return "PNG"
    if b[:3] == b"\xff\xd8\xff":
        return "JPEG"
    if b[:2] == b"BM":
        return "BMP"
    if b[:5] == b"%PDF-":
        return "PDF"
    if b[:2] == b"AC" and b[2:4].isdigit():
        return "DWG(%s)" % b[:6].decode("ascii", "replace")
    if b.startswith(b"ISO-10303-21"):
        return "STEP"
    if b[:1] in (b"0", b"9") or b[:3] in (b"999", b"  0"):
        return "DXF"
    head = b[:12]
    if head.lower().startswith(b"solid") or b[:5] == b"solid":
        return "STL(ascii)"
    if b.startswith(b"**ABCDEFGH"):
        return "Parasolid(text)"
    if b.startswith(b"**GENERIC"):
        return "Parasolid(binary)"
    if b[:1] in (b"S", b"s") and len(b) > 72:
        return "IGES"
    #: STL 二进制：前 80 字节是 header，接着 4 字节三角面数（小端）
    if len(b) >= 84:
        import struct
        n = struct.unpack_from("<I", b, 80)[0]
        return "STL(binary?)" if 0 < n < 5_000_000 else "UNKNOWN"
    return "UNKNOWN"


def main() -> int:
    ev: dict = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "rows": []}
    sw = None
    doc = None
    try:
        import sw_connect
        from scripts import sw_part, sw_sheet_metal, sw_export
        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:      # noqa: BLE001
            pass
        doc = sw_connect.new_document(sw, "part")
        sw_part.start_sketch(doc)
        sw_part.sketch_corner_rectangle(doc, 0.0, 0.0, 60.0, 40.0)
        sw_part.end_sketch(doc)
        sw_sheet_metal.create_base_flange(
            doc, "草图1",
            sw_sheet_metal.BaseFlangeSpec(thickness=0.001, bend_radius=0.001, depth=0.040))
        DIR.mkdir(parents=True, exist_ok=True)
        if PART.exists():
            PART.unlink()
        sw_connect.save_document(doc, str(PART))
        print("  钣金件已保存到 %s（scratch）" % PART.name)

        #: (标签, 调用, 扩展名)
        jobs = [
            ("step", lambda p: sw_export.export_to_step(doc, p), ".step"),
            ("stl", lambda p: sw_export.export_to_stl(doc, p), ".stl"),
            ("iges", lambda p: sw_export.export_to_iges(doc, p), ".igs"),
            ("parasolid", lambda p: sw_export.export_to_parasolid(doc, p), ".x_t"),
            ("pdf", lambda p: sw_export.export_to_pdf(doc, p), ".pdf"),
            ("dxf", lambda p: sw_export.export_to_dxf(doc, p), ".dxf"),
            ("dwg", lambda p: sw_export.export_to_dxf(doc, p), ".dwg"),
            ("png", lambda p: sw_export.export_to_image(doc, p), ".png"),
            ("jpg", lambda p: sw_export.export_to_image(doc, p), ".jpg"),
            ("bmp", lambda p: sw_export.export_to_bmp(doc, p, 640, 480), ".bmp"),
        ]
        print()
        print("  %-11s %-11s %-10s %s" % ("格式", "判定", "字节", "备注"))
        for tag, fn, ext in jobs:
            p = DIR / ("probe" + ext)
            if p.exists():
                p.unlink()
            note = ""
            try:
                fn(p)
            except Exception as exc:      # noqa: BLE001
                note = "%s: %s" % (type(exc).__name__, str(exc)[:58])
            row = {"format": tag, "ext": ext, "error": note or None}
            if p.is_file() and p.stat().st_size > 0:
                b = p.read_bytes()[:96]
                #: ⚠⚠ 第一版只打 `classify()` 的判定 —— 而它对 STL/IGES 判错了
                #: （**顺序 bug**：IGES 只认首字节 `S`/`s`，而 ASCII STL 以 `solid` 开头
                #:  ⇒ 先命中 IGES）。⇒ ★ **改成把文件头原文打出来**，用**证据**判，
                #: 不再让一个容易写错的分类器挡住真相。
                head_txt = b[:24].decode("ascii", "replace").replace("\r", "\\r").replace("\n", "\\n")
                row.update(bytes=p.stat().st_size, kind=classify(b),
                           head_hex=b[:8].hex(), head_ascii=head_txt)
            elif not note:
                note = "**文件不存在**"
                row["error"] = note
            ev["rows"].append(row)
            print("  %-11s %-15s %-9s %-30s %s"
                  % (tag, row.get("kind", "—"), row.get("bytes", "—"),
                     repr(row.get("head_ascii", ""))[:30],
                     note or "（读头为准，不看分类器）"))
    except Exception as exc:      # noqa: BLE001
        ev["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:180])
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
    dialogs, _点掉, scanned = _sc.settle_residual_dialogs()
    print()
    print("  收尾：扫了 %d 个窗口 · %s" % (scanned, "无模态框" if not dialogs else dialogs))
    ev["modal_dialogs"] = dialogs
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  证据: %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
