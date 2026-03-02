"use client";

import Link from "next/link";
import { useAuth } from "@/store/auth";

/**
 * Dashboard simples:
 * - Se não estiver logado, mostra link para /login.
 * - Se estiver com token armazenado, mostra links para as páginas do MVP.
 */
export default function Home() {
  const token = useAuth((s) => s.token);

  if (!token) {
    return (
      <main className="p-6 space-y-2">
        <h1 className="text-2xl font-bold">SAMBA Simulator</h1>
        <p className="text-red-600">Você não está logado.</p>
        <Link href="/login" className="underline text-blue-700">
          Ir para o login
        </Link>
      </main>
    );
  }

  return (
    <main className="p-6 space-y-4">
      <h1 className="text-2xl font-bold">Dashboard</h1>
      <div className="flex gap-4">
        <Link href="/disciplines" className="underline text-blue-700">
          Disciplinas
        </Link>
        <Link href="/pdf" className="underline text-blue-700">
          PDF
        </Link>
      </div>
    </main>
  );
}