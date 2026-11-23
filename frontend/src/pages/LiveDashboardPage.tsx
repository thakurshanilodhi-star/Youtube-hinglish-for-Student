import { useState, useRef, useEffect } from "react";
import { Radio, StopCircle, Activity, Clock, Users } from "lucide-react";
import { liveApi } from "@/services/liveService";
import StatusBadge from "@/components/StatusBadge";

interface LiveSegment {
  type: string;
  original: string;
  translated: string;
  start: number;
  end: number;
}

export default function LiveDashboardPage() {
  const [youtubeUrl, setYoutubeUrl] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isStarting, setIsStarting] = useState(false);
  const [segments, setSegments] = useState<LiveSegment[]>([]);
  const [stats, setStats] = useState({ latency: 0, segments: 0 });
  const wsRef = useRef<WebSocket | null>(null);

  const startStream = async () => {
    if (!youtubeUrl.trim()) return;
    setIsStarting(true);
    try {
      const response = await liveApi.startStream(youtubeUrl);
      const { session_id, websocket_url } = response.data;
      setSessionId(session_id);
      connectWebSocket(websocket_url);
    } catch (err) {
      console.error("Failed to start stream:", err);
    } finally {
      setIsStarting(false);
    }
  };

  const connectWebSocket = (url: string) => {
    const ws = new WebSocket(url);
    wsRef.current = ws;
    ws.onopen = () => ws.send(JSON.stringify({ action: "ping" }));
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "segment") {
        setSegments((prev) => [...prev.slice(-50), data]);
        setStats((s) => ({ ...s, segments: s.segments + 1 }));
      }
    };
    ws.onerror = (err) => console.error("WebSocket error:", err);
    ws.onclose = () => setTimeout(() => connectWebSocket(url), 2000);
  };

  const stopStream = async () => {
    if (!sessionId) return;
    await liveApi.stopStream(sessionId);
    wsRef.current?.close();
    setSessionId(null);
    setSegments([]);
  };

  useEffect(() => { return () => { wsRef.current?.close(); }; }, []);

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">Live Stream Translation</h1>
        <p className="text-muted-foreground">Real-time Hinglish dubbing of YouTube live streams.</p>
      </div>
      {!sessionId ? (
        <div className="bg-card border border-border rounded-xl p-6">
          <label className="block text-sm font-medium mb-2">YouTube Live Stream URL</label>
          <div className="flex gap-3">
            <input type="url" value={youtubeUrl} onChange={(e) => setYoutubeUrl(e.target.value)}
              placeholder="https://youtube.com/live/..."
              className="flex-1 px-4 py-2.5 bg-background border border-border rounded-lg text-sm focus:ring-2 focus:ring-primary" />
            <button onClick={startStream} disabled={isStarting}
              className="px-6 py-2.5 bg-red-600 text-white rounded-lg font-medium text-sm hover:bg-red-700 disabled:opacity-50 inline-flex items-center gap-2">
              {isStarting ? <Activity className="w-4 h-4 animate-spin" /> : <Radio className="w-4 h-4" />}
              Start Stream
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="flex items-center justify-between bg-card border border-border rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
              <span className="font-medium">Live</span>
              <StatusBadge status="active" />
            </div>
            <div className="flex items-center gap-6 text-sm text-muted-foreground">
              <span className="flex items-center gap-1"><Clock className="w-4 h-4" />{stats.latency.toFixed(0)}ms latency</span>
              <span className="flex items-center gap-1"><Users className="w-4 h-4" />{stats.segments} segments</span>
            </div>
            <button onClick={stopStream}
              className="px-4 py-2 bg-destructive text-destructive-foreground rounded-lg text-sm font-medium hover:bg-destructive/90 inline-flex items-center gap-2">
              <StopCircle className="w-4 h-4" /> Stop
            </button>
          </div>
          <div className="bg-card border border-border rounded-xl p-4 h-96 overflow-y-auto">
            <h3 className="text-sm font-medium mb-3 text-muted-foreground uppercase tracking-wider">Live Transcript</h3>
            <div className="space-y-3">
              {segments.map((seg, i) => (
                <div key={i} className="p-3 bg-muted/50 rounded-lg animate-in fade-in slide-in-from-bottom-2">
                  <p className="text-xs text-muted-foreground mb-1">{formatTime(seg.start)} - {formatTime(seg.end)}</p>
                  <p className="text-sm line-through opacity-50">{seg.original}</p>
                  <p className="text-sm font-medium text-primary">{seg.translated}</p>
                </div>
              ))}
              {segments.length === 0 && <p className="text-center text-muted-foreground py-12">Waiting for audio...</p>}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, "0")}`;
}
