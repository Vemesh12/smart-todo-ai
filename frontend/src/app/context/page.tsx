"use client";

import { useEffect, useState } from "react";

type ContextEntry = {
  id: number;
  content: string;
  source_type: string;
  processed_insights?: any;
  created_at: string;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000/api";

export default function ContextPage() {
  const [entries, setEntries] = useState<ContextEntry[]>([]);
  const [content, setContent] = useState("");
  const [sourceType, setSourceType] = useState("note");

  async function fetchEntries() {
    const res = await fetch(`${API_BASE}/context/`);
    const data = await res.json();
    setEntries(data);
  }

  useEffect(() => {
    fetchEntries();
  }, []);

  async function addEntry(e: React.FormEvent) {
    e.preventDefault();
    const res = await fetch(`${API_BASE}/context/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content, source_type: sourceType }),
    });
    if (res.ok) {
      setContent("");
      setSourceType("note");
      fetchEntries();
    }
  }

  return (
    <div className="min-h-screen mx-auto max-w-5xl p-6 space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold tracking-tight">Daily Context</h1>
        <a className="text-sm hover:opacity-80" href="/">Home</a>
      </div>
      <form onSubmit={addEntry} className="grid gap-3 md:grid-cols-4 items-start bg-white/40 dark:bg-black/20 backdrop-blur rounded-xl p-4 border">
        <select
          className="border rounded-lg px-3 py-2"
          value={sourceType}
          onChange={(e) => setSourceType(e.target.value)}
        >
          <option value="note">Note</option>
          <option value="email">Email</option>
          <option value="whatsapp">WhatsApp</option>
          <option value="other">Other</option>
        </select>
        <input
          className="border rounded-lg px-3 py-2 md:col-span-2"
          placeholder="Context content"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          required
        />
        <button className="bg-black text-white rounded-lg px-4 py-2 hover:opacity-90">Add</button>
      </form>

      <div className="space-y-2">
        {entries.map((e) => (
          <div key={e.id} className="border rounded-xl p-4 bg-white/50 dark:bg-black/20">
            <div className="text-xs opacity-60 mb-1">{e.source_type} • {new Date(e.created_at).toLocaleString()}</div>
            <div className="text-sm">{e.content}</div>
            {e.processed_insights && (
              <div className="text-xs opacity-70 mt-2">insights: {JSON.stringify(e.processed_insights)}</div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}


