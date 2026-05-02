"""Prompt templates for exercise generation."""
from __future__ import annotations

import json
from typing import List

from app.models import KnowledgePoint
from app.schemas.common import (
    DIFFICULTY_DESC,
    QUESTION_TYPE_DESC,
    Difficulty,
    QuestionType,
)

SYSTEM_PROMPT = """\
你是一名资深 Python 教学专家与出题专家。你的任务是根据指定知识点、难度和题型，生成一道高质量、可直接用于教学的 Python 练习题。

要求：
1. 题目必须严格围绕给定知识点，不偏题；
2. 题目难度必须与给定难度等级匹配；
3. 输出必须是合法 JSON，且只输出 JSON，不要任何解释、Markdown 代码块标记；
4. 所有字段都必须填写；如果某字段对当前题型不适用，填空字符串 ""；
5. 代码中如果有中文符号，必须替换为英文符号；
6. 测试用例必须真实可运行，期望输出必须正确；
7. 使用 Python 3.10+ 语法。
"""


JSON_TEMPLATE = """\
{
  "title": "题目标题（不超过 30 字）",
  "description": "题目描述（题干，可包含背景）",
  "example_input": "示例输入（无则填空字符串）",
  "example_output": "示例输出（无则填空字符串）",
  "hint": "解题提示（指向方法，不要直接给答案）",
  "standard_answer": "标准答案",
  "reference_code": "参考代码（完整可运行）",
  "test_cases": [
    {"input": "输入1", "expected_output": "期望输出1"},
    {"input": "输入2", "expected_output": "期望输出2"}
  ],
  "explanation": "详细解析，讲清楚思路和涉及的知识点",
  "common_mistakes": "学习者在该题上常犯的错误（列 2-3 条）",
  "extra": {}
}\
"""


def _parse_keywords(raw: str) -> List[str]:
    if not raw:
        return []
    try:
        v = json.loads(raw)
        return v if isinstance(v, list) else []
    except json.JSONDecodeError:
        return []


def render_user_prompt(
    *,
    kp: KnowledgePoint,
    chapter_title: str,
    difficulty: Difficulty,
    question_type: QuestionType,
) -> str:
    keywords = _parse_keywords(kp.keywords)
    keywords_text = "、".join(keywords) if keywords else "（未提供）"
    diff_desc = DIFFICULTY_DESC.get(difficulty, "")
    qt_desc = QUESTION_TYPE_DESC.get(question_type, "")
    return f"""请生成一道 Python 练习题，要求如下：

【章节】{chapter_title}
【知识点】{kp.title}（编号 {kp.code}）
【知识点关键词】{keywords_text}
【知识点描述】{kp.description or '（未提供）'}
【难度】{difficulty.value}（{diff_desc}）
【题型】{question_type.value}（{qt_desc}）

请按以下 JSON 格式严格输出：

{JSON_TEMPLATE}

只输出 JSON，不要任何额外文字。"""


def build_messages(
    *,
    kp: KnowledgePoint,
    chapter_title: str,
    difficulty: Difficulty,
    question_type: QuestionType,
) -> List[dict]:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": render_user_prompt(
                kp=kp,
                chapter_title=chapter_title,
                difficulty=difficulty,
                question_type=question_type,
            ),
        },
    ]


# ==========================================================================
# Scoring (quality evaluation of an existing exercise)
# ==========================================================================

SCORE_SYSTEM_PROMPT = """\
你是一名严格的 Python 教学评审专家。你的任务是评估一道 Python 练习题的整体质量，给出 1-10 分（可保留一位小数）的多维评分和总评。

要求：
1. 客观、严格，不要为了讨好作者打高分；
2. 输出必须是合法 JSON，且只输出 JSON，不要任何解释、Markdown 代码块标记；
3. 所有维度都给分，缺失的字段给较低分；
4. 评语用中文，简短直接，指出具体问题或亮点。
"""


SCORE_JSON_TEMPLATE = """\
{
  "overall": 8.5,
  "scores": {
    "clarity": 9,
    "correctness": 8,
    "difficulty_match": 8,
    "educational_value": 9
  },
  "comment": "题目清晰、代码可运行；但易错点列得太抽象，建议补充具体边界值示例。"
}\
"""


def _format_test_cases(test_cases: list) -> str:
    if not test_cases:
        return "（无）"
    out = []
    for i, tc in enumerate(test_cases, start=1):
        if isinstance(tc, dict):
            out.append(
                f"  {i}. 输入: {tc.get('input', '')!r} → 期望: {tc.get('expected_output', '')!r}"
            )
    return "\n".join(out) if out else "（无）"


def render_score_user_prompt(
    *,
    title: str,
    chapter_title: str,
    kp_title: str,
    difficulty: str,
    question_type: str,
    description: str,
    standard_answer: str,
    reference_code: str,
    test_cases: list,
    explanation: str,
    common_mistakes: str,
) -> str:
    return f"""请对以下 Python 练习题打分。

【知识点】{chapter_title} / {kp_title}
【请求难度】{difficulty}
【题型】{question_type}
【题目标题】{title}

【题目描述】
{description or '（无）'}

【标准答案】
{standard_answer or '（无）'}

【参考代码】
{reference_code or '（无）'}

【测试用例】
{_format_test_cases(test_cases)}

【解析】
{explanation or '（无）'}

【易错点】
{common_mistakes or '（无）'}

评分维度（每项 1-10 分，可保留一位小数）：
- clarity（清晰度）：题干是否表述清楚、无歧义
- correctness（正确性）：标准答案与参考代码是否真的可运行、能解决问题；测试用例是否真实合理
- difficulty_match（难度匹配）：实际难度是否与「请求难度」一致
- educational_value（教学价值）：是否能让学习者掌握该知识点；解析与易错点是否有帮助

请按以下 JSON 格式严格输出：

{SCORE_JSON_TEMPLATE}

只输出 JSON，不要任何额外文字。"""


def build_score_messages(
    *,
    title: str,
    chapter_title: str,
    kp_title: str,
    difficulty: str,
    question_type: str,
    description: str,
    standard_answer: str,
    reference_code: str,
    test_cases: list,
    explanation: str,
    common_mistakes: str,
) -> List[dict]:
    return [
        {"role": "system", "content": SCORE_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": render_score_user_prompt(
                title=title,
                chapter_title=chapter_title,
                kp_title=kp_title,
                difficulty=difficulty,
                question_type=question_type,
                description=description,
                standard_answer=standard_answer,
                reference_code=reference_code,
                test_cases=test_cases,
                explanation=explanation,
                common_mistakes=common_mistakes,
            ),
        },
    ]

