"""Export service: dump exercises to JSON or Markdown."""
from __future__ import annotations

import json
from io import StringIO
from typing import List

from sqlalchemy.orm import Session

from app.crud import knowledge_point as crud_kp
from app.models import Exercise


def _parse(value: str, default):
    if not value:
        return default
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default


def _serialize_exercise(db: Session, ex: Exercise) -> dict:
    kp = crud_kp.get_kp(db, ex.knowledge_point_id)
    chapter_title = kp.chapter.title if kp and kp.chapter else ""
    kp_title = kp.title if kp else ""
    return {
        "id": ex.id,
        "title": ex.title,
        "chapter": chapter_title,
        "knowledge_point": kp_title,
        "knowledge_point_id": ex.knowledge_point_id,
        "difficulty": ex.difficulty,
        "question_type": ex.question_type,
        "description": ex.description,
        "example_input": ex.example_input,
        "example_output": ex.example_output,
        "hint": ex.hint,
        "standard_answer": ex.standard_answer,
        "reference_code": ex.reference_code,
        "test_cases": _parse(ex.test_cases, []),
        "explanation": ex.explanation,
        "common_mistakes": ex.common_mistakes,
        "extra": _parse(ex.extra, {}),
        "status": ex.status,
        "created_at": ex.created_at.isoformat() if ex.created_at else "",
    }


def export_json(db: Session, exercises: List[Exercise]) -> str:
    payload = [_serialize_exercise(db, ex) for ex in exercises]
    return json.dumps(payload, ensure_ascii=False, indent=2)


# --- Markdown helpers --------------------------------------------------------

DIFFICULTY_LABEL = {
    "entry": "入门",
    "basic": "基础",
    "intermediate": "中级",
    "advanced": "进阶",
    "comprehensive": "综合",
}

QTYPE_LABEL = {
    "choice": "选择题",
    "fill": "填空题",
    "judge": "判断题",
    "read": "代码阅读题",
    "complete": "代码补全题",
    "program": "编程实现题",
    "debug": "Debug 修错题",
}


def _md_section(buf: StringIO, ex: dict) -> None:
    buf.write(f"## {ex['title']}\n\n")
    buf.write(
        f"- **知识点**：{ex['chapter']} / {ex['knowledge_point']}\n"
        f"- **难度**：{DIFFICULTY_LABEL.get(ex['difficulty'], ex['difficulty'])}\n"
        f"- **题型**：{QTYPE_LABEL.get(ex['question_type'], ex['question_type'])}\n\n"
    )
    if ex["description"]:
        buf.write(f"### 题目描述\n\n{ex['description']}\n\n")
    if ex["example_input"] or ex["example_output"]:
        buf.write("### 示例\n\n")
        if ex["example_input"]:
            buf.write(f"**输入**：\n\n```\n{ex['example_input']}\n```\n\n")
        if ex["example_output"]:
            buf.write(f"**输出**：\n\n```\n{ex['example_output']}\n```\n\n")
    if ex["hint"]:
        buf.write(f"### 提示\n\n{ex['hint']}\n\n")
    if ex["standard_answer"]:
        buf.write(f"### 标准答案\n\n{ex['standard_answer']}\n\n")
    if ex["reference_code"]:
        buf.write(f"### 参考代码\n\n```python\n{ex['reference_code']}\n```\n\n")
    if ex["test_cases"]:
        buf.write("### 测试用例\n\n")
        for i, tc in enumerate(ex["test_cases"], start=1):
            buf.write(
                f"{i}. 输入：`{tc.get('input','')}` → 期望输出：`{tc.get('expected_output','')}`\n"
            )
        buf.write("\n")
    if ex["explanation"]:
        buf.write(f"### 解析\n\n{ex['explanation']}\n\n")
    if ex["common_mistakes"]:
        buf.write(f"### 易错点\n\n{ex['common_mistakes']}\n\n")
    buf.write("---\n\n")


def export_markdown(db: Session, exercises: List[Exercise]) -> str:
    buf = StringIO()
    buf.write("# Python 练习题题库\n\n")
    buf.write(f"共 {len(exercises)} 道题。\n\n---\n\n")
    for ex in exercises:
        _md_section(buf, _serialize_exercise(db, ex))
    return buf.getvalue()
