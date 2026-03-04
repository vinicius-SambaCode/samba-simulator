/**
 * Zustand com persistência em localStorage (chave "samba-auth").
 * Assim o token não some ao recarregar a página.
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
    { name: "samba-auth" }
  )
);