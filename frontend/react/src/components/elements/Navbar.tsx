import { Container } from "../shared/Container";
import { useThemeStore } from "../../store/ThemeStore";

export const navItems = [
  { href: "#console", text: "Console" },
  { href: "#pipeline", text: "Pipeline Stages" },
  { href: "#discord", text: "Discord Bot" },
  { href: "#api", text: "API Reference" },
];

export const Navbar = () => {
  const { toggleTheme, theme } = useThemeStore();

  return (
    <header className="sticky top-0 z-50 py-3 bg-body/90 backdrop-blur-md border-b border-box-border transition-colors">
      <Container>
        <nav className="w-full flex items-center justify-between gap-6">
          {/* Logo / Monogram */}
          <div className="flex items-center gap-3">
            <a href="#" className="flex items-center gap-2.5">
              <span className="font-mono text-xs font-bold tracking-wider px-2 py-1 rounded bg-slate-800 text-slate-100 border border-slate-700">
                TG
              </span>
              <div className="flex flex-col">
                <span className="text-base font-bold tracking-tight text-heading-1">
                  ToxiGuard
                </span>
                <span className="text-[10px] font-mono uppercase tracking-wider text-heading-3">
                  25PEC4CS1 NLP Engine
                </span>
              </div>
            </a>
          </div>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center gap-6 text-sm font-medium text-heading-2">
            {navItems.map((item, idx) => (
              <a
                key={idx}
                href={item.href}
                className="hover:text-heading-1 transition-colors"
              >
                {item.text}
              </a>
            ))}
          </div>

          {/* Actions / Theme Toggle */}
          <div className="flex items-center gap-3">
            <div className="hidden sm:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>API Ready</span>
            </div>

            <button
              onClick={toggleTheme}
              aria-label="Toggle theme"
              className="p-2 rounded-lg border border-box-border hover:bg-slate-500/10 text-heading-2 transition-colors cursor-pointer"
            >
              {theme === "dark" ? (
                // Sun icon for light mode switch
                <svg
                  className="w-4 h-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={1.8}
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M12 3v2.25m6.364.386-1.591 1.591M21 12h-2.25m-.386 6.364-1.591-1.591M12 18.75V21m-4.773-4.227-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0Z"
                  />
                </svg>
              ) : (
                // Moon icon for dark mode switch
                <svg
                  className="w-4 h-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={1.8}
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M21.752 15.002A9.72 9.72 0 0 1 18 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 0 0 3 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 0 0 9.002-5.998Z"
                  />
                </svg>
              )}
            </button>
          </div>
        </nav>
      </Container>
    </header>
  );
};
