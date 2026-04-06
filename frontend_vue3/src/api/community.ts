import request from './request'

export interface StrategyShare {
  id: number
  userId: string
  userName: string
  strategyName: string
  strategyCode: string
  description: string
  likes: number
  views: number
  isLiked?: boolean
  createdAt: string
}

export interface Comment {
  id: number
  strategyId: number
  userId: string
  userName: string
  content: string
  createdAt: string
}

export const communityApi = {
  getSharedStrategies: (params?: { page?: number; pageSize?: number; sortBy?: string }) =>
    request.get<{ data: { items: StrategyShare[]; total: number } }>('/community/strategies', { params }),
  getStrategy: (id: number) =>
    request.get<{ data: StrategyShare }>(`/community/strategies/${id}`),
  shareStrategy: (data: { strategyId: number; description: string }) =>
    request.post<{ data: StrategyShare }>('/community/strategies/share', data),
  likeStrategy: (id: number) =>
    request.post('/community/strategies/like', { id }),
  unlikeStrategy: (id: number) =>
    request.post('/community/strategies/unlike', { id }),
  getComments: (strategyId: number) =>
    request.get<{ data: Comment[] }>(`/community/strategies/${strategyId}/comments`),
  addComment: (strategyId: number, content: string) =>
    request.post('/community/strategies/comments', { strategyId, content }),
}
