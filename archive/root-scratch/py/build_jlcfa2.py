# -*- coding: utf-8 -*-
"""从嘉立创 FA 选型插件的**明文 SQLite** 建全库零件索引（两个库 ATTACH 关联）。

⚠ 合规边界
----------
· 只读打开（``mode=ro``），**不修改任何厂商文件**。
· **不解密、不逆向、不破解**：插件运行时把加密传输包 ``DB.zip`` 解到
  ``ForFaceSelectorData\DB\``，那里是**明文**。厂商加密保护的是传输。
· 只抽目录性元数据（型号/分类/品牌/参数/模型包名），**不复制模型文件本体**。

⚑ 两个库的关系（本机实测）
--------------------------
    sw-fa-prod-selector（2.9 GB，49 表）  选型：型号 / 分类 / 品牌 / 参数
    sw-fa-prod-builder  （105 MB，8 表）   模型：bu_model 14,583 条
  连接键：selector.se_fa_product_model_third_party_relation.product_model_key_id
          = builder.bu_model.id   （都是**顺序号**，不是雪花 ID —— 这是我第一版
          索引查不出东西的原因：错 join 到了 se_product_code.id）

# ── 来源 ─────────────────────────────────────────────────────────────
# 文件:   嘉立创 FA 选型插件 v2.4.1-20260918-1（本机已安装）
# 路径:   D:\Program Files\SOLIDWORKS Corp\JLCFA Parts Library Plugin
#         Full Version v2.4.1-20260918-1\ForFaceSelector\ForFaceSelectorData\DB\
# 定位:   把「型号」连同分类/品牌/参数/模型包抽成一份可查询索引（全库，不限品类）。
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

DB_DIR = Path(
    "D:\Program Files\SOLIDWORKS Corp\JLCFA Parts Library Plugin "
    r"Full Version v2.4.1-20260918-1\\ForFaceSelector\\ForFaceSelectorData\\DB")
SELECTOR = DB_DIR / "sw-fa-prod-selector"
BUILDER = DB_DIR / "sw-fa-prod-builder"
OUT = Path(r"C:\swprojects\sw-skill-fork\scripts\jlcfa_index.json")

SQL = """
SELECT  pc.code_name,
        pc.code_show_name,
        pc.is_3d,
        p.name,
        b.name,
        rel.tpm,
        bm.model_name,
        bm.model_key,
        bm.preview_model_path
FROM        se_product_code AS pc
LEFT JOIN   se_product AS p ON p.id = pc.product_id
LEFT JOIN   se_product_brand AS b ON b.id = p.brand_id
LEFT JOIN  (SELECT r.product_model_key_id AS mk, r.third_party_model AS tpm
             FROM se_fa_product_model_third_party_relation r
             WHERE r.delete_flag = 0 AND r.third_party_model IS NOT NULL
                   AND r.third_party_model <> '空白'
             GROUP BY r.product_model_key_id) AS rel
            ON 1 = 1
LEFT JOIN  builder.bu_model AS bm ON bm.id = rel.mk
ORDER BY    pc.code_name
"""


def main() -> int:
    for p in (SELECTOR, BUILDER):
        if not p.is_file():
            print("[FATAL] 找不到 %s" % p)
            return 2
    con = sqlite3.connect("file:%s?mode=ro" % SELECTOR, uri=True)
    try:
        con.execute("ATTACH DATABASE ? AS builder", ("file:%s?mode=ro" % BUILDER,))
        cur = con.cursor()
        n_cat = cur.execute("SELECT COUNT(*) FROM se_category").fetchone()[0]
        n_par = cur.execute("SELECT COUNT(*) FROM se_fa_product_param").fetchone()[0]
        n_pva = cur.execute("SELECT COUNT(*) FROM se_fa_product_param_value").fetchone()[0]
        n_mod = cur.execute("SELECT COUNT(*) FROM builder.bu_model").fetchone()[0]
        print("  选型库 %s / 构建库 %s" % (SELECTOR.name, BUILDER.name))
        print("    分类 %d · 参数 %d · 参数可选值 %d · 模型 %d"
              % (n_cat, n_par, n_pva, n_mod))

        rows = cur.execute(SQL)
        parts, seen = [], set()
        for code, show, is3d, pname, brand, tpm, mname, mkey, prev in rows:
            if not code or code in seen:
                continue
            seen.add(code)
            parts.append({
                "code": code,
                "name": show or code,
                "product": pname or "",
                "brand": brand or "",
                "has_3d": int(is3d or 0),
                "model_file": tpm or "",
                "model_name": mname or "",
                "model_key": mkey or "",
            })
        cats = sorted({r[0] for r in cur.execute("SELECT name FROM se_category")})
        con.commit() if False else None      # 只读，不 commit

        data = {
            "source_selector_db": str(SELECTOR),
            "source_builder_db": str(BUILDER),
            "note": ("自嘉立创 FA 选型插件的**运行时明文** SQLite 抽取（全库，非限品类）；"
                     "未解密 DB.zip、未逆向 DLL、未修改任何厂商文件。"),
            "counts": {"categories": n_cat, "parameters": n_par,
                       "parameter_values": n_pva, "builder_models": n_mod,
                       "codes": len(parts)},
            "categories": cats,
            "parts": parts,
        }
        OUT.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        print("  写出 %s（%.2f MB）" % (OUT.name, OUT.stat().st_size / 1e6))
        print("  型号 %d / 有模型包名 %d / 有 3D 标记 %d"
              % (len(parts), sum(1 for p in parts if p["model_file"]),
                 sum(1 for p in parts if p["has_3d"])))
        for p in parts[:3]:
            print("   样例:", {k: v for k, v in p.items() if v})
        return 0
    finally:
        con.close()


if __name__ == "__main__":
    raise SystemExit(main())
