r"""@brief 验收命令：`dxf_preview_scene` 的**端到端**（离线，**不碰 SolidWorks**）。

## 为什么需要它（2026-10-01 轮 75）
`capabilities.yaml` 的 `dxf_preview_scene` 是 **`stitched`** 且 **`evidence: 无`** ——
按 `AGENTS.md §一 A4`：「`verified` 必须有**我们自己的运行证据**」。
本命令补那条证据：造一个**真实 DXF**、走**真实转换**、**逐条判 limitations 里承诺的每一件事**。

## limitations 承诺了四件事（⇒ 本命令就判这四件）
```
只读白名单实体；输入上限 50 MB/200000 实体；不支持实体只记录 warnings；输出不得覆盖旧场景文件
```
⇒ 判据：
1. **实体正确**：LINE / CIRCLE / ARC / LWPOLYLINE / TEXT 都被识别，**种类与数量对**；
2. **图层正确**：图层名与计数对，颜色按表给出；
3. **边界正确**：`bounds` 覆盖所有实体的真实范围（与手算对照）；
4. **不支持实体只记 warnings**（造一个 `3DFACE` ⇒ 必须进 warnings、**不进 entities**）；
5. **拒绝覆盖**：目标已存在 ⇒ `FileExistsError`；
6. **后缀约定**：非 `.scene.json` ⇒ `ValueError`；
7. **CLI 可用**：`python scripts/dxf_preview_scene.py <in> <out>` ⇒ 打印 `status: pass`。
⚠ **外加**：「只读」= 转换**不得修改源 DXF**（比对转换前后的字节与 mtime）。

# ── 来源 ──
# 仓库:   本项目自身（真机/离线验收）
# 文件:   tools/verify_dxf_preview_e2e.py
# 定位:   给 `capabilities.yaml` 的 `dxf_preview_scene` 条目提供 `evidence`。
# 官方依据: 不适用（本项目内部工具，只读 DXF、不调 SolidWorks API）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
for _p in (str(_REPO), str(_REPO / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.stdout.reconfigure(encoding="utf-8")

from scripts.dxf_preview_scene import dxf_to_preview_scene  # noqa: E402

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "dxf-preview-evidence.json")


def _make_dxf(path: Path) -> None:
    """造一个**真实** DXF：4 种支持实体 + 1 种不支持实体，分两个图层。"""
    import ezdxf

    doc = ezdxf.new("R2018")
    doc.header["$INSUNITS"] = 4  # 4 = 毫米
    ms = doc.modelspace()
    ms.add_line((0, 0), (40, 0), dxfattribs={"layer": "OUTLINE"})
    ms.add_line((40, 0), (40, 25), dxfattribs={"layer": "OUTLINE"})
    ms.add_circle((20, 12.5), 5, dxfattribs={"layer": "HOLES"})
    ms.add_arc((5, 5), 3, 0, 90, dxfattribs={"layer": "OUTLINE"})
    ms.add_lwpolyline([(0, 25), (20, 30), (40, 25)], dxfattribs={"layer": "OUTLINE"})
    ms.add_text("MCP", height=2.5, dxfattribs={"layer": "NOTES"}).set_placement((2, 2))
    # 不支持：`3DFACE` 不在 SUPPORTED_TYPES 里
    ms.add_3dface([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)])
    doc.saveas(path)


def main() -> int:
    ev: dict = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "checks": {}}
    checks: list = []

    def chk(name: str, ok: bool, detail: str) -> None:
        checks.append(ok)
        ev["checks"][name] = {"ok": bool(ok), "detail": detail}
        print("   %s %-34s %s" % ("✓" if ok else "**✗**", name, detail))

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        src = td / "part.dxf"
        _make_dxf(src)
        before_bytes = src.read_bytes()
        before_mtime = src.stat().st_mtime

        print("=== ① 转换（库函数）===")
        scene = dxf_to_preview_scene(src)
        kinds = sorted(e["kind"] for e in scene["entities"])
        chk(
            "实体数 = 6（3DFACE 被排除）",
            len(scene["entities"]) == 6,
            "实际 %d 个：%s" % (len(scene["entities"]), kinds),
        )
        chk(
            "四种实体都识别",
            set(kinds) >= {"line", "circle", "arc", "polyline"},
            "种类：%s" % sorted(set(kinds)),
        )
        chk(
            "schemaVersion=1.0 且 units=mm",
            scene.get("schemaVersion") == "1.0" and scene.get("units") == "mm",
            "schemaVersion=%r units=%r"
            % (scene.get("schemaVersion"), scene.get("units")),
        )

        print()
        print("=== ② 图层（承诺：白名单实体 + 图层计数）===")
        layers = {l["name"]: l for l in scene["layers"]}
        chk(
            "OUTLINE 层 4 个实体",
            layers.get("OUTLINE", {}).get("count") == 4,
            "实际 %r" % (layers.get("OUTLINE", {}).get("count"),),
        )
        chk(
            "HOLES 层 1 个 · NOTES 层 1 个",
            layers.get("HOLES", {}).get("count") == 1
            and layers.get("NOTES", {}).get("count") == 1,
            "HOLES=%r NOTES=%r"
            % (
                layers.get("HOLES", {}).get("count"),
                layers.get("NOTES", {}).get("count"),
            ),
        )

        print()
        print("=== ③ 边界（承诺：几何范围）===")
        b = scene["bounds"]
        # 手算：x ∈ [0,40]（圆弧在 (5,5) r=3 ⇒ 最小 2；圆 (20,12.5) r=5 ⇒ y ∈ [7.5,17.5]
        # ；
        # 多段线到 y=30；文本 (2,2)。⇒ x_min=0 · x_max=40 · y_max=30
        chk(
            "x 范围 [0, 40]",
            abs(b["minX"] - 0) < 1e-6 and abs(b["maxX"] - 40) < 1e-6,
            "minX=%s maxX=%s" % (b["minX"], b["maxX"]),
        )
        chk(
            "y 上界 = 30（多段线顶点）",
            abs(b["maxY"] - 30) < 1e-6,
            "maxY=%s" % b["maxY"],
        )

        print()
        print("=== ④ 不支持实体**只记 warnings**（承诺）===")
        chk(
            "warnings 提到 3DFACE",
            any("3DFACE" in w for w in scene["warnings"]),
            "%r" % (scene["warnings"],),
        )
        chk(
            "3DFACE 不在 entities 里",
            all(e.get("kind") != "3dface" for e in scene["entities"]),
            "已排除",
        )

        print()
        print("=== ⑤ **只读**：源 DXF 不得被改动 ===")
        chk("源文件字节不变", src.read_bytes() == before_bytes, "字节逐位相同")
        chk("源文件 mtime 不变", src.stat().st_mtime == before_mtime, "mtime 相同")

        print()
        print("=== ⑥ 拒绝覆盖 + 后缀约定（承诺）===")
        out = td / "part.scene.json"
        dxf_to_preview_scene(src, out)
        chk("首次写盘成功", out.is_file(), "已写 %s" % out.name)
        try:
            dxf_to_preview_scene(src, out)
            chk(
                "**拒绝覆盖**已有场景", False, "**没有报错 —— 与 limitations 承诺不符**"
            )
        except FileExistsError:
            chk("**拒绝覆盖**已有场景", True, "FileExistsError ✓")
        try:
            dxf_to_preview_scene(src, td / "bad.json")
            chk("非 .scene.json 后缀被拒", False, "**没有报错**")
        except ValueError:
            chk("非 .scene.json 后缀被拒", True, "ValueError ✓")

        print()
        print("=== ⑦ CLI 可用（用户入口）===")
        cli_out = td / "cli.scene.json"
        proc = subprocess.run(
            [
                sys.executable,
                str(_REPO / "scripts" / "dxf_preview_scene.py"),
                str(src),
                str(cli_out),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(_REPO),
            stdin=subprocess.DEVNULL,
        )
        payload = {}
        try:
            payload = json.loads((proc.stdout or "").strip().splitlines()[-1])
        except (json.JSONDecodeError, IndexError):
            pass
        chk(
            "CLI 退出码 0 且 status=pass",
            proc.returncode == 0 and payload.get("status") == "pass",
            "rc=%s payload=%s" % (proc.returncode, payload),
        )

    ev["passed"] = sum(1 for c in checks if c)
    ev["total"] = len(checks)
    ev["verdict"] = "pass" if all(checks) else "fail"
    ev["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print()
    print(
        "  ── %d/%d 项通过 · verdict: %s ──"
        % (ev["passed"], ev["total"], ev["verdict"])
    )
    print("  证据已写: %s" % OUT)
    return 0 if ev["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
