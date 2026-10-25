interface ButtonProps {
  className?: string;
  children: React.ReactNode;
  onClick?: () => void;
  type?: "button" | "submit" | "reset";
}

export const Button = ({ onClick, children, className = "", type = "button" }: ButtonProps) => {
  return (
    <button
      type={type}
      onClick={onClick}
      className={`px-6 py-3 rounded-full outline-none cursor-pointer
                 relative overflow-hidden border border-transparent bg-violet-600 ${className}`}
    >
      {children}
    </button>
  );
};
