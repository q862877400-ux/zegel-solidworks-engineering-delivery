# Checklist: 仿真研究族

- [x] 规则 1：三名都带 `solidworks_` 前缀
- [x] 规则 2：无长度参数（本批 `units` 是枚举、`path` 是路径）
- [x] 规则 3：无裸坐标
- [x] ★ 参数名与目标函数真名一致（`template` / `path` / `append` / `control_name` / `units`）
- [x] ★ **查不到的**（`template` 取值）如实标注 + 附核查命令
- [x] ★ **两源冲突**（`units=-1`）**原样保留、不合并**
- [x] ★ **归属按实测改正**（`default_element_size_and_tolerance` 在 `sw_simulation` 不是 `_study`）
- [x] 计数类测试同步更新
- [x] 不声称真机验证
- [x] 特性目录写完不再改（Flow-forward）
