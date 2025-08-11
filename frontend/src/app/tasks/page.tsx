"use client";

import { useEffect, useState } from "react";

type Category = { id: number; name: string };
type Task = {
  id: number;
  title: string;
  description: string;
  category: number | null;
  category_detail?: Category | null;
  priority_score: number;
  deadline: string | null;
  status: "todo" | "in_progress" | "done";
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000/api";

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [filters, setFilters] = useState({ status: "", category: "", min_priority: "" });

  async function fetchData() {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([k, v]) => { if (v) params.set(k, v as string); });
    const [t, c] = await Promise.all([
      fetch(`${API_BASE}/tasks/?${params.toString()}`).then((r) => r.json()),
      fetch(`${API_BASE}/categories/`).then((r) => r.json()),
    ]);
    setTasks(t);
    setCategories(c);
  }

  useEffect(() => { fetchData(); }, [filters]);

  return (
    <div className="min-h-screen mx-auto max-w-6xl p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold tracking-tight">Tasks</h1>
        <a className="text-sm hover:opacity-80" href="/">Home</a>
      </div>
      <div className="flex gap-3 items-end bg-white/40 dark:bg-black/20 backdrop-blur p-4 rounded-xl border">
        <select className="border rounded-lg px-3 py-2" value={filters.status} onChange={(e) => setFilters(f => ({...f, status: e.target.value}))}>
          <option value="">All Status</option>
          <option value="todo">To Do</option>
          <option value="in_progress">In Progress</option>
          <option value="done">Done</option>
        </select>
        <select className="border rounded-lg px-3 py-2" value={filters.category} onChange={(e) => setFilters(f => ({...f, category: e.target.value}))}>
          <option value="">All Categories</option>
          {categories.map(c => <option key={c.id} value={String(c.id)}>{c.name}</option>)}
        </select>
        <input className="border rounded-lg px-3 py-2" placeholder="Min priority" value={filters.min_priority} onChange={(e) => setFilters(f => ({...f, min_priority: e.target.value}))} />
        <button className="border rounded-lg px-3 py-2 hover:bg-black/5" onClick={() => setFilters({ status: "", category: "", min_priority: "" })}>Reset</button>
      </div>

      <div className="grid gap-3">
        {tasks.map(t => (
          <div key={t.id} className="border rounded-xl p-4 flex justify-between items-start bg-white/50 dark:bg-black/20">
            <div className="space-y-1">
              <div className="font-medium tracking-tight flex items-center gap-2">
                <span className="inline-block h-2 w-2 rounded-full" style={{ backgroundColor: t.priority_score > 1.2 ? '#ef4444' : t.priority_score > 0.6 ? '#f59e0b' : '#10b981' }} />
                {t.title}
              </div>
              <div className="text-sm opacity-80">{t.description}</div>
              <div className="text-xs opacity-60 flex gap-3">
                <span>{t.category_detail?.name || "Uncategorized"}</span>
                {t.deadline && <span>Due {new Date(t.deadline).toLocaleDateString()}</span>}
                <span>Priority {t.priority_score.toFixed(2)}</span>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs uppercase opacity-60">{t.status}</span>
              <button
                className="text-xs border rounded-lg px-2 py-1 hover:bg-black/5"
                onClick={async () => {
                  const res = await fetch(`${API_BASE}/tasks/${t.id}/ai-refresh/`, { method: 'POST' });
                  if (res.ok) fetchData();
                }}
              >AI Refresh</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}


