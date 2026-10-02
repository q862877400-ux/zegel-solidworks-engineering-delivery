r"""SolidWorks Toolbox 零件索引：按标准 / 型号 / 关键词查零件并取路径。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本机 SolidWorks Toolbox 安装目录（达索随 SOLIDWORKS 附带的能力包）
# 文件:   D:\SOLIDWORKS Data\browser\**\*.sldprt  —— 1,844 个零件 / 19 套标准
# 定位:   零件索引的**数据文件**是本模块同目录的 `toolbox_index.json`。
# ⚑ 索引由 `tools/build_toolbox_index.py` 遍历目录树机械生成。
# ⚠⚑ **故意不解析** `browser/ToolboxFiles.index`：它是 .NET BinaryFormatter
#   二进制（头 `00 01 00 00 00 ff ff ff ff` + 内部类型 `Isldtoolboxdata`）。
#   反序列化这种来路不明的二进制**有代码执行风险**；遍历目录树能得到同样结果。
#
# ⚠ 本索引的**范围**（重要，别误用）
#   ✅ 含：标准 / 大类 / 小类 / 零件名 / 完整路径
#   ❌ 不含：**型号→尺寸的工程数据**（导轨行程、丝杆导程、额定载荷…）
#      官方 Toolbox 的紧固件是「近似几何，不含真实螺纹」；齿轮不是真渐开线。
#      尺寸是**零件文件内的配置**，不在文件名里 ⇒ **要拿尺寸得开文件读配置**。
#   ❌ 不含：丝杆、直线导轨、欧标铝型材 —— 实测全库为 0（这三类要厂商，见
#      docs/toolbox-survey.md）。
#
# ⚠ 本模块为静态整理，未在本机实测 SolidWorks 行为（见 AGENTS.md 铁律 2）
# 覆盖:   后续同级定义
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

__all__ = ["INDEX_PATH", "load_index", "list_standards", "search", "part_path"]

INDEX_PATH = Path(__file__).resolve().parent / "toolbox_index.json"


def load_index(path: Path | None = None) -> dict[str, Any]:
    """读入索引。⚠ 文件不存在时**明说**，不返回空壳冒充成功。"""
    p = Path(path) if path else INDEX_PATH
    if not p.is_file():
        raise FileNotFoundError(
            f"Toolbox 索引不存在：{p}\n"
            f"⚠ SolidWorks Toolbox 装在 D:\\SOLIDWORKS Data\\。\n"
            f"  若刚装 Toolbox，用 tools/build_toolbox_index.py 重建。")
    return json.loads(p.read_text(encoding="utf-8"))


def list_standards(index: dict[str, Any] | None = None) -> dict[str, int]:
    """返回 {标准名: 零件数}。"""
    data = index if index is not None else load_index()
    out: dict[str, int] = {}
    for item in data["parts"]:
        out[item["standard"]] = out.get(item["standard"], 0) + 1
    return dict(sorted(out.items(), key=lambda kv: -kv[1]))


def search(keyword: str, standard: str = "", category: str = "",
           index: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """按关键词 / 标准 / 大类查零件。**关键词只匹配零件名，不做模糊拼写纠正**。

    返回的每条含 ``part`` / ``code`` / ``path`` / ``standard`` / ``category``。
    ⚠ 官方命名里**不含尺寸**（尺寸是文件内配置）⇒ 按「Φ20」这种查不到，
       要按零件名关键词（如 ``ball bearing``、``hex head``）。
    """
    data = index if index is not None else load_index()
    kw = keyword.strip().lower()
    hits = []
    for item in data["parts"]:
        if standard and item["standard"].lower() != standard.strip().lower():
            continue
        if category and item["category"].lower() != category.strip().lower():
            continue
        if kw and kw not in item["part"].lower() and kw not in item["code"].lower():
            continue
        hits.append(item)
    return hits


def part_path(standard: str, part_name: str,
              index: dict[str, Any] | None = None) -> str:
    """取某个零件的**完整路径**（供 `IAssemblyDoc.AddComponent5` 的 File 参数用）。

    ⚠ 查不到就抛错，**不返回猜测的路径** —— 猜出来的路径插进装配会静默失败。
    """
    data = index if index is not None else load_index()
    hits = [i for i in data["parts"]
            if i["standard"].lower() == standard.strip().lower()
            and i["part"].lower() == part_name.strip().lower()]
    if not hits:
        near = search(part_name, standard=standard, index=data)[:5]
        hint = ("；相近的: " + ", ".join(h["part"] for h in near)) if near else ""
        raise KeyError(
            f"Toolbox 里没有 {standard} / {part_name}{hint}\n"
            f"⚠ 尺寸是零件文件内的配置，不在文件名里 —— "
            f"用 list_standards() + search() 先定位零件名。")
    if len(hits) > 1:
        paths = "\n    ".join(h["path"] for h in hits[:5])
        raise KeyError(f"{standard} / {part_name} 命中多个，请写全路径:\n    {paths}")
    return hits[0]["path"]
