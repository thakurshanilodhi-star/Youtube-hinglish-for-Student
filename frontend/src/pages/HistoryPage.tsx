import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Film, Youtube, FileUp, Edit3, Trash2, RefreshCw } from "lucide-react";
import { jobApi } from "@/services/jobService";
import StatusBadge from "@/components/StatusBadge";
import ProgressBar from "@/components/ProgressBar";

interface Job { id: string; title: string; status: string; progress: number; source_type: string; created_at: string; }

export default function HistoryPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadJobs(); }, []);

  const loadJobs = async () => {
    try { const response = await jobApi.listJobs(); setJobs(response.data); }
    catch (err) { console.error("Failed to load jobs:", err); }
    finally { setLoading(false); }
  };

  const getIcon = (type: string) => {
    switch (type) { case "youtube": case "youtube_live": return <Youtube className="w-5 h-5" />; case "upload": return <FileUp className="w-5 h-5" />; default: return <Film className="w-5 h-5" />; }
  };

  if (loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full" /></div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div><h1 className="text-3xl font-bold mb-1">History</h1><p className="text-muted-foreground">All your dubbing jobs</p></div>
        <button onClick={loadJobs} className="p-2 rounded-lg hover:bg-muted transition-colors" title="Refresh"><RefreshCw className="w-5 h-5" /></button>
      </div>
      {jobs.length === 0 ? (
        <div className="text-center py-16 bg-card border border-border rounded-xl">
          <Film className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-medium mb-1">No jobs yet</h3>
          <p className="text-muted-foreground text-sm">Start by dubbing a video from the <Link to="/recorded" className="text-primary hover:underline">Recorded Video</Link> page.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {jobs.map((job) => (
            <div key={job.id} className="flex items-center justify-between p-4 bg-card border border-border rounded-xl hover:border-primary/30 transition-colors">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center text-primary">{getIcon(job.source_type)}</div>
                <div><p className="font-medium">{job.title || "Untitled"}</p><p className="text-xs text-muted-foreground">{new Date(job.created_at).toLocaleString()}</p></div>
              </div>
              <div className="flex items-center gap-6">
                <div className="flex items-center gap-3"><StatusBadge status={job.status} /><ProgressBar progress={job.progress} className="w-24" /></div>
                <div className="flex items-center gap-2">
                  <Link to={`/editor/${job.id}`} className="p-2 rounded-lg hover:bg-muted transition-colors" title="Edit subtitles"><Edit3 className="w-4 h-4" /></Link>
                  <button className="p-2 rounded-lg hover:bg-destructive/10 text-destructive transition-colors" title="Delete"><Trash2 className="w-4 h-4" /></button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
