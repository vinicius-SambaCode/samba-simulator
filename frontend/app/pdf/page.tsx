"use client";

import { useState } from "react";
import { useAuth } from "@/store/auth";
import { toast } from "sonner";

/**
 * PDF:
 * - gera via POST /pdf/exams/{id}/pdf/generate?class_id=
 * - baixa via GET /pdf/exams/{id}/pdf/download?student_id=
 */
export default function PdfPage() {
  const token = useAuth((s) => s.token);

  const [examId, setExamId] = useState("1");
  const [classId, setClassId] = useState("10");
  const [studentId, setStudentId] = useState("100");

  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  async function gerar() {
    const url = `${process.env.NEXT_PUBLIC_API_BASE_URL}/pdf/exams/${examId}/pdf/generate?class_id=${classId}`;
    const resp = await fetch(url, { method: "POST", headers });

    if (!resp.ok) return toast.error("Erro ao gerar PDF — verifique o status LOCKED.");
    toast.success("PDFs gerados!");
  }

  async function baixar() {
    const url = `${process.env.NEXT_PUBLIC_API_BASE_URL}/pdf/exams/${examId}/pdf/download?student_id=${studentId}`;
    const resp = await fetch(url, { method: "GET", headers });

    if (resp.status === 404) return toast.error("Arquivo não encontrado — gere antes.");
    if (!resp.ok) return toast.error("Erro ao baixar PDF");

    const blob = await resp.blob();
    const href = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = href;
    a.download = `exam${examId}-student${studentId}.pdf`;
    a.click();
    URL.revokeObjectURL(href);

    toast.success("Download iniciado!");
  }

  return (
    <main className="p-6 space-y-4">
      <h1 className="text-xl font-bold">PDF</h1>

      <input className="border p-2 rounded w-52" value={examId} onChange={(e) => setExamId(e.target.value)} />
      <input className="border p-2 rounded w-52" value={classId} onChange={(e) => setClassId(e.target.value)} />
      <input className="border p-2 rounded w-52" value={studentId} onChange={(e) => setStudentId(e.target.value)} />

      <button onClick={gerar} className="bg-blue-700 text-white p-2 rounded">
        Gerar Turma
      </button>

      <button onClick={baixar} className="bg-emerald-700 text-white p-2 rounded">
        Baixar Aluno
      </button>
    </main>
  );
}