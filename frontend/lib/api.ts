export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "";

export function authHeaders(token: string | null): Headers {
  const h = new Headers();
  h.set("Accept", "application/json");
  if (token) h.set("Authorization", `Bearer ${token.trim()}`);
  return h;
}

function joinBase(base: string, path: string): string {
  if (!base) return path;
  const b = base.endsWith("/") ? base.slice(0, -1) : base;
  const p = path.startsWith("/") ? path : `/${path}`;
  return `${b}${p}`;
}

export async function authFetch(
  path: string,
  init: RequestInit,
  token: string | null
): Promise<Response> {
  const baseHeaders = authHeaders(token);
  const incoming = new Headers(init?.headers || {});
  incoming.forEach((value, key) => baseHeaders.set(key, value));

  const url = joinBase(API_BASE, path);
  const resp = await fetch(url, { ...init, headers: baseHeaders });

  if (resp.status === 401) {
    try { localStorage.removeItem("samba-auth"); } catch {}
    if (typeof window !== "undefined") window.location.href = "/login";
  }
  return resp;
}