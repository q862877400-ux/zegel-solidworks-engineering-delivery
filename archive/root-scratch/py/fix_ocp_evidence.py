r"""@brief 修正「OCP 相关声明」的依据 —— 本机没有 `OCP`/`cadquery`/`trimesh`。

## 实测（2026-10-01 轮 77）
```
importlib.util.find_spec('OCP')      → **None**（磁盘上也没有 OCP 目录）
importlib.util.find_spec('cadquery') → None
importlib.util.find_spec('trimesh')  → None
importlib.util.find_spec('ezdxf')    → 可用 · numpy 可用
```
而 `capabilities.yaml` 的 `headless_open_format_writing`（**level: verified**）写着：
```
verified_versions: ["OCP 7.9.3.1.1"]     ← ⚠ **本机没有任何当机依据**
evidence: [..., "pytest tests/test_mcp_headless_open_format.py（**OCP 无头写出**）"]
```
⚠ 实测那个测试 **8 passed**，但它的 OCP 用例**全都 monkeypatch 掉后端**：
```python
monkeypatch.setattr("scripts.advanced_geometry_ocp.execute_ocp_loft", lambda *_args: expected)
monkeypatch.setattr("scripts.advanced_surface_ocp.execute_advanced_surface", lambda *_args: expected)
```
⇒ 它验的是「**MCP 层把参数传对了**」，**不是「OCP 真的能跑」**。
另一条：`tests/test_headless_cad_writer.py` 更是**显式把 OCP 伪装成不可用**
（`lambda name: None if name == "OCP" else original_find_spec(name)`）来测降级路径。

## 精确结论（**不一刀切**）
| 该能力的哪一部分 | 本机有真证据吗 |
|---|---|
| `.cadstudio.json` / STL / OBJ / DXF / SVG / PDF / PNG | ✅ **有**（`tests/test_headless_cad_writer.py` 7 passed，我上轮补过两条） |
| STEP / IGES / BREP / GLB（`OCCT_FORMATS`） | ❌ 缺 OCP ⇒ 走**显式降级**（`headless_cad_writer.py` L587 有记录） |
| `limitations ②`「OCCT 覆盖盒体/圆柱/布尔/Loft」 | ❌ **本机无法复现**（那句话的依据不在这台机器上） |

## 本脚本做的四件（**把依据写对**，不是降级惩罚）
1. `headless_open_format_writing.verified_versions`：`['OCP 7.9.3.1.1']` → **`['ezdxf 1.4.4']`**
   （留**真的**那个；OCP 那个**没有当机依据**）；
2. 把 `evidence` 里那句**误导性**的「（OCP 无头写出）」写准确；
3. 给 `headless_open_format_writing` **加一条 limitation** 记录上述边界；
4. 给 `surface_modeling` / `mold_tools`（都写「可选 OCP」）**各加一条 limitation**
   记录「本机缺 OCP ⇒ 那些 headless-occt 声明在当前机器上无法复现」。

# ── 来源 ──
# 仓库:   本项目自身（清单修正脚本）
# 文件:   D:\AI\SW\fix_ocp_evidence.py
# 定位:   承接 `AGENTS.md §一 A4`：「`verified` 必须有**我们自己的运行证据**」——
#         本次把「证据指向的东西**本机根本不存在**」这一类如实标出来（同 `motion_study` 那次）。
# 官方依据: 不适用（本项目内部工具）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

CAP = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")

OCP_NOTE = (
    "⚠ **2026-10-01 实测（轮 77）：本机没有 `OCP` / `cadquery` / `trimesh`**"
    "（`importlib.util.find_spec` 全为 `None`，磁盘上也没有 OCP 目录）。"
    "⇒ 本条 limitations 里涉及 **headless-occt** 的声明**在当前这台机器上无法复现**；"
    "`tests/` 里对 OCP 后端的用例**都 monkeypatch 掉了后端**（验的是 MCP 层传参，不是 OCP 真跑），"
    "`tests/test_headless_cad_writer.py` 更是**显式把 OCP 伪装成不可用**来测降级路径。"
    "⇒ 这些声明**不是假的**（代码里确有该路径、且降级行为有测试），但**其运行证据不在本机** ——"
    "按铁律 5 如实标注，等装了 `cadquery-ocp` 的机器上重跑才能升级为当机证据。"
)

EVIDENCE_FIXED = [
    "pytest tests/test_headless_cad_writer.py（**7 passed**；覆盖非 OCP 的全部写出格式："
    ".cadstudio.json / STL / OBJ / DXF / SVG / PDF / PNG —— 含 PNG 魔数、%PDF、<svg、STL solid、"
    "OBJ `\\nf `、previewManifest，以及**输入文档只读**与 **dwg 必须 blocked 且不产文件**）",
    "pytest tests/test_mcp_headless_open_format.py（**8 passed**；⭐ **它验的是 MCP 层的参数传递** ——"
    "OCP 后端由 `monkeypatch.setattr` 替换为假实现，**不代表 OCP 真能跑**，见本条 limitations 末条）",
]


def _add_limitation(item: dict, text: str) -> bool:
    lims = item.setdefault("limitations", [])
    if any(text[:40] in str(x) for x in lims):
        return False
    lims.append(text)
    return True


def main() -> int:
    raw = CAP.read_text(encoding="utf-8")
    data = json.loads(raw)
    assert json.dumps(data, ensure_ascii=False, indent=2) + "\n" == raw, "往返不是逐字节相同 ⇒ 停"
    caps = {c["id"]: c for c in data["capabilities"]}

    # ① 去掉没有当机依据的 OCP 版本
    a = caps["headless_open_format_writing"]
    old_vv = list(a.get("verified_versions") or [])
    a["verified_versions"] = ["ezdxf 1.4.4"]

    # ② evidence 写准确（去掉误导性的「（OCP 无头写出）」）
    a["evidence"] = EVIDENCE_FIXED

    # ③④ 三条能力各加一条如实标注
    added = {
        "headless_open_format_writing": _add_limitation(a, OCP_NOTE),
        "surface_modeling": _add_limitation(caps["surface_modeling"], OCP_NOTE),
        "mold_tools": _add_limitation(caps["mold_tools"], OCP_NOTE),
    }

    CAP.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    after = json.loads(CAP.read_text(encoding="utf-8"))
    got = {c["id"]: c for c in after["capabilities"]}
    print("  ① headless_open_format_writing.verified_versions: %s → %s"
          % (old_vv, got["headless_open_format_writing"]["verified_versions"]))
    print("  ② evidence 已改写（去掉误导性的「OCP 无头写出」），%d 条"
          % len(got["headless_open_format_writing"]["evidence"]))
    for k, v in added.items():
        print("  %s %s 加 limitation：现在 %d 条"
              % ("③④" if v else "（已存在）", k, len(got[k]["limitations"])))
    from collections import Counter
    print("  level 分布（**不变**，只改依据不降级）：%s"
          % dict(Counter(x["level"] for x in after["capabilities"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
