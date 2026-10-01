"""清掉本轮冒烟时我自己造的空件（只关**无路径**的自动命名零件）。

⚠ 判据**故意收紧**：只关「标题形如 `零件<N>` 且**路径为空**（从未保存）」的文档 ——
   那必然是 `new_document` 造出来的；**绝不碰**任何有路径的文档（用户的数据）。
"""
import re, sys
sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")
import sw_connect

sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
docs = sw_connect.safe_get_com_member(sw, "GetDocuments") or ()
print("打开的文档 %d 个:" % len(docs))
mine = []
for d in docs:
    title = str(sw_connect.safe_get_com_member(d, "GetTitle") or "")
    path = str(sw_connect.safe_get_com_member(d, "GetPathName") or "")
    auto = bool(re.fullmatch(r"(零件|Part)\d+", title)) and not path
    print("   %-26s 路径=%r  %s" % (title, path, "← 我造的（待关）" if auto else ""))
    if auto:
        mine.append((title, d))

print()
if not mine:
    print("  没有需要清理的。")
else:
    for title, d in mine:
        try:
            d.Close(False)      # False = 不保存
            print("   已关闭 %s（不保存）" % title)
        except Exception as exc:      # noqa: BLE001
            print("   ✗ 关闭 %s 失败：%s" % (title, exc))
    left = sw_connect.safe_get_com_member(sw, "GetDocuments") or ()
    print("   剩余文档 %d 个: %s" % (len(left),
          [str(sw_connect.safe_get_com_member(x, "GetTitle") or "") for x in left]))
