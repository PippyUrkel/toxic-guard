import { Container } from "../shared/Container";
import { navItems } from "./Navbar";

export const Footer = () => {
  return (
    <footer className="mt-20 border-t border-box-border bg-box-bg/50 py-10 text-xs text-heading-3">
      <Container>
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
          <div className="space-y-1">
            <div className="flex items-center gap-2 font-mono font-semibold text-heading-1 text-sm">
              <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-200 border border-slate-700 text-[10px]">
                25PEC4CS1
              </span>
              <span>ToxiGuard Linguistic & Classification Engine</span>
            </div>
            <p className="text-heading-3">
              Department of Computer Engineering • Fr. Conceicao Rodrigues College of Engineering, Mumbai
            </p>
            <p className="font-mono text-[11px] text-heading-3/80">
              Stack: Python 3.11 • PyTorch / TensorFlow BiLSTM • NLTK WordNet • Discord.py API • Vite React TS
            </p>
          </div>

          <div className="flex flex-wrap gap-5">
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
        </div>
      </Container>
    </footer>
  );
};
