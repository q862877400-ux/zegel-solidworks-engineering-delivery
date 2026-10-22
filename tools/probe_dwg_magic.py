r"""@brief 探针：`.dwg` 导出来的**到底是 DWG 还是 DXF**？—— **读魔数说话**。

## 为什么查这个
`scripts/sw_export.py` 的 `export_to_dxf` 文档串写着「导出为 **DXF/DWG** 格式」，
而 `_export_for_format` 把 **`.dwg` 和 `.dxf` 都路由到同一个 `export_to_dxf`**。
⇒ ★ 那 `.dwg` 真的出 DWG 吗？**可验**：
```
DXF 的魔数：文件以 `0` + 换行 + `SECTION`（或 `999`）开头 —— **纯文本**
DWG 的魔数：文件以 **`AC10xx`**（如 `AC1032`）开头 —— **二进制**
⇒ ★★ 读前 6 字节就能分开，**不用猜**。
```

## 判据
```
① 两个文件都生成且非空
② ★★ **`.dwg` 的魔数**：是 `AC10xx`（真 DWG）还是 DXF 文本（**名不副实**）
③ ★ 对照：`.dxf` 的魔数应当是 DXF 文本
```

## ⚠ 安全
**只在新零件上跑**；收尾**关件不保存** + **查模态框**（走共享实现）。

# ── 来源 ──
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_dwg_magic.py
# 定位:   给 Spec Kit `075` 取「`.dwg` 是不是真 DWG」的证据。
# 官方依据: `IModelDocExtension.SaveAs3`（本仓已在用）· DWG 文件头规范（`AC10xx`）
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

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "dwg-magic.json")
DXF = Path(Path(__file__).resolve().parents[1] / "output" / "magic-probe.dxf")
DWG = Path(Path(__file__).resolve().parents[1] / "output" / "magic-probe.dwg")


def magic(path: Path) -> dict:
    """读文件头，判它是 DXF 文本还是 DWG 二进制。"""
    if not path.is_file():
        return {"exists": False}
    b = path.read_bytes()[:16]
    out = {
        "exists": True,
        "bytes": path.stat().st_size,
        "head_ascii": b.decode("ascii", "replace")
        .replace("\r", "\\r")
        .replace("\n", "\\n"),
    }
    if b[:2] == b"AC" and b[2:4].isdigit():
        out["kind"] = "DWG"
        out["version"] = b[:6].decode("ascii", "replace")
    elif b[:1] == b"0" or b[:3] in (b"999", b"  0"):
        out["kind"] = "DXF"
    else:
        out["kind"] = "UNKNOWN"
    return out


def main() -> int:
    ev: dict = {"started": time.strftime("%Y-%m-%d %H:%M:%S")}
    sw = None
    doc = None
    try:
        import sw_connect
        from scripts import sw_part, sw_export

        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass
        doc = sw_connect.new_document(sw, "part")
        #: ⚠⚠ 第一版用**普通拉伸件** ⇒ 两条都报
        #: `ValueError: 导出展开 DXF 前必须先保存钣金零件`（**错误清晰、是对的**）
        #: ⇒ ★ 零件路径要求：**钣金件** + **必须先保存** ⇒ 改用钣金基体法兰。
        from scripts import sw_sheet_metal

        sw_part.start_sketch(doc)
        sw_part.sketch_corner_rectangle(doc, 0.0, 0.0, 60.0, 40.0)
        sw_part.end_sketch(doc)
        #: ⚠ `create_base_flange(model, sketch_ref, spec)` —— 参数是 **spec 数据类**，
        #: 且长度单位**全部是米**（`BaseFlangeSpec` 的文档串写明）。
        sw_sheet_metal.create_base_flange(
            doc,
            "草图1",
            sw_sheet_metal.BaseFlangeSpec(
                thickness=0.001, bend_radius=0.001, depth=0.040
            ),
        )
        #: ★ 官方要求先保存（本探针存到 **output/**，scratch 用途，收尾会删）
        SAVED = Path(
            Path(__file__).resolve().parents[1] / "output" / "magic-probe-part.sldprt"
        )
        if SAVED.exists():
            SAVED.unlink()
        sw_connect.save_document(doc, str(SAVED))
        print("  造出钣金件并**已保存**到 %s" % SAVED.name)

        for f in (DXF, DWG):
            if f.exists():
                f.unlink()
        DXF.parent.mkdir(parents=True, exist_ok=True)

        for path, tag in ((DXF, "dxf"), (DWG, "dwg")):
            try:
                sw_export.export_to_dxf(doc, path)
                print("  export_to_dxf(.%s) 未抛异常" % tag)
            except Exception as exc:  # noqa: BLE001
                print(
                    "  export_to_dxf(.%s) ⇒ %s: %s"
                    % (tag, type(exc).__name__, str(exc)[:90])
                )
            ev[tag] = magic(path)
            m = ev[tag]
            if m.get("exists"):
                print(
                    "     · %s: %d 字节 · 头部 %r · **判定 = %s** %s"
                    % (
                        path.name,
                        m["bytes"],
                        m["head_ascii"][:12],
                        m["kind"],
                        m.get("version", ""),
                    )
                )
            else:
                print("     · %s: **文件不存在**" % path.name)

        d, g = ev.get("dxf", {}), ev.get("dwg", {})
        print()
        print("  ── 判定 ──")
        print("     `.dxf` 是 DXF 文本: %s" % (d.get("kind") == "DXF"))
        if g.get("kind") == "DWG":
            print(
                "     ★★ **`.dwg` 是真 DWG**（版本 %s）⇒ 那条路由**名实相符**"
                % g.get("version")
            )
        elif g.get("kind") == "DXF":
            print(
                "     ★★★ **`.dwg` 里装的是 DXF**（头部 %r）⇒ **名不副实**"
                % g.get("head_ascii", "")[:12]
            )
            print(
                "       ⇒ `export_to_dxf` 的文档串写「DXF/DWG」是**误导**，或该后端不支持真 DWG"
            )
        else:
            print(
                "     ⚠ `.dwg` 判定 = %s（既非 DWG 也非 DXF）⇒ **未查明**"
                % g.get("kind")
            )
        ev["dwg_is_real_dwg"] = g.get("kind") == "DWG"
        ev["dwg_is_dxf_content"] = g.get("kind") == "DXF"
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
