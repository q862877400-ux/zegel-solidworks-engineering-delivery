from pathlib import Path
p = Path(r"D:\AI\SW\build_jlcfa4.py")
s = p.read_text(encoding="utf-8")
s = s.replace('"SELECT product_key_id, category_key_id FROM se_category_product"',
              '"SELECT product_id, category_id FROM se_category_product"')
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("列名已改（category_id / product_id）")