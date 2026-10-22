"""文件摘要的单一实现（原先在两个模块里各有一份）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   scripts/sw_file_digest.py
# 定位:   ★ 2026-10-22（仓库统一化 · 待办「同一功能多份实现」）：`_sha256` 原先在
#         `delivery_compare.py` 与 `sw_delivery.py` 里**各有一份，逐字相同**。
#         本模块给出唯一实现；判据 = `scripts/check_repo_uniformity.py` 指标⑤
#         「跨文件同函数体组」的组数下降（基线只许降）。
# 官方依据: 不适用（本模块不调 COM；只用标准库 `hashlib`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import hashlib
from pathlib import Path


def sha256_file(path: Path) -> str:
    """★ 分块读取并回 `sha256` 十六进制摘要（★ 大文件不整块进内存）。

    ★ 2026-10-22：原为 `delivery_compare._sha256` 与 `sw_delivery._sha256` 两份逐字相同的实现。
    """
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
