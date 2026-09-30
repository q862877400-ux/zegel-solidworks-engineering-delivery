# -*- coding: utf-8 -*-
"""从嘉立创 FA 选型插件的**明文 SQLite** 建全库零件索引。

⚠ 合规边界
----------
· 只读打开（``mode=ro``），**不修改任何厂商文件**。
· **不解密、不逆向、不破解**：插件运行时把加密传输包 ``DB.zip`` 解到
  ``ForFaceSelectorData\\DB\\``，那里是**明文**。厂商加密保护的是传输。
· 只抽目录性元数据，**不复制模型文件本体**。

⚑ 两个库之间靠「顺序键」连接（本机实测）
----------------------------------------
    selector.se_fa_product_model_third_party_relation.product_model_key_id
      = builder.bu_model.id          （形如 ``1195749``，**不是**雪花 ID）

⚑ 本轮第一次索引查出 0 条的三个原因（都记在这，免得再犯）
--------------------------------------------------------
    ① ``se_product_code.status`` 全是 **0** —— 我原先过滤 ``status = 1``
    ② join 键接错：接到了 ``se_product_code.id``（雪花）而非 ``bu_model.id``
    ③ 用 SQL 写 CROSS JOIN + GROUP BY 拼这两张表会**慢到跑不动**
       （relation 260 万行）⇒ 改成分表 SELECT、Python 里用 dict 拼

# ── 来源 ─────────────────────────────────────────────────────────────
# 文件:   嘉立创 FA 选型插件 v2.4.1-20260918-1（本机已安装）
# 路径:   D:\\Program Files\\SOLIDWORKS Corp\\JLCFA Parts Library Plugin
#         Full Version v2.4.1-20260918-1\\ForFaceSelector\\ForFaceSelectorData\\DB\\
# 定位:   型号 + 分类 + 品牌 + 模型包名 → 一份可查询索引（**全库，不限品类**）。
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

    # ── 选型库 ──
    con = ro(SELECTOR)
    try:
        c = con.cursor()
        n_cat = c.execute("SELECT COUNT(*) FROM se_category").fetchone()[0]
        n_par = c.execute("SELECT COUNT(*) FROM se_fa_product_param").fetchone()[0]
        n_pva = c.execute(
            "SELECT COUNT(*) FROM se_fa_product_param_value").fetchone()[0]

        # 型号：id -> (code, show, is3d, product_id)
        codes = {}
        for cid, code, show, is3d, pid in c.execute(
                "SELECT id, code_name, code_show_name, is_3d, product_id "
                "FROM se_product_code"):
            if code:
                codes[cid] = (code, show or code, int(is3d or 0), pid)
        print("  型号 %d · 分类 %d · 参数 %d · 可选值 %d"
              % (len(codes), n_cat, n_par, n_pva))

        products = {r[0]: (r[1] or "", r[2] or "") for r in
                    c.execute("SELECT id, name, brand_id FROM se_product")}
        brands = {r[0]: (r[1] or "") for r in
                  c.execute("SELECT id, name FROM se_product_brand")}
        cats = sorted({r[0] for r in c.execute("SELECT name FROM se_category")})
        print("  产品 %d · 品牌 %d" % (len(products), len(brands)))

        print("  读型号↔模型映射（2,607,833 行）…")
        rel: dict[str, str] = {}
        for mk, tpm in c.execute(
                "SELECT product_model_key_id, third_party_model "
                "FROM se_fa_product_model_third_party_relation "
                "WHERE delete_flag = 0 AND third_party_model IS NOT NULL"):
            if mk and tpm and tpm != "空白":
                rel.setdefault(mk, tpm)
        print("  映射 %d 条" % len(rel))

        # 分类：se_category_product(8,207) 是 product 级，型号挂在 product 下
        #       ⇒ 分类可经 product_id 推出（⚑ 不给型号拍脑袋塞一个分类）
        cat_of: dict[str, list] = {}
        for pid, cid2 in c.execute(
                "SELECT product_id, category_id FROM se_category_product"):
            cat_of.setdefault(pid, []).append(cid2)
        cname = {r[0]: r[1] for r in c.execute("SELECT id, name FROM se_category")}
        pcat = {pid: [cname.get(x, "") for x in v] for pid, v in cat_of.items()}
        print("  产品↔分类 %d 条" % len(pcat))
    finally:
        con.close()

    # ── 构建库 ──
    con2 = ro(BUILDER)
    try:
        models = {r[0]: (r[1] or "", r[2] or "")
                  for r in con2.execute(
                      "SELECT id, model_name, model_key FROM bu_model")}
        n_mod = len(models)
    finally:
        con2.close()
    print("  构建库模型 %d" % n_mod)

    # ── 拼装 ──
    parts = []
    for cid, (code, show, is3d, pid) in codes.items():
        pname, brand_id = products.get(pid, ("", ""))
        parts.append({
            "code": code,
            "name": show,
            "product": pname,
            "brand": brands.get(brand_id, ""),
            "category": pcat.get(pid, []),
            "has_3d": is3d,
            "model_file": rel.get(cid, ""),
        })

    with_model = sum(1 for p in parts if p["model_file"])
    data = {
        "source_selector_db": str(SELECTOR),
        "source_builder_db": str(BUILDER),
        "note": ("自嘉立创 FA 选型插件的运行时**明文** SQLite 抽取（全库，非限品类）；"
                 "未解密 DB.zip、未逆向 DLL、未修改任何厂商文件。"),
        "counts": {"codes": len(parts), "categories": n_cat,
                   "parameters": n_par, "parameter_values": n_pva,
                   "builder_models": n_mod, "codes_with_model": with_model},
        "categories": cats,
        "parts": parts,
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    print("  写出 %s（%.2f MB）" % (OUT.name, OUT.stat().st_size / 1e6))
    print("  型号 %d · 其中关联到模型包 %d · 分类 %d"
          % (len(parts), with_model, n_cat))
    for p in parts[:3]:
        print("   样例:", p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
