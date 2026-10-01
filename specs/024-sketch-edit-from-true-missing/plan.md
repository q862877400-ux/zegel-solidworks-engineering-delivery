# 024 · Plan

**不重造**：照 `023`（`sw_helix.py`）的模块形式与来源块写法。

## 步骤
1. 查 `sketch_chamfer` / `sketch_mirror` 是否真缺 ⇒ 确认缺
2. 两源取签名（反射 + swapi）⇒ 倒角 3 参一致；镜像 0 参一致
3. ★ 取枚举 `swSketchChamferType_e` ⇒ **发现两源冲突**（-1 vs 1）
4. ★ **按铁律 4 取出厂反射的 1**
5. 发现 `SketchChamfer` **已废弃** ⇒ 改走后继 `CreateChamfer`
6. 写 `scripts/sw_sketch_edit.py` + 契约测试（10 条）
7. 加 `capabilities.yaml` 条目（32 → 33）
8. 重生成地图/审计/digest + 同步数字 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| **枚举冲突随手取一个** | ★ 铁律 4 明文裁决 + 测试独立钉住 |
| 用已废弃的入口 | 官方文档明写 Obsolete ⇒ 走后继，且来源块记下原因 |
| 单位再出岔子 | 长度走 `mm()`；**官方未写单位的参数不做换算并声明** |
| 真机测试触发弹窗 | ★ 不做真机测试，等级写 `stitched` |
