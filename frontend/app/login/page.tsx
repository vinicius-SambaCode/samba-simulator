"use client";

import { useForm } from "react-hook-form";
import { useAuth } from "@/store/auth";
import { toast } from "sonner";

type FormData = { username: string; password: string };

export default function LoginPage() {
  const setToken = useAuth((s) => s.setToken);
  const { register, handleSubmit, formState: { isSubmitting } } = useForm<FormData>();

  async function onSubmit(data: FormData) {
    try {
      const body = new URLSearchParams();
      body.append("username", data.username);
      body.append("password", data.password);

      const url = `${process.env.NEXT_PUBLIC_API_BASE_URL}/auth/login`;
      const resp = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body,
      });

      const text = await resp.text();
      if (!resp.ok) throw new Error(JSON.parse(text)?.detail || `Erro ${resp.status}`);
      const json = JSON.parse(text);
      if (!json?.access_token) throw new Error("Resposta sem access_token");

      setToken(json.access_token);
      toast.success("Login realizado!");
      window.location.href = "/";
    } catch (e: any) {
      toast.error(e?.message ?? "Falha no login");
    }
  }

  return (
    <main className="min-h-screen flex items-center justify-center">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 p-6 bg-white rounded shadow w-full max-w-sm">
        <h1 className="font-bold text-xl">Entrar</h1>
        <input className="border p-2 w-full rounded" placeholder="Usuário/email" {...register("username")} />
        <input className="border p-2 w-full rounded" placeholder="Senha" type="password" {...register("password")} />
        <button disabled={isSubmitting} className="bg-blue-600 text-white p-2 w-full rounded disabled:opacity-40">
          {isSubmitting ? "Entrando..." : "Entrar"}
        </button>
      </form>
    </main>
  );
}