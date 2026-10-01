# Checklist: 静力学真机复验

- [x] **单实例** COM（事实 24）
- [x] 收尾：`CommandInProgress=False` + 点掉残留弹窗 + 脚本自建文档自行关闭
- [x] ★ **成功判据是 `Results` 非空 + 图数**，不是 `RunAnalysis` 返回码（该 JSON 自标 `false`）
- [x] ★ **不声称**"求解器不收敛"已解决（那是另一件事）
- [x] 不改任何代码（本特性只取证据）
- [x] 特性目录写完**不再改**（Flow-forward）
