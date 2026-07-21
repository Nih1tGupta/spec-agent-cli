import type { ReactNode } from "react";
import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
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
 * Full-cell hover tip with a short delay (default 500ms).
 * Renders a fixed popup so scroll parents do not clip it.
 */
export function CellTip({
  text,
  children,
  className = "",
  delayMs = 500,
}: {
  text: string;
  children: ReactNode;
  className?: string;
  delayMs?: number;
}) {
  const hitRef = useRef<HTMLDivElement>(null);
  const timerRef = useRef<number | null>(null);
  const [open, setOpen] = useState(false);
  const [pos, setPos] = useState({ top: 0, left: 0, width: 280 });

  const clearTimer = () => {
    if (timerRef.current != null) {
      window.clearTimeout(timerRef.current);
      timerRef.current = null;
    }
  };

  const hide = () => {
    clearTimer();
    setOpen(false);
  };

  const showSoon = () => {
    clearTimer();
    timerRef.current = window.setTimeout(() => {
      const rect = hitRef.current?.getBoundingClientRect();
      if (!rect) return;
      const maxWidth = Math.min(360, window.innerWidth - 24);
      const left = Math.max(
        12,
        Math.min(rect.left, window.innerWidth - maxWidth - 12),
      );
      const below = rect.bottom + 8;
      const estimatedHeight = 72;
      const top =
        below + estimatedHeight > window.innerHeight - 8
          ? Math.max(8, rect.top - estimatedHeight - 8)
          : below;
      setPos({ top, left, width: Math.max(rect.width, 200) });
      setOpen(true);
    }, delayMs);
  };

  useEffect(() => () => clearTimer(), []);

  return (
    <>
      <div
        ref={hitRef}
        className={`cell-tip-hit ${className}`.trim()}
        onMouseEnter={showSoon}
        onMouseLeave={hide}
        onFocus={showSoon}
        onBlur={hide}
      >
        {children}
      </div>
      {open && text
        ? createPortal(
            <div
              className="cell-tip-popup"
              style={{
                top: pos.top,
                left: pos.left,
                maxWidth: Math.min(360, window.innerWidth - 24),
                minWidth: Math.min(pos.width, 360),
              }}
              role="tooltip"
            >
              {text}
            </div>,
            document.body,
          )
        : null}
    </>
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
