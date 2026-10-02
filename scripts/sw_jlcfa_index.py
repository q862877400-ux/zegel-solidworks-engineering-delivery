r"""嘉立创 FA 全库零件索引：按型号 / 分类 / 品牌 / 产品查询。

# ── 来源 ─────────────────────────────────────────────────────────────
# 文件:   嘉立创 FA 选型插件 v2.4.1-20260918-1（本机已安装）
# 路径:   D:\Program Files\SOLIDWORKS Corp\JLCFA Parts Library Plugin
#         Full Version v2.4.1-20260918-1\ForFaceSelector\ForFaceSelectorData\DB\
# 定位:   从插件的**运行时明文 SQLite**（2.9 GB，49 表）抽出的**全库**选型索引。
#
# ⚠ 合规边界（本项目对该厂商数据的处置）
# --------------------------------------
# · **只读**打开（sqlite3 ``mode=ro``），**不修改任何厂商文件**。
# · **不解密、不逆向、不破解**。加密的只有传输包 ``DB.zip``（传统 ZipCrypto）；
#   插件运行时把它解到 ``ForFaceSelectorData\DB\``，那里是**明文**。
#   本模块只读那份明文 —— 厂商加密保护的是传输，不是运行时数据。
# · 只抽**目录性元数据**（型号/产品/品牌/分类），**不复制模型文件本体**。
#
# ⚠⚑ 索引覆盖的与没覆盖的（别误用）
# -----------------------------------
# ✅ 有：63,234 个型号 · 8,207 个产品 · 209 个品牌 · 200 个分类
#         （含「导轨」3 个分类、「型材」5 个、「直线」7 个）
#         库内另有 se_fa_product_param 330,208 条参数定义、
#         se_fa_product_param_value 447,527 条可选值（本索引未展开）
# ❌ **没有型号→模型文件的路径**。
#    原因（本机实测）：``se_fa_product_model_third_party_relation`` 的
#    ``product_model_key_id`` 是 **1000000+ 的第三方模型目录号**，
#    与 ``se_product_code.id``（雪花 ID）**无交集**（Python 比对 0 命中），
#    与 ``bu_model.id`` 仅 228 个偶然撞上。
#    ⇒ 「型号 → 本地 .sldprt」这条链**没有落在数据库里**，
#       它由插件运行时另行解析。
# 覆盖:   后续同级定义
# ⚠ 本模块为静态整理，未在本机实测 SolidWorks 行为（见 AGENTS.md）
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

__all__ = ["INDEX_PATH", "load_index", "list_categories", "search", "summarize"]

INDEX_PATH = Path(__file__).resolve().parent / "jlcfa_index.json"


def load_index(path: Path | None = None) -> dict[str, Any]:
    """读入索引。⚠ 文件不存在时**明说**，不返回空壳冒充成功。"""
    p = Path(path) if path else INDEX_PATH
    if not p.is_file():
        raise FileNotFoundError(
            f"嘉立创 FA 索引不存在：{p}\n"
            f"  它从插件的明文 SQLite 抽取，需先运行 tools/build_jlcfa_index.py；\n"
            f"  数据源：D:\\Program Files\\SOLIDWORKS Corp\\JLCFA Parts Library "
            f"Plugin Full Version ...\\ForFaceSelector\\ForFaceSelectorData\\DB\\")
    return json.loads(p.read_text(encoding="utf-8"))


def summarize(index: dict[str, Any] | None = None) -> dict[str, Any]:
    """索引规模概览。"""
    return dict((index if index is not None else load_index())["counts"])


def list_categories(index: dict[str, Any] | None = None) -> list[str]:
    """全部 200 个分类名（含「导轨」「型材」「直线」等）。"""
    return list((index if index is not None else load_index())["categories"])


def search(keyword: str = "", brand: str = "", product: str = "", category: str = "",
           index: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """按关键词 / 品牌 / 产品 / 分类查型号。

    ⚑ **四个字段全都要搜** —— ��工漏了 ``product`` 与 ``category``，
    导���「铝型材」实测数据里有 12 条、却返回 0（关键词只出现在产品名里）。
    ⚠ **只做子串匹配，不做拼写纠正** —— 官方没提供模糊检索接口，
    编一个「智能建议」反而会悄悄返回错件。
    """
    data = index if index is not None else load_index()
    kw = keyword.strip().lower()
    br = brand.strip().lower()
    pr = product.strip().lower()
    ct = category.strip().lower()
    hits = []
    for item in data["parts"]:
        if kw and not any(kw in str(item.get(f, "")).lower()
                         for f in ("code", "name", "product", "brand")):
            continue
        if br and br not in item["brand"].lower():
            continue
        if pr and pr not in item["product"].lower():
            continue
        if ct and not any(ct in c.lower() for c in item.get("category", [])):
            continue
        hits.append(item)
    return hits
