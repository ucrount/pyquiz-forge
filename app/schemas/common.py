"""Common enums and shared schemas."""
from enum import Enum
from typing import Generic, List, TypeVar

from pydantic import BaseModel, Field


class Difficulty(str, Enum):
    entry = "entry"               # 入门
    basic = "basic"               # 基础
    intermediate = "intermediate" # 中级
    advanced = "advanced"         # 进阶
    comprehensive = "comprehensive"  # 综合


DIFFICULTY_DESC = {
    Difficulty.entry: "入门：刚学完该知识点，单一概念应用",
    Difficulty.basic: "基础：能熟练使用单一概念",
    Difficulty.intermediate: "中级：需要 2-3 个概念组合",
    Difficulty.advanced: "进阶：灵活组合多个概念，含边界条件",
    Difficulty.comprehensive: "综合：跨章节知识，贴近实际场景",
}


class QuestionType(str, Enum):
    choice = "choice"        # 选择题
    fill = "fill"            # 填空题
    judge = "judge"          # 判断题
    read = "read"            # 代码阅读题
    complete = "complete"    # 代码补全题
    program = "program"      # 编程实现题
    debug = "debug"          # Debug 修错题


QUESTION_TYPE_DESC = {
    QuestionType.choice: "选择题：extra.options 提供 A/B/C/D 四个选项，standard_answer 为字母",
    QuestionType.fill: "填空题：description 中用 ___ 表示空，standard_answer 为填入内容",
    QuestionType.judge: ' 判断题：standard_answer 为 "正确" 或 "错误"',
    QuestionType.read: "代码阅读题：给一段代码问输出，standard_answer 为输出值",
    QuestionType.complete: "代码补全题：reference_code 给出框架，TODO 处需补全",
    QuestionType.program: "编程实现题：需要完整解法 + 测试用例",
    QuestionType.debug: "Debug 修错题：description 给出错误代码，standard_answer 给出修复后代码",
}


class Provider(str, Enum):
    openai = "openai"
    deepseek = "deepseek"
    qwen = "qwen"
    moonshot = "moonshot"
    claude = "claude"


class ExerciseStatus(str, Enum):
    draft = "draft"
    published = "published"
    archived = "archived"


T = TypeVar("T")


class PageResult(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int = Field(ge=1)
    size: int = Field(ge=1, le=200)


class MessageResponse(BaseModel):
    message: str
