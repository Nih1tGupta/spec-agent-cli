import type { ReactNode } from "react";
import { shortenPath } from "../lib/format";

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

/**
 * File paths: one line with ellipsis (optionally shortened middle),
 * never mid-word wrap. Full path always on hover.
 */
export function PathText({
  path,
  className = "",
  shorten = true,
}: {
  path: string;
  className?: string;
  shorten?: boolean;
}) {
  const display = shorten ? shortenPath(path) : path;
  return (
    <span className={`path-text ${className}`.trim()} title={path}>
      {display}
    </span>
  );
}

/** Multi-line prose with clear paragraph breaks. */
export function ProseBlock({
  lines,
  className = "",
}: {
  lines: string[];
  className?: string;
}) {
  if (!lines.length) return null;
  return (
    <div className={`prose-block ${className}`.trim()}>
      {lines.map((line, index) =>
        line ? (
          <p key={`${index}-${line.slice(0, 24)}`}>{line}</p>
        ) : (
          <div className="prose-gap" key={`gap-${index}`} />
        ),
      )}
    </div>
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
