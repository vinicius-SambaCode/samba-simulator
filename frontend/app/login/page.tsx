"use client";

import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { useAuth } from "@/store/auth";

/**
 * Página de login compatível com OAuth2PasswordRequestForm do FastAPI.
 * Envia form-data (x-www-form-urlencoded) para a rota /auth/login.
 */
type FormData = { username: string; password: string };

export default function LoginPage() {
  const setToken = useAuth((s) => s.setToken);
  const { register, handleSubmit, formState: { isSubmitting } } = useForm<FormData>();

  async function onSubmit(data: FormData) {
    try {
      const body = new URLSearchParams();
      body.append("username", data.username);
      body.append("password", data.password);

      const resp = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body,
      });

      if (!resp.ok) {
        const j = await resp.json().catch(() => ({}));
        throw new Error(j.detail || `Erro ${resp.status}`);
      }

      const json = await resp.json();
      setToken(json.access_token);
      toast.success("Login realizado!");

      window.location.href = "/";
    } catch (err: any) {
      toast.error(err.message ?? "Erro no login");
    }
  }

  return (
    <main className="min-h-screen flex items-center justify-center">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 p-6 bg-white rounded shadow w-full max-w-sm">
        <h1 className="font-bold text-xl">Entrar</h1>

        <input className="border p-2 w-full rounded" placeholder="Usuário" {...register("username")} />
        <input className="border p-2 w-full rounded" placeholder="Senha" type="password" {...register("password")} />

        <button disabled={isSubmitting} className="bg-blue-600 p-2 rounded text-white w-full disabled:opacity-40">
          {isSubmitting ? "Entrando..." : "Entrar"}
        </button>
      </form>
    </main>
  );
}