/**
 * API配置文件
 * 包含API基础URL和AI问答功能所需的API参数
 */

// API基础URL配置
export const apiConfig = {
  // 后端API基础URL
  baseURL: 'http://127.0.0.1:8000',
}

export const aiChatConfig = {
  // 后端 AI 代理接口（API Key 保存在服务端环境变量，不暴露给前端）
  apiEndpoint: `${apiConfig.baseURL}/api/ai/chat`,

  // 使用的模型（可选，不传则使用服务端默认模型）
  model: 'qwen3-max-preview'
}
