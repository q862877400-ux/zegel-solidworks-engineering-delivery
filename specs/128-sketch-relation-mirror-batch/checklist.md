# Checklist: 草图几何关系 + 镜像特征

- [x] 规则 1：两名都带 `solidworks_` 前缀（`solidworks_add_sketch_relation` / `solidworks_mirror_feature`）
- [x] 规则 2：无长度/角度参数（本批两名都不含）
- [x] 规则 3：无裸坐标
- [x] ★ 参数名与目标函数真名一致（`relation_type` / `feature_name` / `mirror_plane_name`）
- [x] ★ `relation_type` 的合法值**引自 docstring**（12 个），不是猜的
- [x] ★ 把「**基准面名随 UI 语言变**」的既有事实写进描述（不丢）
- [x] ★ **14 个逐条有归属**：本批 2 · A6（角度）2 · A8（坐标）6 · 规则 2 长度 4 · ★ **本来就坏 1（不挂）**
- [x] ★ **不挂已知坏的入口**（`insert_composite_curve`，事实 121/124）—— 哪怕它在规则上"干净"
- [x] 计数类测试同步更新（54→56 · 99→101）
- [x] 不声称真机验证
- [x] 特性目录写完不再改（Flow-forward）
