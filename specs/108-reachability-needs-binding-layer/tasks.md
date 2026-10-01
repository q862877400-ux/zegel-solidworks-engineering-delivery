# 108 · Tasks（全部完成，轮 188）

- [x] T-10801 查后端可用性（`comtypes` ✓ / `sldworks.tlb` ✓ / PIA ✓）
- [x] T-10802 ★★★ comtypes 早绑定探针
  `→ 验收:` `python tools/probe_safearray_comtypes.py`
  （**QI 成功 · 同实例 PID 20456 · 往返未走通 · 无净收益**）
- [x] T-10803 ★★★ 读**类型库方法表**拿权威 `in/out` 签名
  `→ 验收:` `python -c "import comtypes.client as cc; I=getattr(cc.GetModule(r'D:/Program Files/SOLIDWORKS Corp/SOLIDWORKS/sldworks.tlb'),'ISafeArrayUtility'); [print(m[1], m[3]) for m in I._methods_[:3]]"`
- [x] T-10804 更正 `capabilities.yaml` 的 `backend_catalog` 里轮 186 的过强措辞
- [x] T-10805 事实 128
- [x] T-10806 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
