# 037 · Tasks（全部完成，轮 118）

- [x] T-3301 写 `tools/probe_capability_coverage.py`
- [x] T-3302 ★ 第一版判据（模块名）⇒ 报 43 个 ⇒ 识别为**假阳性**
- [x] T-3303 ★ 第二版（函数名）⇒ 报 43 个（另一批）⇒ 仍不对
- [x] T-3304 ★ 第三版（并集）⇒ 38 个 ⇒ **停手**（事实 53）
- [x] T-3305 ★★ 定位真问题：**A1 的单位是域，不是文件**
- [x] T-3306 写 `docs/module-capability-coverage.md` + 探针源码带结论
  `→ 验收:` `Select-String docs\module-capability-coverage.md -Pattern '问错了问题'`
- [x] T-3307 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
