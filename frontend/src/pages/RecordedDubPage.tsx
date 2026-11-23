import { useState, useRef, useCallback } from "react";
import { Link } from "react-router-dom";
import {
  Youtube,
  Upload,
  Link as LinkIcon,
  FileVideo,
  CheckCircle,
  AlertCircle,
  Loader2,
} from "lucide-react";
import { jobApi } from "@/services/jobService";
import { useJobsStore } from "@/store/jobsStore";
import StatusBadge from "@/components/StatusBadge";
import ProgressBar from "@/components/ProgressBar";

type InputMode = "youtube" | "upload";

export default function RecordedDubPage() {
  const [mode, setMode] = useState<InputMode>("youtube");
  const [youtubeUrl, setYoutubeUrl] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [recentJob, setRecentJob] = useState<any>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { jobs, addJob } = useJobsStore();

  const handleYoutubeSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!youtubeUrl.trim()) return;

    setIsSubmitting(true);
    setError("");

    try {
      const response = await jobApi.createJob(youtubeUrl, "youtube");
      const job = response.data;
      setRecentJob(job);
      addJob({
        id: job.job_id,
        title: "YouTube Video",
        status: "pending",
        progress: 0,
        source_type: "youtube",
        created_at: new Date().toISOString(),
      });
      setYoutubeUrl("");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to create job");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsSubmitting(true);
    setError("");

    try {
      const response = await jobApi.uploadVideo(file);
      const job = response.data;
      setRecentJob(job);
      addJob({
        id: job.job_id,
        title: file.name,
        status: "pending",
        progress: 0,
        source_type: "upload",
        created_at: new Date().toISOString(),
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to upload video");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold mb-2">Recorded Video Dubbing</h1>
        <p className="text-muted-foreground">
          Paste a YouTube URL or upload a video file to dub it into Hinglish.
        </p>
      </div>

      {/* Mode selector */}
      <div className="flex gap-2 p-1 bg-muted rounded-lg w-fit">
        <button
          onClick={() => setMode("youtube")}
          className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            mode === "youtube"
              ? "bg-card text-foreground shadow-sm"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          <Youtube className="w-4 h-4" />
          YouTube URL
        </button>
        <button
          onClick={() => setMode("upload")}
          className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            mode === "upload"
              ? "bg-card text-foreground shadow-sm"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          <Upload className="w-4 h-4" />
          Upload File
        </button>
      </div>

      {/* Input area */}
      <div className="bg-card border border-border rounded-xl p-6">
        {mode === "youtube" ? (
          <form onSubmit={handleYoutubeSubmit} className="space-y-4">
            <label className="block text-sm font-medium mb-1.5">
              YouTube Video URL
            </label>
            <div className="flex gap-3">
              <div className="relative flex-1">
                <LinkIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <input
                  type="url"
                  value={youtubeUrl}
                  onChange={(e) => setYoutubeUrl(e.target.value)}
                  placeholder="https://youtube.com/watch?v=..."
                  className="w-full pl-10 pr-4 py-2.5 bg-background border border-border rounded-lg text-sm focus:ring-2 focus:ring-primary focus:border-transparent"
                  required
                />
              </div>
              <button
                type="submit"
                disabled={isSubmitting}
                className="px-6 py-2.5 bg-primary text-primary-foreground rounded-lg font-medium text-sm hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center gap-2"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <Youtube className="w-4 h-4" />
                    Start Dubbing
                  </>
                )}
              </button>
            </div>
          </form>
        ) : (
          <div className="space-y-4">
            <label className="block text-sm font-medium mb-1.5">
              Upload Video File
            </label>
            <div
              onClick={() => fileInputRef.current?.click()}
              className="border-2 border-dashed border-border rounded-lg p-8 text-center cursor-pointer hover:border-primary/50 hover:bg-muted/50 transition-colors"
            >
              <FileVideo className="w-10 h-10 text-muted-foreground mx-auto mb-3" />
              <p className="text-sm font-medium mb-1">
                Click to upload or drag and drop
              </p>
              <p className="text-xs text-muted-foreground">
                MP4, MKV, AVI up to 2GB
              </p>
              <input
                ref={fileInputRef}
                type="file"
                accept=".mp4,.mkv,.avi,.mov"
                onChange={handleFileUpload}
                className="hidden"
              />
            </div>
            {isSubmitting && (
              <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="w-4 h-4 animate-spin" />
                Uploading and processing...
              </div>
            )}
          </div>
        )}

        {error && (
          <div className="mt-4 flex items-center gap-2 text-sm text-red-600 bg-red-50 dark:bg-red-900/20 p-3 rounded-lg">
            <AlertCircle className="w-4 h-4" />
            {error}
          </div>
        )}

        {recentJob && (
          <div className="mt-4 flex items-center gap-2 text-sm text-green-600 bg-green-50 dark:bg-green-900/20 p-3 rounded-lg">
            <CheckCircle className="w-4 h-4" />
            Job created! ID: {recentJob.job_id}
          </div>
        )}
      </div>

      {/* Recent jobs */}
      {jobs.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">Recent Jobs</h2>
          <div className="space-y-3">
            {jobs.slice(0, 5).map((job) => (
              <div
                key={job.id}
                className="flex items-center justify-between p-4 bg-card border border-border rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                    {job.source_type === "youtube" ? (
                      <Youtube className="w-5 h-5 text-primary" />
                    ) : (
                      <FileVideo className="w-5 h-5 text-primary" />
                    )}
                  </div>
                  <div>
                    <p className="font-medium text-sm">{job.title || "Untitled"}</p>
                    <p className="text-xs text-muted-foreground">
                      {new Date(job.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <StatusBadge status={job.status} />
                  <ProgressBar progress={job.progress} className="w-24" />
                  <Link
                    to={`/editor/${job.id}`}
                    className="text-xs text-primary hover:underline"
                  >
                    Edit
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
