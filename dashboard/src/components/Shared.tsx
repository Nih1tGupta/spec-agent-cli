import type { ReactNode } from "react";

export function ExternalLink({
  href,
  children,
}: {
  href?: string | null;
  children: ReactNode;
}) {
  if (!href) return <>{children}</>;
  return (
    <a href={href} target="_blank" rel="noopener noreferrer">
      {children}
    </a>
  );
}

export function WarnBanner({
  title,
  items,
}: {
  title: string;
  items: string[];
}) {
  if (!items.length) return null;
  return (
    <div className="warn-banner">
      <strong>{title}</strong>
      {items.map((item) => (
        <div key={item}>{item}</div>
      ))}
    </div>
  );
}

export function SectionLabel({
  children,
  count,
}: {
  children: ReactNode;
  count?: ReactNode;
}) {
  return (
    <div className="section-label">
      {children}
      {count != null ? <span>{count}</span> : null}
    </div>
  );
}

export function Empty({ children }: { children: ReactNode }) {
  return <div className="empty">{children}</div>;
}

export function StatusPill({ status }: { status: string }) {
  const tone =
    status === "drift" || status === "stale"
      ? status
      : status === "linked" || status === "unlinked"
        ? status
        : "";
  return <span className={`pill ${tone}`.trim()}>{status}</span>;
}
