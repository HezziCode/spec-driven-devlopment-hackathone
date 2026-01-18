import type { Metadata, Viewport } from "next";
import { IBM_Plex_Sans, DM_Sans } from "next/font/google";
import "./globals.css";

// IBM Plex Sans for UI/body text - extremely legible and professional
const ibmPlexSans = IBM_Plex_Sans({
  variable: "--font-ibm-plex-sans",
  subsets: ["latin"],
  weight: ["100", "200", "300", "400", "500", "600", "700"],
  display: "swap",
});

// DM Sans for headings - clean and distinctive but professional
const dmSans = DM_Sans({
  variable: "--font-dm-sans",
  subsets: ["latin"],
  weight: ["400", "500", "700"],
  display: "swap",
  style: ["normal"],
});

export const metadata: Metadata = {
  title: "TaskFlow - Modern Task Management",
  description: "The minimalist, modern way to manage your tasks",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark overflow-x-hidden">
      <body
        className={`${ibmPlexSans.variable} ${dmSans.variable} antialiased bg-slate-900 overflow-x-hidden`}
      >
        {children}
      </body>
    </html>
  );
}
