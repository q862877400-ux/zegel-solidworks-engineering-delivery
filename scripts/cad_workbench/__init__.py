"""CAD 自动化交付工作台。"""
# ── 来源 ──
# 仓库:   本项目自身（2026-11-04 从 apps/desktop/cad_workbench/ 用 git mv 搬到 scripts/cad_workbench/）
# 文件:   scripts/cad_workbench/__init__.py
# 定位:   包初始化（cad_workbench 库的对外出口）。★ 桌面工作台（PySide6 界面 / React+Tauri 客户端）已删除；
#         这批库被 scripts/cad_studio.py、headless_cad_writer.py、headless_occt_service.py
#         与 12 个测试依赖，因此保留并迁到 scripts 层。
# 官方依据: 不适用（本项目内部库，不直接调 SolidWorks API）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────


__version__ = "0.1.0"
