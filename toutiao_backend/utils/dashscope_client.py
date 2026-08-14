import asyncio
import json
import logging
import os

import httpx

logger = logging.getLogger(__name__)

# DashScope 配置（API Key 只保存在服务端环境变量，不暴露给前端）
DASHSCOPE_BASE_URL = os.getenv(
    "DASHSCOPE_BASE_URL",
    "https://dashscope.aliyuncs.com/compatible-mode/v1",
)
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
DASHSCOPE_MODEL = os.getenv("DASHSCOPE_MODEL", "qwen3-max-preview")

# 整轮流式生成的超时上限（秒）：读不设限，由 asyncio.timeout 控制总时长，
# 避免第三方大模型接口悬挂拖死连接（分层超时思路参考 RAG-LearnLittle）
STREAM_TIMEOUT = 120


def _sse_event(payload: dict) -> str:
    """构造一条 SSE data 帧"""
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


async def stream_chat(messages: list[dict], model: str | None = None):
    """
    调用 DashScope 兼容接口（OpenAI 格式，stream=True），逐行透传 SSE 流。
    错误/超时统一降级为 SSE 友好错误帧，细节只入日志。
    """
    if not DASHSCOPE_API_KEY:
        logger.error("DASHSCOPE_API_KEY 未配置，无法调用大模型")
        yield _sse_event({"error": {"message": "AI 服务未配置 API Key，请联系管理员"}})
        yield "data: [DONE]\n\n"
        return

    payload = {
        "model": model or DASHSCOPE_MODEL,
        "messages": messages,
        "stream": True,
    }
    headers = {
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(
            # 仅限制连接超时；流式读取时长由外层 asyncio.timeout 控制
            timeout=httpx.Timeout(connect=10.0, read=None, write=None, pool=None),
        ) as client:
            async with client.stream(
                "POST", f"{DASHSCOPE_BASE_URL}/chat/completions",
                json=payload, headers=headers,
            ) as resp:
                if resp.status_code != 200:
                    body = await resp.aread()
                    logger.warning("DashScope 返回 %s: %.500s", resp.status_code, body)
                    yield _sse_event({"error": {"message": "AI 服务暂时不可用，请稍后重试"}})
                    yield "data: [DONE]\n\n"
                    return

                # 透传上游 SSE 行（data: {...} / [DONE] / 空行）
                async with asyncio.timeout(STREAM_TIMEOUT):
                    async for line in resp.aiter_lines():
                        yield line + "\n"
    except TimeoutError:
        logger.warning("DashScope 流式响应超时（%ss）", STREAM_TIMEOUT)
        yield _sse_event({"error": {"message": "AI 响应超时，请稍后重试"}})
        yield "data: [DONE]\n\n"
    except httpx.HTTPError as e:
        logger.warning("请求 DashScope 失败: %s", e)
        yield _sse_event({"error": {"message": "AI 服务连接失败，请稍后重试"}})
        yield "data: [DONE]\n\n"
    except Exception:
        # 兜底：SSE 响应头已发出，任何未预期异常都降级为错误帧，细节只入日志
        logger.exception("AI 流式代理未预期异常")
        yield _sse_event({"error": {"message": "AI 服务异常，请稍后重试"}})
        yield "data: [DONE]\n\n"
