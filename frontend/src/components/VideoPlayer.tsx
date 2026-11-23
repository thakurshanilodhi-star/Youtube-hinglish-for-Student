import { useRef, useState } from "react";
import ReactPlayer from "react-player";
import { Play, Pause, Volume2, VolumeX, Maximize } from "lucide-react";

interface VideoPlayerProps {
  url: string;
  subtitlesUrl?: string;
  dubbedAudioUrl?: string;
  showSubtitles?: boolean;
}

export default function VideoPlayer({
  url,
  subtitlesUrl,
  dubbedAudioUrl,
  showSubtitles = true,
}: VideoPlayerProps) {
  const playerRef = useRef<ReactPlayer>(null);
  const audioRef = useRef<HTMLAudioElement>(null);
  const [playing, setPlaying] = useState(false);
  const [muted, setMuted] = useState(false);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);

  const togglePlay = () => {
    const nextPlaying = !playing;
    setPlaying(nextPlaying);
    if (audioRef.current) {
      if (nextPlaying) {
        void audioRef.current.play();
      } else {
        audioRef.current.pause();
      }
    }
  };

  const toggleMute = () => {
    const nextMuted = !muted;
    setMuted(nextMuted);
    if (audioRef.current) {
      audioRef.current.muted = nextMuted;
    }
  };

  return (
    <div className="relative bg-black rounded-xl overflow-hidden aspect-video group">
      {dubbedAudioUrl && (
        <audio ref={audioRef} src={dubbedAudioUrl} muted={muted} />
      )}
      <ReactPlayer
        ref={playerRef}
        url={url}
        playing={playing}
        muted={Boolean(dubbedAudioUrl) || muted}
        width="100%"
        height="100%"
        onProgress={({ played }) => setProgress(played * 100)}
        onDuration={setDuration}
        config={{
          file: {
            tracks:
              showSubtitles && subtitlesUrl
                ? [
                    {
                      kind: "subtitles",
                      src: subtitlesUrl,
                      srcLang: "hi",
                      label: "Hinglish",
                      default: true,
                    },
                  ]
                : [],
          },
        }}
      />

      {/* Controls overlay */}
      <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex flex-col justify-end p-4">
        {/* Progress bar */}
        <div className="w-full bg-white/20 rounded-full h-1 mb-3 cursor-pointer">
          <div
            className="bg-primary h-full rounded-full"
            style={{ width: `${progress}%` }}
          />
        </div>

        <div className="flex items-center gap-3">
          <button onClick={togglePlay} className="text-white hover:text-primary transition-colors">
            {playing ? <Pause className="w-6 h-6" /> : <Play className="w-6 h-6" />}
          </button>
          <button onClick={toggleMute} className="text-white hover:text-primary transition-colors">
            {muted ? <VolumeX className="w-5 h-5" /> : <Volume2 className="w-5 h-5" />}
          </button>
          <span className="text-white text-sm">
            {formatTime((progress / 100) * duration)} / {formatTime(duration)}
          </span>
          <div className="flex-1" />
          <button className="text-white hover:text-primary transition-colors">
            <Maximize className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, "0")}`;
}
