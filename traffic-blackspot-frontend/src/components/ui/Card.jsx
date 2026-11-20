export default function Card({ children, className = '', style, ...props }) {
  return (
    <div
      className={`glass rounded-xl p-4 ${className}`}
      style={style}
      {...props}
    >
      {children}
    </div>
  );
}
