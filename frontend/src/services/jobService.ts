import api from "./api";

export const jobApi = {
  createJob: (youtubeUrl: string, sourceType: string = "youtube") =>
    api.post("/jobs/create", null, { params: { youtube_url: youtubeUrl, source_type: sourceType } }),

  uploadVideo: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post("/jobs/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },

  getJob: (jobId: string) => api.get(`/jobs/${jobId}`),
  listJobs: () => api.get("/jobs/"),
  downloadFile: (jobId: string, fileType: string) =>
    api.get(`/jobs/${jobId}/download/${fileType}`, { responseType: "blob" }),
};
