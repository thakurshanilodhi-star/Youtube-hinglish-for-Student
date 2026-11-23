import { Link } from "react-router-dom";
import { Film, Radio, FileText, ArrowRight, Zap, Globe, Brain } from "lucide-react";

const features = [
  {
    icon: Film,
    title: "Recorded Video Dubbing",
    description: "Upload or paste YouTube URLs to dub any video into natural Hinglish.",
    link: "/recorded",
  },
  {
    icon: Radio,
    title: "Live Stream Translation",
    description: "Real-time dubbing of YouTube live streams with under 3-second latency.",
    link: "/live",
  },
  {
    icon: FileText,
    title: "Subtitle Editor",
    description: "Fine-tune translations with our intuitive subtitle editing interface.",
    link: "/history",
  },
];

const highlights = [
  { icon: Zap, title: "AI-Powered", desc: "Whisper + Gemini/OpenAI for accurate transcription and translation" },
  { icon: Globe, title: "Natural Hinglish", desc: "Preserves technical terms, maintains conversational tone" },
  { icon: Brain, title: "Speaker Aware", desc: "Multi-speaker diarization with voice preservation" },
];

export default function HomePage() {
  return (
    <div className="space-y-12">
      {/* Hero */}
      <section className="text-center space-y-6 py-12">
        <h1 className="text-4xl lg:text-6xl font-bold tracking-tight">
          Dub Any Video into{" "}
          <span className="text-primary">Natural Hinglish</span>
        </h1>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          AI-powered platform that translates and dubs YouTube videos and live streams
          into conversational Hinglish — Hindi mixed naturally with English.
        </p>
        <div className="flex flex-wrap justify-center gap-4">
          <Link
            to="/recorded"
            className="inline-flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground rounded-lg font-medium hover:bg-primary/90 transition-colors"
          >
            <Film className="w-5 h-5" />
            Dub a Video
            <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            to="/live"
            className="inline-flex items-center gap-2 px-6 py-3 bg-secondary text-secondary-foreground rounded-lg font-medium hover:bg-secondary/80 transition-colors"
          >
            <Radio className="w-5 h-5" />
            Try Live Mode
          </Link>
        </div>
      </section>

      {/* Features */}
      <section className="grid md:grid-cols-3 gap-6">
        {features.map((feature) => {
          const Icon = feature.icon;
          return (
            <Link
              key={feature.title}
              to={feature.link}
              className="group p-6 bg-card border border-border rounded-xl hover:border-primary/50 transition-all hover:shadow-lg"
            >
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4 group-hover:bg-primary/20 transition-colors">
                <Icon className="w-6 h-6 text-primary" />
              </div>
              <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
              <p className="text-sm text-muted-foreground mb-4">{feature.description}</p>
              <span className="text-sm text-primary font-medium inline-flex items-center gap-1">
                Get Started <ArrowRight className="w-4 h-4" />
              </span>
            </Link>
          );
        })}
      </section>

      {/* Highlights */}
      <section className="bg-muted/50 rounded-2xl p-8">
        <h2 className="text-2xl font-bold text-center mb-8">Why HinglishDub?</h2>
        <div className="grid md:grid-cols-3 gap-8">
          {highlights.map((h) => {
            const Icon = h.icon;
            return (
              <div key={h.title} className="text-center space-y-3">
                <div className="w-14 h-14 bg-primary/10 rounded-full flex items-center justify-center mx-auto">
                  <Icon className="w-7 h-7 text-primary" />
                </div>
                <h3 className="font-semibold">{h.title}</h3>
                <p className="text-sm text-muted-foreground">{h.desc}</p>
              </div>
            );
          })}
        </div>
      </section>
    </div>
  );
}
