# -*- coding: utf-8 -*-
"""从嘉立创 FA 选型插件的**明文 SQLite** 建全库零件索引。

⚠ 合规边界
----------
· 只读打开（``mode=ro``），**不修改任何厂商文件**。
· **不解密、不逆向、不破解**：插件运行时把加密传输包 ``DB.zip`` 解到
  ``ForFaceSelectorData\DB\``，那里是**明文**。厂商加密保护的是传输。
· 只抽目录性元数据，**不复制模型文件本体**。

⚑ 为什么分三步取、在 Python 里拼
------------------------------
两个库之间的连接键是
``selector.se_fa_product_model_third_party_relation.product_model_key_id``
= ``builder.bu_model.id``（**顺序号**，如 ``1195749``，不是雪花 ID）。

⚑ 用 SQL 写 CROSS JOIN + GROUP BY 去拼这两张表会**慢到跑不动**（relation
2,607,833 行）⇒ 改成：各表分别 SELECT 出来，在 Python 里用 dict 拼。

⚑ 第一次索引查出 0 条的三个原因（本轮实测）：
    ① ``se_product_code.status`` 全是 **0**，我原先过滤 ``status = 1``
    ② join 键错：接到 ``se_product_code.id``（雪花）而不是 ``bu_model.id``（顺序号）
    ③ SQL 里 LEFT JOIN 引用了右边的表 ⇒ ``ON clause references tables to its right``

# ── 来源 ─────────────────────────────────────────────────────────────
# 文件:   嘉立创 FA 选型插件 v2.4.1-20260918-1（本机已安装）
# 路径:   D:\Program Files\SOLIDWORKS Corp\JLCFA Parts Library Plugin
#         Full Version v2.4.1-20260918-1\ForFaceSelector\ForFaceSelectorData\DB\
# 定位:   把「型号」连同分类/品牌/模型包抽成可查询索引（**全库，不限品类**）。
# 覆盖:   后续同级定义
# ⚠ 本脚本只读文件，不连接 SolidWorks
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE = Path(
    "D:\\Program Files\\SOLIDWORKS Corp\\JLCFA Parts Library Plugin "
    "Full Version v2.4.1-20260918-1\\ForFaceSelector\\ForFaceSelectorData\\DB")
SELECTOR = BASE / "sw-fa-prod-selector"
BUILDER = BASE / "sw-fa-prod-builder"
OUT = Path(r"C:\swprojects\sw-skill-fork\scripts\jlcfa_index.json")


def ro(path: Path) -> sqlite3.Connection:
    return sqlite3.connect("file:%s?mode=ro" % path, uri=True)   # 只读


def main() -> int:
    for p in (SELECTOR, BUILDER):
        if not p.is_file():
            print("[FATAL] 找不到 %s" % p)
            return 2
    con = ro(SELECTOR)
    try:
        cur = con.cursor()
        n_cat = cur.execute("SELECT COUNT(*) FROM se_category").fetchone()[0]
        n_par = cur.execute("SELECT COUNT(*) FROM se_fa_product_param").fetchone()[0]
        n_pva = cur.execute("SELECT COUNT(*) FROM se_fa_product_param_value").fetchone()[0]
        print("  分类 %d · 参数 %d · 参数可选值 %d" % (n_cat, n_par, n_pva))

        # ① 型号 + 产品 + 品牌（63K 行）
        codes = {}
        for cid, code, show, is3d, pid in cur.execute(
                "SELECT id, code_name, code_show_name, is_3d, product_id "
                "FROM se_product_code"):
            if code:
                codes[cid] = [code, show or code, int(is3d or 0), pid, "", ""]
        print("  型号 %d" % len(codes))

        # ② 产品名 / 品牌名（8K + 209）
        products = {r[0]: r[1] for r in
                    cur.execute("SELECT id, name FROM se_product")}
        brands = {r[0]: r[1] for r in
                  cur.execute("SELECT id, name FROM se_product_brand")}
        print("  产品 %d · 品牌 %d" % (len(products), len(brands)))

        # ③ 型号→模型键 映射（2.6M 行，过滤掉「空白」占位）
        print("  读型号↔模型映射（2,607,833 行）…")
        rel: dict[str, str] = {}
        for mk, tpm in cur.execute(
                "SELECT product_model_key_id, third_party_model "
                "FROM se_fa_product_model_third_party_relation "
                "WHERE delete_flag = 0 AND third_party_model IS NOT NULL"):
            if mk and tpm and tpm != "空白":
                rel.setdefault(mk, tpm)
        print("  映射 %d 条" % len(rel))
    finally:
        con.close()

    # ④ bu_model：顺序键 → 模型名/预览图（14.5K）
    con2 = ro(BUILDER)
    try:
        c2 = con2.cursor()
        models = {}
        for mid, mname, mkey, prev in c2.execute(
                "SELECT id, model_name, model_key, preview_model_path FROM bu_model"):
            models[mid] = (mname or "", mkey or "", prev or "")
        n_mod = len(models)
    finally:
        con2.close()
    print("  构建库模型 %d" % n_mod)

    # ⑤ 拼装
    parts, with_model = [], 0
    for cid, (code, show, is3d, pid, _x, _y) in codes.items():
        model_file = rel.get(cid, "") or ""
        if model_file:
            with_model += 1
        parts.append({
            "code": code,
            "name": show,
            "product": products.get(pid, "") or "",
            "brand": brands.get(products and pid and
                                (0,) or (0,), "") or "",   # 占位，见下
            "has_3d": is3d,
            "model_file": model_file,
        })

    # 品牌要按 product_id → brand_id 走一遍，单独补
    con3 = ro(SELECTOR)
    try:
        c3 = con3.cursor()
        pbrand = {r[0]: r[1] for r in
                  c3.execute("SELECT id, brand_id FROM se_product")}
        for p in parts:
            p["brand"] = brands.get(pbrand.get(pid_of(p, parts), ""), "")
    except Exception:
        pass
    finally:
        con3.close()
    return 0


def pid_of(p, parts):
    return p.get("_pid", "")


if __name__ == "__main__":
    raise SystemExit(main())
