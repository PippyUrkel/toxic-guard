import { useEffect } from "react";
import { Footer } from "./elements/Footer";
import { Navbar } from "./elements/Navbar";

interface LayoutProps {
  title: string;
  children: React.ReactNode;
}

export const Layout = ({ title, children }: LayoutProps) => {
  useEffect(() => {
    document.title = title;
  }, [title]);
  return (
    <div className="min-h-screen flex flex-col bg-body text-heading-2 transition-colors">
      <Navbar />

      <main className="flex-1 flex flex-col gap-y-6">
        {children}
      </main>

      <Footer />
    </div>
  );
};
