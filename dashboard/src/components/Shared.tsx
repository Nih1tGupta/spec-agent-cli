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

/** Single-line truncation; full value available via native tooltip. */
export function Truncate({
  children,
  title,
  className = "",
}: {
  children: ReactNode;
  title?: string;
  className?: string;
}) {
  const tip =
    title ?? (typeof children === "string" ? children : undefined);
  return (
    <span className={`truncate ${className}`.trim()} title={tip}>
      {children}
    </span>
  );
}

/** Paths/IDs: prefer breaking at separators; still truncate if needed. */
export function PathText({
  path,
  className = "",
}: {
  path: string;
  className?: string;
}) {
  return (
    <span className={`path-text ${className}`.trim()} title={path}>
      {path}
    </span>
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
