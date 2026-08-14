from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from schemas.ai import ChatRequest
from utils.dashscope_client import stream_chat

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/chat")
async def chat(req: ChatRequest):
    """
    AI 对话：后端代理 DashScope 流式接口，以 SSE 逐 token 下发。
    API Key 保存在服务端环境变量中，不暴露给前端。
    """
    messages = [m.model_dump() for m in req.messages]

    return StreamingResponse(
        stream_chat(messages, req.model),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
