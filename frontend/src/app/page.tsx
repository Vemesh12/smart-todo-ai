"use client";

import { useEffect, useMemo, useState } from "react";

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

export default function Home() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [categoryId, setCategoryId] = useState<number | null>(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [suggestedPriority, setSuggestedPriority] = useState<number | null>(null);
  const [suggestedDeadline, setSuggestedDeadline] = useState<string | null>(null);
  const [deadlineToCreate, setDeadlineToCreate] = useState<string | null>(null);
  const [priorityToCreate, setPriorityToCreate] = useState<number | null>(null);

  async function fetchData() {
    const [t, c] = await Promise.all([
      fetch(`${API_BASE}/tasks/`).then((r) => r.json()),
      fetch(`${API_BASE}/categories/`).then((r) => r.json()),
    ]);
    setTasks(t);
    setCategories(c);
  }

  useEffect(() => {
    fetchData();
  }, []);

  async function addTask(e: React.FormEvent) {
    e.preventDefault();
    const res = await fetch(`${API_BASE}/tasks/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title,
        description,
        category: categoryId,
        deadline: deadlineToCreate,
        priority_score: priorityToCreate ?? undefined,
      }),
    });
    if (res.ok) {
      setTitle("");
      setDescription("");
      setCategoryId(null);
      setDeadlineToCreate(null);
      setPriorityToCreate(null);
      setSuggestedDeadline(null);
      setSuggestedPriority(null);
      fetchData();
    }
  }

  async function getAiSuggestion() {
    setAiLoading(true);
    const res = await fetch(`${API_BASE}/ai/suggest/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        tasks: [{ title, description }],
        context: [],
      }),
    });
    const data = await res.json();
    const s = data?.suggestions?.[0];
    if (s) {
      setDescription(s.enhanced_description || description);
      setSuggestedPriority(typeof s.suggested_priority_score === 'number' ? s.suggested_priority_score : null);
      setSuggestedDeadline(s.suggested_deadline || null);
      const catName = s.suggested_category_name as string | undefined;
      if (catName) {
        const found = categories.find((c) => c.name === catName);
        if (found) setCategoryId(found.id);
      }
    }
    setAiLoading(false);
  }

  return (
    <div className="min-h-screen mx-auto max-w-5xl p-6 space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold tracking-tight">Smart Todo AI</h1>
        <nav className="flex gap-4 text-sm">
          <a href="/tasks" className="hover:opacity-80">Tasks</a>
          <a href="/context" className="hover:opacity-80">Context</a>
        </nav>
      </div>

      <form onSubmit={addTask} className="grid gap-3 md:grid-cols-4 items-start bg-white/40 dark:bg-black/20 backdrop-blur rounded-xl p-4 border">
        <input
          className="border rounded-lg px-3 py-2 md:col-span-1 focus:outline-none focus:ring-2 focus:ring-gray-300"
          placeholder="Task title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />
        <input
          className="border rounded-lg px-3 py-2 md:col-span-2 focus:outline-none focus:ring-2 focus:ring-gray-300"
          placeholder="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
        <div className="flex gap-2 md:col-span-1">
          <select
            className="border rounded-lg px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-gray-300"
            value={categoryId ?? ""}
            onChange={(e) => setCategoryId(e.target.value ? Number(e.target.value) : null)}
          >
            <option value="">No category</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>

        <div className="flex gap-2 md:col-span-4 items-center flex-wrap">
          <button type="submit" className="bg-black text-white rounded-lg px-4 py-2 hover:opacity-90">
            Add Task
          </button>
          <button
            type="button"
            onClick={getAiSuggestion}
            className="border rounded-lg px-4 py-2 hover:bg-black/5"
            disabled={aiLoading || !title}
          >
            {aiLoading ? "Thinking..." : "AI Suggest"}
          </button>

          {(suggestedPriority !== null || suggestedDeadline) && (
            <div className="ml-auto flex items-center gap-3 text-sm">
              {suggestedPriority !== null && (
                <span className="inline-flex items-center gap-2 rounded-full border px-3 py-1">
                  <span className="inline-block h-2 w-2 rounded-full" style={{ backgroundColor: suggestedPriority > 1.2 ? '#ef4444' : suggestedPriority > 0.6 ? '#f59e0b' : '#10b981' }} />
                  Priority {suggestedPriority.toFixed(2)}
                </span>
              )}
              {suggestedDeadline && (
                <span className="inline-flex items-center gap-2 rounded-full border px-3 py-1">
                  Deadline {new Date(suggestedDeadline).toLocaleDateString()}
                </span>
              )}
              <button
                type="button"
                className="border rounded-lg px-3 py-1 hover:bg-black/5"
                onClick={() => {
                  setPriorityToCreate(suggestedPriority);
                  setDeadlineToCreate(suggestedDeadline);
                }}
              >Apply</button>
            </div>
          )}
        </div>
      </form>

      <div className="space-y-2">
        <h2 className="text-xl font-medium">Tasks</h2>
        <div className="grid gap-3">
          {tasks.map((t) => (
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
              <div className="text-xs uppercase tracking-wide opacity-60">{t.status}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
