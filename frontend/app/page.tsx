"use client";
import Link from "next/link";
import { useAuth } from "@/store/auth";

export default function Home() {
  const token = useAuth((s) => s.token);
  return (
    <main className="p-6 space-y-4">
      <h1 className="text-2xl font-bold">Dashboard</h1>
      {!token ? (
        <div className="text-red-600">
          Você não está logado. <Link className="underline" href="/login">Ir para o login</Link>
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          <Link href="/disciplines" className="border p-3 rounded bg-white">Disciplinas</Link>
          <Link href="/grades" className="border p-3 rounded bg-white">Séries</Link>
          <Link href="/sections" className="border p-3 rounded bg-white">Turmas</Link>
          <Link href="/classes" className="border p-3 rounded bg-white">Classes</Link>
          <Link href="/students" className="border p-3 rounded bg-white">Alunos</Link>
          <Link href="/exams" className="border p-3 rounded bg-white">Exames</Link>
          <Link href="/pdf" className="border p-3 rounded bg-white">PDF</Link>
          <Link href="/answers" className="border p-3 rounded bg-white">Correção</Link>
        </div>
      )}
    </main>
  );
}