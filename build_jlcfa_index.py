# -*- coding: utf-8 -*-
"""从嘉立创 FA 选型插件的**明文 SQLite** 建全库零件索引。

⚠ 合规边界（重要，先看）
------------------------
· 只读打开厂商数据库（``mode=ro``），**不修改任何厂商文件**。
· **不解密、不逆向、不破解** ``DB.zip`` ——
  插件运行时把加密传输包解到 ``ForFaceSelectorData\DB\``，那份是**明文**。
  本脚本只读明文目录。厂商的加密保护的是**传输**，不是运行时数据。
· 只抽「型号 / 分类 / 品牌 / 参数 / 模型包名」这类**目录性元数据**，
  不复制模型文件本体。

# ── 来源 ─────────────────────────────────────────────────────────────
# 文件:   嘉立创 FA 选型插件 v2.4.1-20260918-1（本机已安装）
# 路径:   D:\Program Files\SOLIDWORKS Corp\JLCFA Parts Library Plugin
#         Full Version v2.4.1-20260918-1\ForFaceSelector\ForFaceSelectorData\DB\
#         ├ sw-fa-prod-selector   2.90 GB  SQLite（49 张表，全量选型库）
#         └ sw-fa-prod-builder    105 MB   SQLite
# 定位:   把「型号」连同分类/品牌/参数/可选值/模型包名抽成一份可查询索引。
#   关键表（本机实测行数）：
#     se_product                          8,207  产品
#     se_product_code                    63,234  型号（★ 主键是 code_name）
#     se_fa_product_param               330,208  参数定义（直径/导程/轨宽…）
#     se_fa_product_param_value         447,527  每型号的参数可选值
#     se_fa_product_model_third_party_relation 2,607,833  ★ 型号→模型包名
#     se_category                           200  分类（导轨 3 / 型材 5 / 直线 7 …）
# 覆盖:   后续同级定义
# ⚠ 本脚本只读文件，不连接 SolidWorks（见 AGENTS.md）
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

DB_DIR = Path(
    r"D:\Program Files\SOLIDWORKS Corp\JLCFA Parts Library Plugin "
    r"Full Version v2.4.1-20260918-1\ForFaceSelector\ForFaceSelectorData\DB"
)
SELECTOR = DB_DIR / "sw-fa-prod-selector"
OUT = Path(r"C:\swprojects\sw-skill-fork\scripts\jlcfa_index.json")

SQL = """
SELECT  pc.code_name,
        pc.code_show_name,
        pc.is_3d,
        p.name,
        b.name,
        m.third_party_model
FROM        se_product_code AS pc
LEFT JOIN   se_product  AS p ON p.id  = pc.product_id
LEFT JOIN   se_product_brand AS b ON b.id = p.brand_id
LEFT JOIN   se_fa_product_model_third_party_relation AS m
            ON m.product_model_key_id = pc.id AND m.delete_flag = 0
WHERE       pc.status = 1
"""


def main() -> int:
    if not SELECTOR.is_file():
        print("[FATAL] 找不到选型库：%s" % SELECTOR)
        print("        请确认嘉立创 FA 选型插件已安装。")
        return 2
    con = sqlite3.connect("file:%s?mode=ro" % SELECTOR, uri=True)   # 只读
    try:
        cur = con.cursor()
        n_cat = cur.execute("SELECT COUNT(*) FROM se_category").fetchone()[0]
        n_par = cur.execute("SELECT COUNT(*) FROM se_fa_product_param").fetchone()[0]
        n_pva = cur.execute("SELECT COUNT(*) FROM se_fa_product_param_value").fetchone()[0]
        n_prod = cur.execute("SELECT COUNT(*) FROM se_product").fetchone()[0]

        print("  读 %s" % SELECTOR.name)
        print("    se_category=%d  se_product=%d  se_fa_product_param=%d  param_value=%d"
              % (n_cat, n_prod, n_par, n_pva))
        print("    扫描型号表（%d 行级）…" % 63234)
        rows = cur.execute(SQL)
        parts, seen = [], set()
        for code, show, is3d, pname, brand, model in rows:
            if not code:
                continue
            if code in seen:
                continue
            seen.add(code)
            parts.append({
                "code": code,
                "name": show or code,
                "product": pname or "",
                "brand": brand or "",
                "has_3d": int(is3d or 0),
                "model": model or "",
            })
        cats = {r[0]: r[1] for r in
                cur.execute("SELECT id, name FROM se_category")}

        data = {
            "source_db": str(SELECTOR),
            "note": ("自嘉立创 FA 选型插件的**运行时明文** SQLite 抽取；"
                     "未解密 DB.zip、未逆向 DLL、未修改任何厂商文件。"),
            "counts": {"categories": n_cat, "products": n_prod,
                       "parameters": n_par, "parameter_values": n_pva,
                       "codes": len(parts)},
            "categories": sorted(cats.values()),
            "parts": parts,
        }
        OUT.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        print("  写出 %s（%.1f MB）" % (OUT.name, OUT.stat().st_size / 1e6))
        print("  型号 %d 个 / 分类 %d 个 / 有 3D 的 %d 个"
              % (len(parts), len(cats), sum(1 for p in parts if p["has_3d"])))
        m = sum(1 for p in parts if p["model"])
        print("  关联到模型包名的 %d 个" % m)
        with3d = sum(1 for p in parts if p["model"] and p["has_3d"])
        print("  同时有 3D 与模型包的 %d 个" % with3d)
        return 0
    finally:
        con.close()          # 只读打开，读完立刻关


if __name__ == "__main__":
    raise SystemExit(main())
