"""Prompt templates for exercise generation and scoring.

All prompts are parameterized by language so the same templates work for
Python, Java, Go, JavaScript, etc. The `language_label` (e.g. "Python")
is a human-readable form used in prompt text; the `language` slug
(e.g. "python") is the DB enum.
"""
from __future__ import annotations

import json
from typing import Dict, List

from app.models import KnowledgePoint
from app.schemas.common import (
    DIFFICULTY_DESC,
    QUESTION_TYPE_DESC,
    Difficulty,
    QuestionType,
)


# Human-readable label per language slug. Add new entries when extending.
LANGUAGE_LABELS: Dict[str, str] = {
    "python": "Python",
    "java": "Java",
    "go": "Go",
    "javascript": "JavaScript",
}

# Language-specific notes injected into the system prompt.
LANGUAGE_NOTES: Dict[str, str] = {
    "python": "使用 Python 3.10+ 语法。",
    "java": "使用 Java 17+ 语法。代码需要写成可编译的完整片段（含 main 方法或必要的类骨架）。",
    "go": "使用 Go 1.21+ 语法。代码需要写成可编译的完整 package main + main 函数片段（如适用）。",
    "javascript": "使用 ES2022+ 语法。如需运行环境请明确说明（浏览器或 Node.js）。",
}


def language_label(language: str) -> str:
    return LANGUAGE_LABELS.get(language, language.title())


def _system_prompt(language: str) -> str:
    label = language_label(language)
    note = LANGUAGE_NOTES.get(language, "")
    return f"""你是一名资深 {label} 教学专家与出题专家。你的任务是根据指定知识点、难度和题型，生成一道高质量、可直接用于教学的 {label} 练习题。

要求：
1. 题目必须严格围绕给定知识点，不偏题；
2. 题目难度必须与给定难度等级匹配；
3. 输出必须是合法 JSON，且只输出 JSON，不要任何解释、Markdown 代码块标记；
4. 所有字段都必须填写；如果某字段对当前题型不适用，填空字符串 ""；
5. 代码中如果有中文符号，必须替换为英文符号；
6. 测试用例必须真实可运行，期望输出必须正确；
7. {note}
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
    language: str,
    existing_titles: list[str] | None = None,
) -> str:
    keywords = _parse_keywords(kp.keywords)
    keywords_text = "、".join(keywords) if keywords else "（未提供）"
    diff_desc = DIFFICULTY_DESC.get(difficulty, "")
    qt_desc = QUESTION_TYPE_DESC.get(question_type, "")
    label = language_label(language)

    avoid_block = ""
    if existing_titles:
        bullet_list = "\n".join(f"- {t}" for t in existing_titles)
        avoid_block = f"""

【避免重复】请勿生成与以下已有题目重复或过于相似的题目（标题和考点都要避免雷同）：
{bullet_list}
"""

    return f"""请生成一道 {label} 练习题，要求如下：

【语言】{label}
【章节】{chapter_title}
【知识点】{kp.title}（编号 {kp.code}）
【知识点关键词】{keywords_text}
【知识点描述】{kp.description or '（未提供）'}
【难度】{difficulty.value}（{diff_desc}）
【题型】{question_type.value}（{qt_desc}）{avoid_block}

请按以下 JSON 格式严格输出：

{JSON_TEMPLATE}

只输出 JSON，不要任何额外文字。"""


def build_messages(
    *,
    kp: KnowledgePoint,
    chapter_title: str,
    difficulty: Difficulty,
    question_type: QuestionType,
    language: str,
    existing_titles: list[str] | None = None,
) -> List[dict]:
    return [
        {"role": "system", "content": _system_prompt(language)},
        {
            "role": "user",
            "content": render_user_prompt(
                kp=kp,
                chapter_title=chapter_title,
                difficulty=difficulty,
                question_type=question_type,
                language=language,
                existing_titles=existing_titles,
            ),
        },
    ]


# ==========================================================================
# Learning content (markdown teaching material per knowledge point)
# ==========================================================================


def _learning_content_system_prompt(language: str) -> str:
    label = language_label(language)
    note = LANGUAGE_NOTES.get(language, "")
    return f"""你是一名资深 {label} 教师。请为指定的知识点编写一篇详细的学习材料，帮助学习者从零理解这个知识点。

要求：
1. **直接输出 Markdown**——不要任何前置解释、不要包裹在 ```markdown ... ``` 里
2. 结构包含但不限于（按需自由组织标题层级）：
   - 概念定义（这个东西是什么）
   - 语法要点（怎么写）
   - 代码示例（**至少 2 段**可运行的代码）
   - 常见用法 / 应用场景
   - 易错点 / 注意事项
3. 代码块用 ```{language} 围栏包裹（语言标签很重要，前端会做语法高亮）
4. 控制在 600-1500 字之间
5. {note}
6. 用学习者友好的口吻，避免堆术语；关键术语首次出现可以括号附英文
"""


def render_learning_user_prompt(
    *,
    kp: KnowledgePoint,
    chapter_title: str,
    language: str,
) -> str:
    keywords = _parse_keywords(kp.keywords)
    keywords_text = "、".join(keywords) if keywords else "（未提供）"
    label = language_label(language)
    return f"""请为以下 {label} 知识点撰写学习材料：

【章节】{chapter_title}
【知识点】{kp.title}（编号 {kp.code}）
【知识点关键词】{keywords_text}
【知识点简介】{kp.description or '（未提供）'}

直接输出 Markdown 内容，不要任何额外文字。"""


def build_learning_messages(
    *,
    kp: KnowledgePoint,
    chapter_title: str,
    language: str,
) -> List[dict]:
    return [
        {"role": "system", "content": _learning_content_system_prompt(language)},
        {
            "role": "user",
            "content": render_learning_user_prompt(
                kp=kp, chapter_title=chapter_title, language=language,
            ),
        },
    ]


# ==========================================================================
# Scoring (quality evaluation of an existing exercise)
# ==========================================================================


def _score_system_prompt(language: str) -> str:
    label = language_label(language)
    return f"""你是一名严格的 {label} 教学评审专家。你的任务是评估一道 {label} 练习题的整体质量，给出 1-10 分（可保留一位小数）的多维评分和总评。

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
    language: str,
) -> str:
    label = language_label(language)
    return f"""请对以下 {label} 练习题打分。

【语言】{label}
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
    language: str,
) -> List[dict]:
    return [
        {"role": "system", "content": _score_system_prompt(language)},
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
                language=language,
            ),
        },
    ]
