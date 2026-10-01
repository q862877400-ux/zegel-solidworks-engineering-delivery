# 027 · Tasks（全部完成，轮 108）

- [x] T-2301 写 `tools/probe_enum_assembly_coverage.py`（只读）
  `→ 验收:` `python tools/probe_enum_assembly_coverage.py`
- [x] T-2302 ★ 首跑 16 条"未覆盖" ⇒ 识别出**枚举类型名被误判**
- [x] T-2303 ★ 收紧后再跑 ⇒ 剔掉自有名 ⇒ 只剩 **4 条噪声**
- [x] T-2304 结论：**现有 17 份转储已覆盖全部用到的成员**
- [x] T-2305 ★ 查出 `swExportPDFData` 官方真名是 **`swExportPdfData`** ⇒ 更正
- [x] T-2306 补函数体内来源块（溯源门禁要求）
  `→ 验收:` `python scripts/check_provenance.py`（exit 0）
- [x] T-2307 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
