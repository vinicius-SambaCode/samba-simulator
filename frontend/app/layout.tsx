import "./globals.css";
import Providers from "./providers";
import Link from "next/link";

export const metadata = {
  title: "SAMBA Simulator",
  description: "MVP de testes (CRUD + PDF + Correção)",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body className="min-h-screen bg-gray-50 text-gray-900">
        <header className="p-3 border-b bg-white flex gap-4">
          <b>SAMBA Simulator</b>
          <Link href="/">Dashboard</Link>
          <Link href="/disciplines">Disciplinas</Link>
          <Link href="/grades">Séries</Link>
          <Link href="/sections">Turmas</Link>
          <Link href="/classes">Classes</Link>
          <Link href="/students">Alunos</Link>
          <Link href="/exams">Exames</Link>
          <Link href="/pdf">PDF</Link>
          <Link href="/answers">Correção</Link>
          <span className="flex-1" />
          <Link href="/login">Login</Link>
        </header>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}