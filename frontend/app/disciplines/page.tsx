"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/store/auth";
import { toast } from "sonner";

/**
 * Página de Disciplinas:
 * - lista via GET /disciplines
 * - cria via POST /disciplines
 */
type Discipline = { id: number; name: string };

export default function DisciplinePage() {
  const token = useAuth((s) => s.token);
  const [list, setList] = useState<Discipline[]>([]);
  const [name, setName] = useState("");

  const headers = token
    ? { Authorization: `Bearer ${token}`, "Content-Type": "application/json" }
    : { "Content-Type": "application/json" };

  async function load() {
    try {
      const resp = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/disciplines`, { headers });
      if (!resp.ok) throw new Error("Erro ao carregar disciplinas");
      setList(await resp.json());
    } catch (e: any) {
      toast.error(e.message);
    }
  }

  async function create() {
    try {
      const resp = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/disciplines`, {
        method: "POST",
        headers,
        body: JSON.stringify({ name }),
      });
      if (!resp.ok) throw new Error("Erro ao criar disciplina");

      toast.success("Disciplina criada!");
      setName("");
      load();
    } catch (e: any) {
      toast.error(e.message);
    }
  }

  useEffect(() => { load(); }, []);

  return (
    <main className="p-6 space-y-4">
      <h1 className="text-xl font-bold">Disciplinas</h1>

      <div className="flex gap-2">
        <input
          className="border p-2 rounded flex-1"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Nome da disciplina"
        />
        <button onClick={create} className="bg-green-600 text-white p-2 rounded">
          Criar
        </button>
      </div>

      <ul className="list-disc pl-6">
        {list.map((d) => (
          <li key={d.id}>{d.name}</li>
        ))}
      </ul>
    </main>
  );
}