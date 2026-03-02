/**
 * Estado global de autenticação (Zustand) **com persistência** (localStorage).
 * Isso evita perder o token ao recarregar ou navegar.
 */
import { create } from "zustand";
import { persist } from "zustand/middleware";

type AuthState = {
  token: string | null;
  setToken: (t: string | null) => void;
};

export const useAuth = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      setToken: (t) => set({ token: t }),
    }),
    { name: "samba-auth" } // chave no localStorage
  )
);