import { useState } from "react";
import { Save, RotateCcw } from "lucide-react";

interface Segment {
  id: string;
  speaker: string;
  start: number;
  end: number;
  original: string;
  translated: string;
}

interface SubtitleEditorProps {
  segments: Segment[];
  onSave: (segmentId: string, text: string) => void;
  currentTime?: number;
}

export default function SubtitleEditor({
  segments,
  onSave,
  currentTime = 0,
}: SubtitleEditorProps) {
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editText, setEditText] = useState("");

  const handleEdit = (segment: Segment) => {
    setEditingId(segment.id);
    setEditText(segment.translated || segment.original);
  };

  const handleSave = (segmentId: string) => {
    onSave(segmentId, editText);
    setEditingId(null);
  };

  const isActive = (seg: Segment) =>
    currentTime >= seg.start && currentTime <= seg.end;

  return (
    <div className="space-y-2 max-h-[500px] overflow-y-auto pr-2">
      {segments.map((seg) => (
        <div
          key={seg.id}
          className={`p-3 rounded-lg border transition-colors ${
            isActive(seg)
              ? "border-primary bg-primary/5"
              : "border-border bg-card hover:bg-muted/50"
          }`}
        >
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-medium text-primary">{seg.speaker}</span>
            <span className="text-xs text-muted-foreground">
              {formatTime(seg.start)} - {formatTime(seg.end)}
            </span>
          </div>

          <p className="text-sm text-muted-foreground mb-2">{seg.original}</p>

          {editingId === seg.id ? (
            <div className="space-y-2">
              <textarea
                value={editText}
                onChange={(e) => setEditText(e.target.value)}
                className="w-full p-2 text-sm bg-background border border-border rounded-md focus:ring-2 focus:ring-primary focus:border-transparent resize-none"
                rows={2}
              />
              <div className="flex gap-2">
                <button
                  onClick={() => handleSave(seg.id)}
                  className="flex items-center gap-1 px-3 py-1 text-xs bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
                >
                  <Save className="w-3 h-3" /> Save
                </button>
                <button
                  onClick={() => setEditingId(null)}
                  className="flex items-center gap-1 px-3 py-1 text-xs bg-muted rounded-md hover:bg-muted/80"
                >
                  <RotateCcw className="w-3 h-3" /> Cancel
                </button>
              </div>
            </div>
          ) : (
            <p
              className="text-sm font-medium cursor-pointer hover:text-primary transition-colors"
              onClick={() => handleEdit(seg)}
            >
              {seg.translated || "(No translation yet)"}
            </p>
          )}
        </div>
      ))}
    </div>
  );
}

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  const ms = Math.floor((seconds % 1) * 1000);
  return `${mins}:${secs.toString().padStart(2, "0")}.${ms.toString().padStart(3, "0")}`;
}
