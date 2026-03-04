"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/store/auth";
import { authFetch } from "@/lib/api";
import { toast } from "sonner";

/** Padrão paths:
 *  GET/POST   -> /grades/
 *  PUT/DELETE -> /grades/{id}/
 */

type Grade = { id: number; level: "fundamental" | "medio"; year_number: number; label: string };

export default function GradesPage() {
  const token = useAuth((s) => s.token);
  const [list, setList] = useState<Grade[]>([]);
  const [form, setForm] = useState<Grade>({ id: 0, level: "fundamental", year_number: 9, label: "9º" });
  const [editing, setEditing] = useState<Grade | null>(null);

  async function load() {
    try {
      const resp = await authFetch("/grades/", { method: "GET" }, token);
      if (!resp.ok) throw new Error(`Erro ${resp.status}`);
      setList(await resp.json());
    } catch (e: any) { toast.error(e.message ?? "Falha ao carregar"); }
  }

  async function create() {
    try {
      const { id, ...payload } = form; // id é auto
      const resp = await authFetch("/grades/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }, token);
      if (!resp.ok) throw new Error(`Erro ${resp.status}`);
      toast.success("Criado!"); setForm({ id: 0, level: "fundamental", year_number: 9, label: "9º" }); load();
    } catch (e: any) { toast.error(e.message ?? "Falha ao criar"); }
  }

  async function update(g: Grade) {
    try {
      const resp = await authFetch(`/grades/${g.id}/`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(g),
      }, token);
      if (!resp.ok) throw new Error(`Erro ${resp.status}`);
      toast.success("Atualizado!"); setEditing(null); load();
    } catch (e: any) { toast.error(e.message ?? "Falha ao atualizar"); }
  }

  async function remove(id: number) {
    try {
      const resp = await authFetch(`/grades/${id}/`, { method: "DELETE" }, token);
      if (!resp.ok) throw new Error(`Erro ${resp.status}`);
      toast.success("Removido!"); load();
    } catch (e: any) { toast.error(e.message ?? "Falha ao remover"); }
  }

  useEffect(() => { load(); }, []);

  return (
    <main className="p-6 space-y-4">
      <h1 className="text-xl font-bold">Séries (SchoolGrade)</h1>
      <div className="flex gap-2 items-center">
        <select className="border p-2 rounded" value={form.level} onChange={(e) => setForm({ ...form, level: e.target.value as Grade["level"] })}>
          <option value="fundamental">fundamental</option>
          <option value="medio">medio</option>
        </select>
        <input className="border p-2 rounded w-20" type="number" value={form.year_number} onChange={(e) => setForm({ ...form, year_number: Number(e.target.value) })} placeholder="Ano" />
        <input className="border p-2 rounded" value={form.label} onChange={(e) => setForm({ ...form, label: e.target.value })} placeholder="Label ex: 9º" />
        <button onClick={create} className="bg-green-600 text-white p-2 rounded">Criar</button>
      </div>

      <ul className="divide-y bg-white rounded shadow">
        {list.map((g) => (
          <li key={g.id} className="p-2 flex items-center gap-2">
            {editing?.id === g.id ? (
              <>
                <select className="border p-1 rounded" value={editing.level} onChange={(e) => setEditing({ ...editing, level: e.target.value as Grade["level"] })}>
                  <option value="fundamental">fundamental</option>
                  <option value="medio">medio</option>
                </select>
                <input className="border p-1 rounded w-20" type="number" value={editing.year_number} onChange={(e) => setEditing({ ...editing, year_number: Number(e.target.value) })} />
                <input className="border p-1 rounded" value={editing.label} onChange={(e) => setEditing({ ...editing, label: e.target.value })} />
                <button onClick={() => update(editing)} className="bg-blue-600 text-white px-2 py-1 rounded">Salvar</button>
                <button onClick={() => setEditing(null)} className="px-2 py-1">Cancelar</button>
              </>
            ) : (
              <>
                <span className="flex-1">{g.label} ({g.level}) • ano={g.year_number}</span>
                <button onClick={() => setEditing(g)} className="px-2 py-1 border rounded">Editar</button>
                <button onClick={() => remove(g.id)} className="px-2 py-1 border rounded text-red-700">Excluir</button>
              </>
            )}
          </li>
        ))}
      </ul>
    </main>
  );
}