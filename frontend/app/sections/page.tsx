"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/store/auth";
import { authFetch } from "@/lib/api";
import { toast } from "sonner";

/** Padrão:
 *  GET/POST   -> /sections/
 *  PUT/DELETE -> /sections/{id}/
 */

type Section = { id: number; label: string };

export default function SectionsPage() {
  const token = useAuth((s) => s.token);
  const [list, setList] = useState<Section[]>([]);
  const [label, setLabel] = useState("");
  const [editing, setEditing] = useState<Section | null>(null);

  async function load() {
    try {
      const resp = await authFetch("/sections/", { method: "GET" }, token);
      if (!resp.ok) throw new Error(`Erro ${resp.status}`);
      setList(await resp.json());
    } catch (e: any) { toast.error(e.message ?? "Falha ao carregar"); }
  }

  async function create() {
    try {
      const resp = await authFetch("/sections/", {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ label }),
      }, token);
      if (!resp.ok) throw new Error(`Erro ${resp.status}`);
      toast.success("Criado!"); setLabel(""); load();
    } catch (e: any) { toast.error(e.message ?? "Falha ao criar"); }
  }

  async function update(sx: Section) {
    try {
      const resp = await authFetch(`/sections/${sx.id}/`, {
        method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(sx),
      }, token);
      if (!resp.ok) throw new Error(`Erro ${resp.status}`);
      toast.success("Atualizado!"); setEditing(null); load();
    } catch (e: any) { toast.error(e.message ?? "Falha ao atualizar"); }
  }

  async function remove(id: number) {
    try {
      const resp = await authFetch(`/sections/${id}/`, { method: "DELETE" }, token);
      if (!resp.ok) throw new Error(`Erro ${resp.status}`);
      toast.success("Removido!"); load();
    } catch (e: any) { toast.error(e.message ?? "Falha ao remover"); }
  }

  useEffect(() => { load(); }, []);

  return (
    <main className="p-6 space-y-4">
      <h1 className="text-xl font-bold">Turmas (ClassSection)</h1>
      <div className="flex gap-2">
        <input className="border p-2 rounded" value={label} onChange={(e) => setLabel(e.target.value)} placeholder="A, B, C..." />
        <button onClick={create} className="bg-green-600 text-white p-2 rounded">Criar</button>
      </div>

      <ul className="divide-y bg-white rounded shadow">
        {list.map((sx) => (
          <li key={sx.id} className="p-2 flex items-center gap-2">
            {editing?.id === sx.id ? (
              <>
                <input className="border p-1 rounded" value={editing.label} onChange={(e) => setEditing({ ...editing, label: e.target.value })} />
                <button onClick={() => update(editing)} className="bg-blue-600 text-white px-2 py-1 rounded">Salvar</button>
                <button onClick={() => setEditing(null)} className="px-2 py-1">Cancelar</button>
              </>
            ) : (
              <>
                <span className="flex-1">{sx.label}</span>
                <button onClick={() => setEditing(sx)} className="px-2 py-1 border rounded">Editar</button>
                <button onClick={() => remove(sx.id)} className="px-2 py-1 border rounded text-red-700">Excluir</button>
              </>
            )}
          </li>
        ))}
      </ul>
    </main>
  );
}