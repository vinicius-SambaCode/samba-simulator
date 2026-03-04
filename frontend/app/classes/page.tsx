"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/store/auth";
import { authFetch } from "@/lib/api";
import { toast } from "sonner";

/** Padrão:
 *  GET/POST   -> /classes/
 *  PUT/DELETE -> /classes/{id}/
 */

type Grade = { id: number; label: string };
type Section = { id: number; label: string };
type SchoolClass = { id: number; grade_id: number; section_id: number; name: string };

export default function ClassesPage() {
  const token = useAuth((s) => s.token);
  const [grades, setGrades] = useState<Grade[]>([]);
  const [sections, setSections] = useState<Section[]>([]);
  const [list, setList] = useState<SchoolClass[]>([]);

  const [form, setForm] = useState<SchoolClass>({ id: 0, grade_id: 1, section_id: 1, name: "" });
  const [editing, setEditing] = useState<SchoolClass | null>(null);

  async function loadAll() {
    try {
      const [g, s, c] = await Promise.all([
        authFetch("/grades/", { method: "GET" }, token),
        authFetch("/sections/", { method: "GET" }, token),
        authFetch("/classes/", { method: "GET" }, token),
      ]);
      if (!g.ok || !s.ok || !c.ok) throw new Error("Falha ao carregar bases");
      setGrades(await g.json()); setSections(await s.json()); setList(await c.json());
    } catch (e: any) { toast.error(e.message ?? "Falha ao carregar"); }
  }

  async function create() {
    try {
      const payload = { grade_id: form.grade_id, section_id: form.section_id, name: form.name || "Nova Classe" };
      const resp = await authFetch("/classes/", {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload),
      }, token);
      if (!resp.ok) throw new Error(`Erro ${resp.status}`);
      toast.success("Criado!"); setForm({ id: 0, grade_id: 1, section_id: 1, name: "" }); loadAll();
    } catch (e: any) { toast.error(e.message ?? "Falha ao criar"); }
  }

  async function update(sc: SchoolClass) {
    try {
      const resp = await authFetch(`/classes/${sc.id}/`, {
        method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(sc),
      }, token);
      if (!resp.ok) throw new Error(`Erro ${resp.status}`);
      toast.success("Atualizado!"); setEditing(null); loadAll();
    } catch (e: any) { toast.error(e.message ?? "Falha ao atualizar"); }
  }

  async function remove(id: number) {
    try {
      const resp = await authFetch(`/classes/${id}/`, { method: "DELETE" }, token);
      if (!resp.ok) throw new Error(`Erro ${resp.status}`);
      toast.success("Removido!"); loadAll();
    } catch (e: any) { toast.error(e.message ?? "Falha ao remover"); }
  }

  useEffect(() => { loadAll(); }, []);

  return (
    <main className="p-6 space-y-4">
      <h1 className="text-xl font-bold">Classes (SchoolClass)</h1>
      <div className="flex gap-2 items-center">
        <select className="border p-2 rounded" value={form.grade_id} onChange={(e) => setForm({ ...form, grade_id: Number(e.target.value) })}>
          {grades.map(g => <option key={g.id} value={g.id}>{g.label}</option>)}
        </select>
        <select className="border p-2 rounded" value={form.section_id} onChange={(e) => setForm({ ...form, section_id: Number(e.target.value) })}>
          {sections.map(s => <option key={s.id} value={s.id}>{s.label}</option>)}
        </select>
        <input className="border p-2 rounded" placeholder="Nome (ex: 9ºA)" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
        <button onClick={create} className="bg-green-600 text-white p-2 rounded">Criar</button>
      </div>

      <ul className="divide-y bg-white rounded shadow">
        {list.map((sc) => (
          <li key={sc.id} className="p-2 flex items-center gap-2">
            {editing?.id === sc.id ? (
              <>
                <select className="border p-1 rounded" value={editing.grade_id} onChange={(e) => setEditing({ ...editing, grade_id: Number(e.target.value) })}>
                  {grades.map(g => <option key={g.id} value={g.id}>{g.label}</option>)}
                </select>
                <select className="border p-1 rounded" value={editing.section_id} onChange={(e) => setEditing({ ...editing, section_id: Number(e.target.value) })}>
                  {sections.map(s => <option key={s.id} value={s.id}>{s.label}</option>)}
                </select>
                <input className="border p-1 rounded" value={editing.name} onChange={(e) => setEditing({ ...editing, name: e.target.value })} />
                <button onClick={() => update(editing)} className="bg-blue-600 text-white px-2 py-1 rounded">Salvar</button>
                <button onClick={() => setEditing(null)} className="px-2 py-1">Cancelar</button>
              </>
            ) : (
              <>
                <span className="flex-1">{sc.name} • grade={sc.grade_id}, section={sc.section_id}</span>
                <button onClick={() => setEditing(sc)} className="px-2 py-1 border rounded">Editar</button>
                <button onClick={() => remove(sc.id)} className="px-2 py-1 border rounded text-red-700">Excluir</button>
              </>
            )}
          </li>
        ))}
      </ul>
    </main>
  );
}
