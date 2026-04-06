import request from './request'

export interface Credential {
  id: number
  name: string
  type: 'ibkr' | 'mt5' | 'telegram' | 'polymarket' | 'alpaca' | 'binance' | 'okx'
  fields: Record<string, string>  // encrypted values stored by backend
  isActive: boolean
  createdAt: string
  updatedAt: string
}

export interface SaveCredentialParams {
  id?: number
  name: string
  type: string
  fields: Record<string, string>
}

export const credentialsApi = {
  getAll: () =>
    request.get<{ data: Credential[] }>('/settings/credentials'),
  getByType: (type: string) =>
    request.get<{ data: Credential }>(`/settings/credentials/${type}`),
  save: (data: SaveCredentialParams) =>
    request.post<{ data: Credential }>('/settings/credentials', data),
  delete: (id: number) =>
    request.post('/settings/credentials/delete', { id }),
  testConnection: (id: number) =>
    request.post<{ data: { ok: boolean; message: string } }>(`/settings/credentials/test`, { id }),
}
