import { Routes, Route } from "react-router-dom";
import { useEffect } from "react";
import Layout from "@/components/Layout";
import HomePage from "@/pages/HomePage";
import RecordedDubPage from "@/pages/RecordedDubPage";
import LiveDashboardPage from "@/pages/LiveDashboardPage";
import SubtitleEditorPage from "@/pages/SubtitleEditorPage";
import HistoryPage from "@/pages/HistoryPage";
import SettingsPage from "@/pages/SettingsPage";
import LoginPage from "@/pages/LoginPage";
import { useThemeStore } from "@/store/themeStore";

function App() {
  const { darkMode } = useThemeStore();

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [darkMode]);

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<Layout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/recorded" element={<RecordedDubPage />} />
        <Route path="/live" element={<LiveDashboardPage />} />
        <Route path="/editor/:jobId" element={<SubtitleEditorPage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Route>
    </Routes>
  );
}

export default App;
