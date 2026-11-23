import { useState } from "react";
import { Moon, Key, Bell } from "lucide-react";
import { useThemeStore } from "@/store/themeStore";

export default function SettingsPage() {
  const { darkMode, toggleDarkMode } = useThemeStore();
  const [apiKey, setApiKey] = useState("");
  const [notifications, setNotifications] = useState(true);

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <div><h1 className="text-3xl font-bold mb-2">Settings</h1><p className="text-muted-foreground">Manage your preferences and API keys</p></div>
      <section className="bg-card border border-border rounded-xl p-6 space-y-4">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center"><Moon className="w-5 h-5 text-primary" /></div>
          <div><h2 className="font-semibold">Appearance</h2><p className="text-sm text-muted-foreground">Customize how HinglishDub looks</p></div>
        </div>
        <div className="flex items-center justify-between py-3 border-t border-border">
          <div><p className="font-medium">Dark Mode</p><p className="text-sm text-muted-foreground">Use dark theme across the app</p></div>
          <button onClick={toggleDarkMode} className={`relative w-12 h-6 rounded-full transition-colors ${darkMode ? "bg-primary" : "bg-muted"}`}>
            <span className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${darkMode ? "translate-x-7" : "translate-x-1"}`} />
          </button>
        </div>
      </section>
      <section className="bg-card border border-border rounded-xl p-6 space-y-4">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center"><Key className="w-5 h-5 text-primary" /></div>
          <div><h2 className="font-semibold">API Configuration</h2><p className="text-sm text-muted-foreground">Manage your AI service keys</p></div>
        </div>
        <div className="space-y-3">
          <div><label className="block text-sm font-medium mb-1.5">Gemini API Key</label><input type="password" value={apiKey} onChange={(e) => setApiKey(e.target.value)} placeholder="AIza..." className="w-full px-4 py-2.5 bg-background border border-border rounded-lg text-sm focus:ring-2 focus:ring-primary" /></div>
          <div><label className="block text-sm font-medium mb-1.5">OpenAI API Key</label><input type="password" placeholder="sk-..." className="w-full px-4 py-2.5 bg-background border border-border rounded-lg text-sm focus:ring-2 focus:ring-primary" /></div>
          <div><label className="block text-sm font-medium mb-1.5">ElevenLabs API Key</label><input type="password" placeholder="..." className="w-full px-4 py-2.5 bg-background border border-border rounded-lg text-sm focus:ring-2 focus:ring-primary" /></div>
        </div>
        <button className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90">Save API Keys</button>
      </section>
      <section className="bg-card border border-border rounded-xl p-6 space-y-4">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center"><Bell className="w-5 h-5 text-primary" /></div>
          <div><h2 className="font-semibold">Notifications</h2><p className="text-sm text-muted-foreground">Configure alert preferences</p></div>
        </div>
        <div className="flex items-center justify-between py-3 border-t border-border">
          <div><p className="font-medium">Job Completion Alerts</p><p className="text-sm text-muted-foreground">Get notified when dubbing completes</p></div>
          <button onClick={() => setNotifications(!notifications)} className={`relative w-12 h-6 rounded-full transition-colors ${notifications ? "bg-primary" : "bg-muted"}`}>
            <span className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${notifications ? "translate-x-7" : "translate-x-1"}`} />
          </button>
        </div>
      </section>
    </div>
  );
}
