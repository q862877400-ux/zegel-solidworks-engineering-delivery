"""元数据 YAML 读取的单一实现（原先有两个名字）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   scripts/engineering/_yaml_loader.py
# 定位:   ★ 2026-10-22（仓库统一化）：`catalog._load_simple_yaml` 与
#         `protocols._load_yaml` 两份**逻辑逐字相同**
#         （都是 `yaml.safe_load(path.read_text()) or {}`）⇒ 收敛到此处。
#         判据 = `scripts/check_repo_uniformity.py` 指标⑤「跨文件同函数体组」只降不升。
# 官方依据: ⚠ `catalog._load_simple_yaml` 的教训（2026-10-12，逐字保留）：
#         第一版**手写**了一个极简 YAML 解析器 ⇒ ★ **域读成 0 个**
#         （处理不了 `- id: x` 后跟缩进子键的列表元素）⇒ ★★ 而「0 个域」看起来像
#         「元数据文件是空的」，不像「解析器坏了」。
#         ⇒ ★ 改判据：**本机有 PyYAML 6.0.3**（已实测）⇒ 用它，★ **不手写解析器**
#         （手写解析器是「发明」，不是「缝合」—— 违反铁律 1）。
# 许可:   本仓库 MIT。无第三方代码引入（PyYAML 是既有运行时依赖）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import pathlib


def load_yaml(path: pathlib.Path) -> dict:
    """★ 读元数据 YAML ⇒ dict（空文件回 `{}`）。

    ★★ **不要手写 YAML 解析器** —— 见模块头的 2026-10-12 实测教训：
      手写版把域读成 0 个，而「0 个域」看起来像「元数据是空的」，不像「解析器坏了」✗
    """
    import yaml  # noqa: PLC0415,F811
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
