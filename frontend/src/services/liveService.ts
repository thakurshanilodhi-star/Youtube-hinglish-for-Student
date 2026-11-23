import api from "./api";

export const liveApi = {
  startStream: (youtubeUrl: string) =>
    api.post("/live/start", null, { params: { youtube_url: youtubeUrl } }),
  stopStream: (sessionId: string) => api.post(`/live/${sessionId}/stop`),
  getStatus: (sessionId: string) => api.get(`/live/${sessionId}/status`),
};
