from pathlib import Path
p = Path(r"D:\AI\SW\build_jlcfa2.py")
s = p.read_text(encoding="utf-8")
old = """LEFT JOIN   se_fa_product_model_third_party_relation AS rel
            ON rel.product_model_key_id = bm.id AND rel.delete_flag = 0
LEFT JOIN   bu_model AS bm ON bm.id = rel.product_model_key_id"""
new = """LEFT JOIN   bu_model AS bm ON 1 = 0
LEFT JOIN   se_fa_product_model_third_party_relation AS rel
            ON rel.product_model_key_id = bm.id AND rel.delete_flag = 0"""
# 上面只是占位；正确做法：先 join bu_model（用 relation 指向），需交叉子查询
new = """LEFT JOIN  (SELECT r.product_model_key_id AS mk, r.third_party_model AS tpm
             FROM se_fa_product_model_third_party_relation r
             WHERE r.delete_flag = 0 AND r.third_party_model IS NOT NULL
                   AND r.third_party_model <> '空白'
             GROUP BY r.product_model_key_id) AS rel
            ON 1 = 1
LEFT JOIN  builder.bu_model AS bm ON bm.id = rel.mk"""
assert old in s
s = s.replace(old, new, 1)
# 补 SELECT 里的 rel.tpm
s = s.replace("rel.third_party_model,\n        bm.model_name,", "rel.tpm,\n        bm.model_name,")
# 去掉 r"" 的转义警告
s = s.replace('DB_DIR = Path(\n    r"', 'DB_DIR = Path(\n    "').replace(
    'Full Version v2.4.1-20260918-1\\ForFaceSelector\\ForFaceSelectorData\\DB"\n)',
    'Full Version v2.4.1-20260918-1\\\\ForFaceSelector\\\\ForFaceSelectorData\\\\DB")')
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("  SQL 顺序已改")