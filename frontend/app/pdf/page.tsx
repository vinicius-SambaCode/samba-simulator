"use client";

import { useState } from "react";
import { useAuth } from "@/store/auth";
import { authFetch } from "@/lib/api";
import { toast } from "sonner";

export default function PdfPage() {
  const token = useAuth((s) => s.token);

  const [examId, setExamId] = useState("1");
  const [classId, setClassId] = useState("10");
  const [studentId, setStudentId] = useState("100");
  const [gerado, setGerado] = useState(false);

  async function gerar() {
    try {
      const url = `/pdf/exams/${examId}/pdf/generate?class_id=${classId}`;
      const resp = await authFetch(url, { method: "POST" }, token);
      const body = await resp.text();
      console.log("[PDF gerar] STATUS:", resp.status, "BODY:", body);
      if (!resp.ok) return toast.error(body || "Erro ao gerar PDF.");
      setGerado(true);
      toast.success("PDFs gerados!");
    } catch (e: any) {
      toast.error(e?.message ?? "Falha ao gerar");
    }
  }

  async function baixar() {
    try {
      const url = `/pdf/exams/${examId}/pdf/download?student_id=${studentId}`;
      const probe = await authFetch(url, { method: "GET" }, token);
      const text = await probe.text();
      console.log("[PDF baixar] STATUS:", probe.status, "BODY:", text);
      if (probe.status === 404) return toast.error("Gere antes.");
      if (!probe.ok) return toast.error(text || "Erro ao baixar");

      // baixa de fato
      const resp = await authFetch(url, { method: "GET" }, token);
      const blob = await resp.blob();
      const href = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = href; a.download = `exam${examId}-student${studentId}.pdf`; a.click();
      URL.revokeObjectURL(href);
      toast.success("Download iniciado!");
    } catch (e: any) {
      toast.error(e?.message ?? "Falha ao baixar");
    }
  }

  return (
    <main className="p-6 space-y-4">
      <h1 className="text-xl font-bold">PDF</h1>

      <div className="flex gap-2 items-center">
        <input className="border p-2 rounded w-24" value={examId} onChange={(e) => setExamId(e.target.value)} placeholder="Exam ID" />
        <input className="border p-2 rounded w-24" value={classId} onChange={(e) => setClassId(e.target.value)} placeholder="Class ID" />
        <input className="border p-2 rounded w-24" value={studentId} onChange={(e) => setStudentId(e.target.value)} placeholder="Student ID" />
        <button onClick={gerar} className="bg-blue-700 text-white p-2 rounded">Gerar Turma</button>
        <button onClick={baixar} disabled={!gerado} className="bg-emerald-700 text-white p-2 rounded disabled:opacity-40">Baixar Aluno</button>
      </div>
    </main>
  );
}