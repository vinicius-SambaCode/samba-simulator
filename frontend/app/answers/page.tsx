"use client";

import { useState } from "react";
import { useAuth } from "@/store/auth";
import { authHeaders } from "@/lib/api";
import { toast } from "sonner";

// TODO: ajuste para o endpoint real do seu backend (ex.: "/answers/grade")
const GRADE_ENDPOINT = "/answers/grade";

export default function AnswersPage() {
  const token = useAuth((s) => s.token);
  const [examId, setExamId] = useState("1");
  const [classId, setClassId] = useState("10");
  const [studentId, setStudentId] = useState("100");
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<any>(null);

  async function enviar() {
    try {
      if (!file) return toast.error("Escolha um arquivo (imagem/PDF).");
      const form = new FormData();
      form.append("file", file);
      form.append("exam_id", examId);
      form.append("class_id", classId);
      form.append("student_id", studentId);

      const headers = authHeaders(token); // Authorization
      const resp = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}${GRADE_ENDPOINT}`, {
        method: "POST",
        headers,             // NÃO setar Content-Type manualmente em multipart
        body: form,
      });

      const text = await resp.text();
      console.log("[GRADE] STATUS:", resp.status, "BODY:", text);
      if (!resp.ok) return toast.error(text || `Erro ${resp.status}`);

      try { setResult(JSON.parse(text)); } catch { setResult({ raw: text }); }
      toast.success("Correção enviada!");
    } catch (e: any) {
      toast.error(e?.message ?? "Falha ao enviar");
    }
  }

  return (
    <main className="p-6 space-y-4">
      <h1 className="text-xl font-bold">Correção de Cartões</h1>

      <div className="grid gap-2 max-w-md">
        <input className="border p-2 rounded" placeholder="Exam ID" value={examId} onChange={(e) => setExamId(e.target.value)} />
        <input className="border p-2 rounded" placeholder="Class ID" value={classId} onChange={(e) => setClassId(e.target.value)} />
        <input className="border p-2 rounded" placeholder="Student ID" value={studentId} onChange={(e) => setStudentId(e.target.value)} />
        <input className="border p-2 rounded bg-white file:mr-2 file:py-1 file:px-2" type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} />
        <button onClick={enviar} className="bg-blue-600 text-white p-2 rounded">Enviar p/ Correção</button>
      </div>

      <pre className="bg-gray-100 p-3 rounded text-sm overflow-auto">{result ? JSON.stringify(result, null, 2) : "Sem resultado ainda."}</pre>
    </main>
  );
}