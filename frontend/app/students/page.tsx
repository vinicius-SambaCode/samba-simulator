"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/store/auth";
import { authFetch } from "@/lib/api";
import { toast } from "sonner";

/** Padrão:
 *  GET/POST   -> /students/
 *  PUT/DELETE -> /students/{id}/
 */

type Student = { id: number; ra: string; name: string; class_id: number };
type SchoolClass = { id: number; name: string };

export default function StudentsPage() {
  const token = useAuth((s) => s.token);
  const [classes, setClasses] = useState<SchoolClass[]>([]);
  const [list, setList] = useState<Student[]>([]);
  const [form, setForm] = useState<Student>({ id: 0, ra: "", name: "", class_id: 10 });
  const [editing, setEditing] = useState<Student | null>(null);

  async function loadAll() {
    try {
      const [c, s] = await Promise.all([
        authFetch("/classes/", { method: "GET" }, token),
        authFetch("/students/", { method: "GET" }, token),
      ]);
      if (!c.ok || !s.ok) throw new Error("Falha ao carregar");
      setClasses(await c.json()); setList(await s.json());
    } catch (e: any) { toast.error(e.message ?? "Falha ao carregar"); }
  }

  async function create() {
    try {
      const { id, ...payload } = form;
      const resp = await authFetch("/students/", {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload),
      }, token);
      if (!resp.ok) throw new Error(`Erro ${resp.status}`);
      toast.success("Criado!"); setForm({ id: 0, ra: "", name: "", class_id: 10 }); loadAll();
    } catch (e: any) { toast.error(e.message ?? "Falha ao criar"); }
  }

  async function update(st: Student) {
    try {
      const resp = await authFetch(`/students/${st.id}/`, {
        method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(st),
      }, token);
      if (!resp.ok) throw new Error(`Erro ${resp.status}`);
      toast.success("Atualizado!"); setEditing(null); loadAll();
    } catch (e: any) { toast.error(e.message ?? "Falha ao atualizar"); }
  }

  async function remove(id: number) {
    try {
      const resp = await authFetch(`/students/${id}/`, { method: "DELETE" }, token);
      if (!resp.ok) throw new Error(`Erro ${resp.status}`);
      toast.success("Removido!"); loadAll();
    } catch (e: any) { toast.error(e.message ?? "Falha ao remover"); }
  }

  useEffect(() => { loadAll(); }, []);

  return (
    <main className="p-6 space-y-4">
      <h1 className="text-xl font-bold">Alunos</h1>
      <div className="flex gap-2 items-center">
        <input className="border p-2 rounded" placeholder="RA" value={form.ra} onChange={(e) => setForm({ ...form, ra: e.target.value })} />
        <input className="border p-2 rounded" placeholder="Nome" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
        <select className="border p-2 rounded" value={form.class_id} onChange={(e) => setForm({ ...form, class_id: Number(e.target.value) })}>
          {classes.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
        <button onClick={create} className="bg-green-600 text-white p-2 rounded">Criar</button>
      </div>

      <ul className="divide-y bg-white rounded shadow">
        {list.map((st) => (
          <li key={st.id} className="p-2 flex items-center gap-2">
            {editing?.id === st.id ? (
              <>
                <input className="border p-1 rounded w-32" value={editing.ra} onChange={(e) => setEditing({ ...editing, ra: e.target.value })} />
                <input className="border p-1 rounded flex-1" value={editing.name} onChange={(e) => setEditing({ ...editing, name: e.target.value })} />
                <select className="border p-1 rounded" value={editing.class_id} onChange={(e) => setEditing({ ...editing, class_id: Number(e.target.value) })}>
                  {classes.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                </select>
                <button onClick={() => update(editing)} className="bg-blue-600 text-white px-2 py-1 rounded">Salvar</button>
                <button onClick={() => setEditing(null)} className="px-2 py-1">Cancelar</button>
              </>
            ) : (
              <>
                <span className="w-32">{st.ra}</span>
                <span className="flex-1">{st.name}</span>
                <span>class={st.class_id}</span>
                <button onClick={() => setEditing(st)} className="px-2 py-1 border rounded">Editar</button>
                <button onClick={() => remove(st.id)} className="px-2 py-1 border rounded text-red-700">Excluir</button>
              </>
            )}
          </li>
        ))}
      </ul>
    </main>
  );
}