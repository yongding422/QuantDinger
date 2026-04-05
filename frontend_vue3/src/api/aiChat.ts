import request from './request'

export interface ChatMessage {
  id?: number
  role: 'user' | 'assistant' | 'system'
  content: string
  agent?: string  // e.g. 'Investment Director', 'Market Analyst'
  createdAt?: string
}

export interface ChatSession {
  id: string
  name: string
  createdAt: string
  updatedAt: string
}

export interface SendMessageParams {
  message: string
  agent?: string  // optional agent persona
}

export const aiChatApi = {
  sendMessage: (data: SendMessageParams) =>
    request.post<{ data: { reply: string; agent?: string } }>('/ai/chat/message', data),
  getHistory: (params?: { page?: number; pageSize?: number }) =>
    request.get<{ data: ChatSession[] }>('/ai/chat/history', { params }),
  saveChat: (data: { name: string; messages: ChatMessage[] }) =>
    request.post('/ai/chat/history/save', data),
}
