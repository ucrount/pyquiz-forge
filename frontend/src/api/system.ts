import client from './client'

export const systemApi = {
  health(): Promise<{ status: string }> {
    return client.get('/health').then((r) => r.data)
  },
  version(): Promise<{ name: string; version: string }> {
    return client.get('/version').then((r) => r.data)
  },
}
