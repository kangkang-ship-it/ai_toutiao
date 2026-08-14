from typing import Literal, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """单条对话消息"""
    role: Literal["system", "user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    """AI 对话请求体"""
    messages: list[ChatMessage] = Field(min_length=1, description="对话消息列表")
    model: Optional[str] = Field(default=None, description="模型名，不传则使用服务端配置的默认模型")
