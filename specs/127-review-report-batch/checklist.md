# Checklist: 结构化审查报告

- [x] 规则 1：工具名 `solidworks_build_review_report`（`solidworks_` 前缀）
- [x] 规则 2：无长度/角度参数（`output_dir` 是路径、`basename` 是前缀）
- [x] 规则 3：无裸坐标
- [x] ★ 参数名与目标函数真名一致（`output_dir` / `basename`）
- [x] ★ **可选的 `list` 型参数不暴露**，并在描述里**指向理由**（批头）
- [x] ★ 两条核查命令**都排除了本批产物**（事实 147 的定则）
- [x] ★ **挂不了的**（`activate_plot`）写明理由与去处（A10），不硬挂
- [x] 计数类测试同步更新（53→54 · 98→99）
- [x] 不声称真机验证
- [x] 特性目录写完不再改（Flow-forward）
