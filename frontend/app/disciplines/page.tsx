"use client";

import { useEffect, useState, useCallback } from "react";
import { useAuth } from "@/store/auth";
import { authFetch } from "@/lib/api";
import { toast } from "sonner";

/**
 * Convenção pretendida:
 *   - GET/POST   -> /disciplines/
 *   - PUT/DELETE -> /disciplines/{id}/
 *
 * Porém, se o backend tiver declarado os itens SEM barra final,
 * enviamos fallback automaticamente tentando também /disciplines/{id}
 * quando a primeira tentativa retornar 404.
 */

type Discipline = { id: number; name: string };

export default function DisciplinePage() {
  const token = useAuth((s) => s.token);

  const [list, setList] = useState<Discipline[]>([]);
  const [name, setName] = useState("");
  const [editing, setEditing] = useState<Discipline | null>(null);

  const load = useCallback(async () => {
    try {
      const resp = await authFetch("/disciplines/", { method: "GET" }, token);
      if (!resp.ok) throw new Error(`Erro ${resp.status}`);
      setList(await resp.json());
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Falha ao carregar";
      toast.error(msg);
    }
  }, [token]);

  async function create() {
    try {
      const resp = await authFetch(
        "/disciplines/",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name }),
        },
        token
      );
      if (!resp.ok) throw new Error(`Erro ${resp.status}`);
      toast.success("Criado!");
      setName("");
      load();
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Falha ao criar";
      toast.error(msg);
    }
  }

  // PUT com fallback: tenta /disciplines/{id}/ e, se 404, tenta /disciplines/{id}
  async function update(d: Discipline) {
    try {
      let resp = await authFetch(
        `/disciplines/${d.id}/`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name: d.name }),
        },
        token
      );

      if (resp.status === 404) {
        // tenta sem barra final
        resp = await authFetch(
          `/disciplines/${d.id}`,
          {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name: d.name }),
          },
          token
        );
      }

      if (!resp.ok) throw new Error(`Erro ${resp.status}`);
      toast.success("Atualizado!");
      setEditing(null);
      load();
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Falha ao atualizar";
      toast.error(msg);
    }
  }

  // DELETE com fallback: tenta /disciplines/{id}/ e, se 404, tenta /disciplines/{id}
  async function remove(id: number) {
    try {
      let resp = await authFetch(
        `/disciplines/${id}/`,
        { method: "DELETE" },
        token
      );

      if (resp.status === 404) {
        resp = await authFetch(
          `/disciplines/${id}`,
          { method: "DELETE" },
          token
        );
      }

      if (!resp.ok) throw new Error(`Erro ${resp.status}`);
      toast.success("Removido!");
      load();
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Falha ao remover";
      toast.error(msg);
    }
  }

  useEffect(() => {
    load();
  }, [load]);

  return (
    <main className="p-6 space-y-4">
      <h1 className="text-xl font-bold">Disciplinas</h1>

      <div className="flex gap-2">
        <input
          className="border p-2 rounded"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Nome"
        />
        <button onClick={create} className="bg-green-600 text-white p-2 rounded">
          Criar
        </button>
      </div>

      <ul className="divide-y bg-white rounded shadow">
        {list.map((d) => (
          <li key={d.id} className="p-2 flex items-center gap-2">
            {editing?.id === d.id ? (
              <>
                <input
                  className="border p-1 rounded"
                  value={editing.name}
                  onChange={(e) => setEditing({ ...editing, name: e.target.value })}
                />
                <button
                  onClick={() => update(editing)}
                  className="bg-blue-600 text-white px-2 py-1 rounded"
                >
                  Salvar
                </button>
                <button onClick={() => setEditing(null)} className="px-2 py-1">
                  Cancelar
                </button>
              </>
            ) : (
              <>
                <span className="flex-1">{d.name}</span>
                <button
                  onClick={() => setEditing(d)}
                  className="px-2 py-1 border rounded"
                >
                  Editar
                </button>
                <button
                  onClick={() => remove(d.id)}
                  className="px-2 py-1 border rounded text-red-700"
                >
                  Excluir
                </button>
              </>
            )}
          </li>
        ))}
      </ul>
    </main>
  );
}