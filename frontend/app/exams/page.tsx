"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/store/auth";
import { authFetch } from "@/lib/api";
import { toast } from "sonner";

/** Padrão:
 *  GET/POST   -> /exams/
 *  PUT/DELETE -> /exams/{id}/
 */

type Exam = { id: number; title: string; options_count: number; status?: string };

export default function ExamsPage() {
  const token = useAuth((s) => s.token);
  const [list, setList] = useState<Exam[]>([]);
  const [form, setForm] = useState<Exam>({ id: 0, title: "", options_count: 4, status: "LOCKED" });
  const [editing, setEditing] = useState<Exam | null>(null);

  async function load() {
    try {
      const resp = await authFetch("/exams/", { method: "GET" }, token);
      if (!resp.ok) throw new Error(`Erro ${resp.status}`);
      setList(await resp.json());
    } catch (e: any) { toast.error(e.message ?? "Falha ao carregar"); }
  }

  async function create() {
    try {
      const { id, ...payload } = form;
      const resp = await authFetch("/exams/", {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload),
      }, token);
      if (!resp.ok) throw new Error(`Erro ${resp.status}`);
      toast.success("Criado!"); setForm({ id: 0, title: "", options_count: 4, status: "LOCKED" }); load();
    } catch (e: any) { toast.error(e.message ?? "Falha ao criar"); }
  }

  async function update(ex: Exam) {
    try {
      const resp = await authFetch(`/exams/${ex.id}/`, {
        method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(ex),
      }, token);
      if (!resp.ok) throw new Error(`Erro ${resp.status}`);
      toast.success("Atualizado!"); setEditing(null); load();
    } catch (e: any) { toast.error(e.message ?? "Falha ao atualizar"); }
  }

  async function remove(id: number) {
    try {
      const resp = await authFetch(`/exams/${id}/`, { method: "DELETE" }, token);
      if (!resp.ok) throw new Error(`Erro ${resp.status}`);
      toast.success("Removido!"); load();
    } catch (e: any) { toast.error(e.message ?? "Falha ao remover"); }
  }

  useEffect(() => { load(); }, []);

  return (
    <main className="p-6 space-y-4">
      <h1 className="text-xl font-bold">Exames</h1>
      <div className="flex gap-2 items-center">
        <input className="border p-2 rounded" placeholder="Título" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
        <input className="border p-2 rounded w-24" type="number" placeholder="Opções" value={form.options_count} onChange={(e) => setForm({ ...form, options_count: Number(e.target.value) })} />
        <select className="border p-2 rounded" value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
          <option value="LOCKED">LOCKED</option>
          <option value="DRAFT">DRAFT</option>
        </select>
        <button onClick={create} className="bg-green-600 text-white p-2 rounded">Criar</button>
      </div>

      <ul className="divide-y bg-white rounded shadow">
        {list.map((ex) => (
          <li key={ex.id} className="p-2 flex items-center gap-2">
            {editing?.id === ex.id ? (
              <>
                <input className="border p-1 rounded" value={editing.title} onChange={(e) => setEditing({ ...editing, title: e.target.value })} />
                <input className="border p-1 rounded w-24" type="number" value={editing.options_count} onChange={(e) => setEditing({ ...editing, options_count: Number(e.target.value) })} />
                <select className="border p-1 rounded" value={editing.status} onChange={(e) => setEditing({ ...editing, status: e.target.value })}>
                  <option value="LOCKED">LOCKED</option>
                  <option value="DRAFT">DRAFT</option>
                </select>
                <button onClick={() => update(editing)} className="bg-blue-600 text-white px-2 py-1 rounded">Salvar</button>
                <button onClick={() => setEditing(null)} className="px-2 py-1">Cancelar</button>
              </>
            ) : (
              <>
                <span className="flex-1">{ex.title}</span>
                <span>opções={ex.options_count} • {ex.status}</span>
                <button onClick={() => setEditing(ex)} className="px-2 py-1 border rounded">Editar</button>
                <button onClick={() => remove(ex.id)} className="px-2 py-1 border rounded text-red-700">Excluir</button>
              </>
            )}
          </li>
        ))}
      </ul>
    </main>
  );
}