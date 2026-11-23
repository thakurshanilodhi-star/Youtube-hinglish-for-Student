import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { Save, Download, ArrowLeft } from "lucide-react";
import { jobApi } from "@/services/jobService";
import { subtitleApi } from "@/services/subtitleService";
import VideoPlayer from "@/components/VideoPlayer";
import SubtitleEditor from "@/components/SubtitleEditor";
import StatusBadge from "@/components/StatusBadge";
import ProgressBar from "@/components/ProgressBar";

interface Segment { id: string; speaker: string; start: number; end: number; original: string; translated: string; }
interface JobDetails { id: string; title: string; status: string; progress: number; source_url?: string; download_urls: Record<string, string | null>; }

export default function SubtitleEditorPage() {
  const { jobId } = useParams<{ jobId: string }>();
  const [job, setJob] = useState<JobDetails | null>(null);
  const [segments, setSegments] = useState<Segment[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentTime, setCurrentTime] = useState(0);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!jobId) return;
    loadJob();
    const interval = setInterval(loadJob, 5000);
    return () => clearInterval(interval);
  }, [jobId]);

  const loadJob = async () => {
    try {
      const [jobRes, segmentsRes] = await Promise.all([jobApi.getJob(jobId!), subtitleApi.getSegments(jobId!)]);
      setJob(jobRes.data);
      setSegments(segmentsRes.data);
    } catch (err) { console.error("Failed to load job:", err); }
    finally { setLoading(false); }
  };

  const handleSaveSegment = async (segmentId: string, text: string) => {
    setSaving(true);
    try {
      await subtitleApi.updateSegment(jobId!, segmentId, text);
      setSegments((prev) => prev.map((s) => (s.id === segmentId ? { ...s, translated: text } : s)));
    } catch (err) { console.error("Failed to save:", err); }
    finally { setSaving(false); }
  };

  const handleDownload = (type: string) => { if (job?.download_urls[type]) window.open(job.download_urls[type]!, "_blank"); };

  if (loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full" /></div>;
  if (!job) return <div className="text-center py-12 text-muted-foreground">Job not found</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <button
            onClick={() => {
              setCurrentTime(0);
              window.history.back();
            }}
            className="text-sm text-muted-foreground hover:text-foreground inline-flex items-center gap-1 mb-2"
          >
            <ArrowLeft className="w-4 h-4" /> Back
          </button>
          <h1 className="text-2xl font-bold">{job.title || "Subtitle Editor"}</h1>
        </div>
        <div className="flex items-center gap-3">
          <StatusBadge status={job.status} />
          <ProgressBar progress={job.progress} className="w-32" />
        </div>
      </div>
      <div className="grid lg:grid-cols-2 gap-6">
        <div className="space-y-4">
          {job.source_url && <VideoPlayer url={job.source_url} subtitlesUrl={job.download_urls.subtitles_vtt || undefined} showSubtitles={true} />}
          <div className="flex flex-wrap gap-2">
            {job.download_urls.dubbed_audio && (
              <button onClick={() => handleDownload("dubbed_audio")} className="inline-flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90">
                <Download className="w-4 h-4" /> Download Audio
              </button>
            )}
            {job.download_urls.subtitles_srt && (
              <button onClick={() => handleDownload("subtitles_srt")} className="inline-flex items-center gap-2 px-4 py-2 bg-secondary text-secondary-foreground rounded-lg text-sm font-medium hover:bg-secondary/80">
                <Download className="w-4 h-4" /> SRT Subtitles
              </button>
            )}
            {job.download_urls.subtitles_vtt && (
              <button onClick={() => handleDownload("subtitles_vtt")} className="inline-flex items-center gap-2 px-4 py-2 bg-secondary text-secondary-foreground rounded-lg text-sm font-medium hover:bg-secondary/80">
                <Download className="w-4 h-4" /> VTT Subtitles
              </button>
            )}
          </div>
        </div>
        <div className="bg-card border border-border rounded-xl p-4">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold">Edit Translations</h2>
            {saving && <span className="text-xs text-muted-foreground inline-flex items-center gap-1"><Save className="w-3 h-3" /> Saving...</span>}
          </div>
          <SubtitleEditor segments={segments} onSave={handleSaveSegment} currentTime={currentTime} />
        </div>
      </div>
    </div>
  );
}
