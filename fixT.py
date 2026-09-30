import sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
p = Path(r"C:\swprojects\sw-skill-fork\SKILL.md")
lines = p.read_text(encoding="utf-8").splitlines()
# 279..312（1-based）整段替换
s = 278; e = 312
NEW = '''官方 API 清单速查（**「收录」= 名字与参数个数已抄进官方 API 索引，可直接调用**）：

| 判据 | 实测 |
|---|---|
| 收录程序集 | **12** 个 |
| 接口族 | **792** |
| 成员 | **15,466** |
| 编入官方 API 索引 | **15,466 / 15,466 = 100%** |
| 未编入的族 | **0** |

本机实装 **18** 个 interop 程序集（合计 1,804 个接口），收录 12 个；
未收录的 3 个是明确排除的（`sustainability` 绿色设计 / `sw3dprinter` 3D 打印 /
`swbrowser` PDM 浏览器），另 `swconst` 只有枚举（已单独收录字面值）、
`swcommands` 实测 0 个接口。

12 份索引一览：

| 索引 | 族 | 能力 | 是什么 |
|---|---|---|---|
| `sw_api_sldworks.py` | 523 | 8,210 | 主体：零件 / 装配 / 工程图 / 草图 / 钣金 / 焊件 |
| `sw_api_swdocumentmgr.py` | 138 | 2,524 | Enterprise PDM（需许可） |
| `sw_api_cosworks.py` | 84 | 1,235 | Simulation 仿真（需许可） |
| `sw_api_swdimxpert.py` | 51 | 136 | 尺寸标注自动化 / GD&T 公差 |
| `sw_api_swpublished.py` | 31 | 354 | 加载项框架（属性管理页回调、消息栏） |
| `sw_api_SWRoutingLib.py` | 14 | 87 | Routers 线缆路由（需许可） |
| `sw_api_sldcostingapi.py` | 14 | 81 | Composer / Costing（需许可） |
| `sw_api_swmotionstudy.py` | 11 | 81 | 机构运动仿真（需许可） |
| `sw_api_gtswutilities.py` | 11 | 120 | 几何分析 / 壁厚分析 / 图档比较 |
| `sw_api_sldtoolboxconfigureaddin.py` | 2 | 5 | Toolbox 配置 |
| `sw_api_fworks.py` | 1 | 7 | Factory / 辅助 |
| `sw_api_dsgnchk.py` | 1 | 19 | Design Checker 设计检查器 |

怎么用（**只有一种走法，全用官方名**）：

```python
call_index(对象, "族名", "成员名", *参数)
```

例：

```python
call_index(特征管理器, "IFeatureManager", "FeatureCut4", x1, x2, ..., x27)
```

三处口径（各索引的 docstring 里都写明）：

- **成员名用 COM 名** —— 反射里 `get_CustomPropertyManager` 的 COM 名是
  `CustomPropertyManager`；⚠ 传 `GetXxx`（大写 G）**谁都不认**
- **arity = 调用方要传的实参，排除 by-ref 出参** ——
  ⚠ `GetErrorMessages(Object&, Object&, Object&)` 是 **0 参**，三个全是 [out]
- **不收 COM 内部分发口** —— `IGetXxx` / `IUpdateYyy` 是同一能力的内部变体

> ⚠ 域 13/14 需要**独立许可产品**（Simulation / Routers / Composer / Enterprise PDM），
> 本机**均未安装**，加载项 ProgID 与取用链**查不到**——
> 相关入口一律**接收调用方传入的对象**，不代为连接。
> 逐族明细见 `docs/family-coverage.md`；口径讨论见 `docs/gap-analysis.md`。'''
out = lines[:s] + NEW.splitlines() + lines[e:]
p.write_text("\n".join(out) + "\n", encoding="utf-8")
print("  [ok] SKILL.md 覆盖小节已整段重写")