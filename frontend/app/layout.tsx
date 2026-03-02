import "./globals.css";
import Providers from "./providers";

/**
 * RootLayout:
 * - engloba todas as rotas
 * - injeta os providers globais
 */
export const metadata = {
  title: "SAMBA Simulator",
  description: "Frontend MVP integrado ao backend",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body className="bg-gray-50 min-h-screen">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}