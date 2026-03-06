import type { Metadata } from "next";
import { Bricolage_Grotesque } from "next/font/google";
import Image from "next/image";
import { ChatAssistant } from "@/components/ChatAssistant";
import "./globals.css";

const bricolage = Bricolage_Grotesque({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-bricolage",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Batiora - Quality Products Scanner",
  description: "Find the purest food products at the best prices",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${bricolage.variable} font-sans min-h-screen bg-[#f9f6ee] text-[#282828] antialiased`}>
        <header className="border-b border-[#e7e7e7] bg-[#f6edd9] px-6 py-3">
          <div className="mx-auto flex max-w-6xl items-center justify-between">
            <a href="/">
              <Image
                src="https://cdn.shopify.com/s/files/1/0655/8131/8340/files/logo-desktop_4bbfadb8-a6c8-41bf-8393-7b50dc7d71c2.png?v=1752899007"
                alt="Batiora"
                width={160}
                height={48}
                className="h-12 w-auto object-contain"
                unoptimized
              />
            </a>
            <nav className="flex gap-6 text-sm font-medium text-[#282828]">
              <a href="/" className="transition-colors hover:text-[#d2b777]">Search</a>
              <a href="/trends" className="transition-colors hover:text-[#d2b777]">Trends</a>
              <a href="/jobs" className="transition-colors hover:text-[#d2b777]">Crawl Jobs</a>
            </nav>
          </div>
        </header>
        <main className="mx-auto max-w-6xl px-6 py-8">{children}</main>
        <ChatAssistant />
      </body>
    </html>
  );
}
