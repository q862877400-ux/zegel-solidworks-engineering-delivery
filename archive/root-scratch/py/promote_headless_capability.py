r"""@brief 把 `autocad_headless_preview` 从 `stitched` 升到 `verified`。

## 依据（`AGENTS.md §一 A4`）
> `verified` 必须有**我们自己的运行证据**。

轮 76 实测：**既有测试 `tests/test_headless_cad_writer.py` 已经很完整**
（PNG 魔数 / `%PDF` / `<svg` / STL `solid` / OBJ `\nf ` / DXF 实体 / previewManifest），
**5 passed** ⇒ 但核 limitations 时发现**点名承诺的「不能读取或写入 DWG」没有覆盖**
（只测了通用未知格式 `sat`）⇒ 本轮**补两条**：
* `test_headless_writer_refuses_dwg_and_does_not_fake_a_file` —— `dwg` 必须 `blocked`、
  **磁盘上不许出现任何 dwg 文件**（比"返回 blocked"更强：**杜绝"假装写了 DWG"**）；
* `test_headless_writer_does_not_modify_the_input_document` —— **只读**承诺
  （输入文档的 sha256 与 mtime 都不变）。
⇒ **7 passed** ⇒ 证据成立。

# ── 来源 ──
# 仓库:   本项目自身（清单更新脚本）
# 文件:   D:\AI\SW\promote_headless_capability.py
# 定位:   单条能力清单升级（只改一条，**不做批量**）。
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

EVIDENCE = [
    "pytest tests/test_headless_cad_writer.py（**7 passed**）—— 覆盖 limitations 承诺的每一句："
    "PNG（**魔数** `\\x89PNG` + IHDR 尺寸）· SVG/PDF/STL/OBJ/DXF 回退 · PreviewScene JSON 与 "
    "previewManifest · **`dwg` 必须 blocked 且磁盘上不出现任何 dwg 文件**（杜绝「假装写了 DWG」）· "
    "**输入文档只读**（sha256 与 mtime 不变）",
]


def main() -> int:
    raw = CAP.read_text(encoding="utf-8")
    data = json.loads(raw)
    assert json.dumps(data, ensure_ascii=False, indent=2) + "\n" == raw, "往返不是逐字节相同 ⇒ 停"

    item = next(x for x in data["capabilities"] if x["id"] == "autocad_headless_preview")
    before = (item["level"], list(item.get("evidence") or []),
              list(item.get("verified_versions") or []))
    item["level"] = "verified"
    item["evidence"] = EVIDENCE
    item["verified_versions"] = ["ezdxf 1.4.4"]

    CAP.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    after = json.loads(CAP.read_text(encoding="utf-8"))
    got = next(x for x in after["capabilities"] if x["id"] == "autocad_headless_preview")
    from collections import Counter
    print("  autocad_headless_preview: level %s → **%s**" % (before[0], got["level"]))
    print("  evidence: %s → %d 条" % (before[1] or "（空）", len(got["evidence"])))
    print("  verified_versions: %s → %s" % (before[2] or "（空）", got["verified_versions"]))
    print("  limitations: %d 条（**一条不删**）" % len(got.get("limitations") or []))
    print("  level 分布: %s" % dict(Counter(x["level"] for x in after["capabilities"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
