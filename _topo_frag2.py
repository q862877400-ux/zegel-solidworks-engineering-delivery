

def topology_constraints_report(study) -> dict[str, Any]:
    """★ 回**已建约束与控制**的可 JSON 化报告（★ 不回 COM 对象）。

    ★★ `list_topology_constraints_and_controls` 回的是 ``{kind: object|None}``（**含 COM 对象**）
      ⇒ MCP 回不了 ⇒ 本函数把它翻成**布尔 + 计数**（★ 那也是「取到了」这件事**可断言**的形态）。
    """
    return {"ok": True, "study_name": str(get_com_member(study, "Name") or ""),
            **_kinds_summary(study),
            "★": "ok 恒 True（这是纯读取入口）；★ 判据在 taken_count / kinds 上"}
