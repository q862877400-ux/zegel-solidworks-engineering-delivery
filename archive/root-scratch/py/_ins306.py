import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           306 🎯 **Spec Kit `046`：补 `bbox` —— 数值冒烟抓到一处单位错，并查出一条与其它接口不同的单位**（轮 127）——
               挑它是因为**可以用精确数字验证**：建一个**已知尺寸**的盒子再量。
            307 ★★ **先读官方文档，改掉了我原本的判据**：
               ```
               我原本：「建 80×60×50 的盒子 ⇒ size 应当**完全等于** [80,60,50]」
               ★ 读了 IMPORTANT 段才发现该值是 **approximate**、**不应用于比较**
               ⇒ 判据改成「**容差内**」，并**专门去量偏差是多少**（那才是这轮真正想知道的）
               ```
               ★ 按原计划写死"完全相等"，将来任何浮点误差都会让它红 ——
                 而那**不是 bug**，是**把官方的警告当成了精度承诺**。
            308 ★ 数值冒烟：**先 7/8，修完 8/8**
               ```
               ✗ NameError: name 'mm' is not defined          ← 第 1 处（mm 只在文档串示例里出现过）
               ✗ size got=[0.05,0.06,0.08] want=[50,60,80]     ← 第 2 处
                   真因：**把 `mm()` 用在了输出上**（它是**输入方向**：毫米→米）
               ⇒ 修完：size=[80.0, 60.0, 50.0]，**偏差 0.00e+00**
               ```
            309 ★★ **顺手查出一条与其它几何接口不同的单位**：直读 COM ⇒
               `GetBodyBox` 原始返回 `[0.0, 0.0, -50.0, 80.0, 60.0, 0.0]`
               ⇒ **原始值就是 80/60/50 ⇒ 单位是毫米**（不是惯用的米）。⚠ 官方**没写单位**。
            310 ★★★ **本轮最微妙的一点：官方说「近似」，实测偏差却是 0** ——
               ```
               实测只证：「**这一个盒子、这一次**」的偏差是 0
               官方说的是：「**不要依赖它**」+「重建后**可能变**」
               ⇒ ★ **一个有界样本，压不过一条适用范围声明。**
               ```
               ★ 与 `035`/`036`/`040`/`043` 的"往返一致"同族但**更进一层**：
                 那些是**强证据**，而强证据**也有它的适用域** —— 本轮就是
                 「**证据成立、但不能外推**」的实例。官方的 approximate 原文已**照抄进源码**。
               ⚑ 三个小坑（都当场修）：① `mm` 导入问题 —— ★ **正确做法是撤回导入**
                 （单位修正后不需要它），**不是去改测试的桩来迁就代码**；
                 ② 我加的测试用了 `pytest`+`REPO_ROOT`，而该文件用 `unittest`+`ROOT`；
                 ③ 判据切片从 `def` 开始 ⇒ 取不到**来源块里**的官方原文 ⇒ 往前扩。
               ⚠ 限度：只测 **1 个盒子**；旋转体/多实体/装配体未测；**重建后是否真会变未测**；
                 **没有**注册成 MCP 工具。已知事实 **71** 入库 · 回归 **1133 passed**。
               下轮候选：① 继续补「真缺」；② 给剩下 3 条 `stitched` 冒烟；
               ③ 把查到的 API 注册成 MCP 工具（这批已经攒了 5 个可用入口）。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+306 ", before, re.M):
    print("  游标 306 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+310 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 310 行已存在 ✓")
