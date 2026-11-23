import api from "./api";

export const subtitleApi = {
  getSegments: (jobId: string) => api.get(`/subtitles/${jobId}/segments`),
  updateSegment: (jobId: string, segmentId: string, translatedText: string) =>
    api.put(`/subtitles/${jobId}/segments/${segmentId}`, null, {
      params: { translated_text: translatedText },
    }),
};
