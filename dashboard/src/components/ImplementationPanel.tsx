import { useEffect, useMemo, type ReactNode } from "react";
import { fileKey, fmt, fmtWhen, ruleText } from "../lib/format";
import type { Backlink, Packet, Snapshot } from "../types";
import { useCodePreview } from "../hooks/useCodePreview";
import { Empty, ExternalLink, SectionLabel, StatusPill } from "./Shared";

function ProvenanceStrip({ packet }: { packet: Packet }) {
  const spec = packet.provenance?.spec;
  const acceptance = packet.provenance?.acceptance;
  return (
    <div className="meta-strip">
      {spec ? (
        <span>
          Spec last changed by <b>{spec.author}</b> · {fmtWhen(spec.date)} ·{" "}
          <ExternalLink href={spec.url}>{spec.commit}</ExternalLink>
          {spec.pr_url ? (
            <>
              {" "}
              · <ExternalLink href={spec.pr_url}>#{spec.pr_number}</ExternalLink>
            </>
          ) : null}
        </span>
      ) : (
        <span>Spec provenance unavailable (uncommitted or no git history)</span>
      )}
      {acceptance ? (
        <span>
          Acceptance · <b>{acceptance.author}</b> ·{" "}
          <ExternalLink href={acceptance.url}>{acceptance.commit}</ExternalLink>
        </span>
      ) : null}
    </div>
  );
}

function RuleDetail({ packet, ruleId }: { packet: Packet; ruleId: string }) {
  const links = packet.behavior_backlinks?.[ruleId] || [];
  const coverage = (packet.coverage || []).find(
    (row) => row.behavior_id === ruleId,
  );
  const status =
    coverage?.status || (links.length ? "linked" : "unlinked");

  return (
    <div className="rule-detail">
      <div className="rule-detail-head">
        <h3>{ruleId}</h3>
        <StatusPill status={status} />
      </div>
      <p>{ruleText(packet.spec, ruleId)}</p>
      <div className="detail-grid">
        <div className="detail-item">
          <small>Acceptance</small>
          <span>{ruleText(packet.acceptance, ruleId, true)}</span>
        </div>
        <div className="detail-item">
          <small>Defined in</small>
          <span>
            {packet.source_dir || `spec/packets/${packet.slug}`}/spec.md
          </span>
        </div>
        <div className="detail-item">
          <small>Backlinks</small>
          <span>
            {links.length
              ? links
                  .map(
                    (link) =>
                      `${link.path}${link.line ? `:${link.line}` : ""}${
                        link.hash_ok === false ? " (stale hash)" : ""
                      }`,
                  )
                  .join(", ")
              : "No backlink recorded"}
          </span>
        </div>
        <div className="detail-item">
          <small>Evolution events</small>
          <span>
            {packet.events.length
              ? packet.events.join(", ")
              : "No linked event"}
          </span>
        </div>
      </div>
    </div>
  );
}

function CodeWindow({
  path,
  line,
  rule,
}: {
  path: string | null;
  line: number | null;
  rule: string | null;
}) {
  const { loading, error, model } = useCodePreview({
    path,
    line,
    rule,
  });

  if (!path) {
    return (
      <div className="code-window plain">No linked code for this rule.</div>
    );
  }
  if (loading) {
    return <div className="code-window plain">Loading {path}…</div>;
  }
  if (error || !model) {
    return (
      <div className="code-window plain">
        {error || "Unable to load file."}
      </div>
    );
  }

  return (
    <div className="code-window">
      <div className="code-toolbar">
        <span>{model.path}</span>
        <em>
          line {model.hitLine}
          {model.lineHint != null ? ` · index line ${model.lineHint}` : ""}
        </em>
      </div>
      {model.lines.map((lineText, index) => {
        const number = model.start + index + 1;
        const isHit =
          number === model.hitLine || lineText.includes(model.needle);
        let body: ReactNode = lineText;
        if (model.needle && lineText.includes(model.needle)) {
          const parts = lineText.split(model.needle);
          body = (
            <>
              {parts.map((part, partIndex) => (
                <span key={`${number}-${partIndex}`}>
                  {part}
                  {partIndex < parts.length - 1 ? (
                    <mark>{model.needle}</mark>
                  ) : null}
                </span>
              ))}
            </>
          );
        }
        return (
          <div
            key={number}
            className={`code-line${isHit ? " hit" : ""}`}
          >
            <span>{number}</span>
            <span>{body}</span>
          </div>
        );
      })}
    </div>
  );
}

export function ImplementationPanel({
  data,
  packet,
  rule,
  file,
  onToggleRule,
  onSelectFile,
  onFileKey,
}: {
  data: Snapshot;
  packet: Packet;
  rule: string | null;
  file: string | null;
  onToggleRule: (id: string) => void;
  onSelectFile: (key: string) => void;
  onFileKey: (key: string) => void;
}) {
  const activeRule =
    rule && packet.behavior_ids.includes(rule)
      ? rule
      : packet.behavior_ids[0] || null;
  const backlinks: Backlink[] = activeRule
    ? packet.behavior_backlinks?.[activeRule] || []
    : [];

  const preferred = useMemo(() => {
    return (
      backlinks.find((link) => fileKey(link.path, link.line) === file) ||
      backlinks[0] ||
      null
    );
  }, [backlinks, file]);

  useEffect(() => {
    if (!preferred) return;
    const key = fileKey(preferred.path, preferred.line);
    if (file !== key) onFileKey(key);
  }, [preferred, file, onFileKey]);

  const packetDriftCount = data.drift.issues.filter((issue) =>
    packet.behavior_ids.includes(issue.behavior_id),
  ).length;

  return (
    <main id="main-panel" className="panel evidence-panel view-active">
      <div className="kicker">Implementation</div>
      <div className="evidence-head">
        <div>
          <h1 className="page-title">{packet.title}</h1>
          <p className="lead">
            Select a rule to inspect its definition, backlinks, and code
            evidence.
          </p>
        </div>
        <span className="status">{packet.status}</span>
      </div>
      <ProvenanceStrip packet={packet} />
      <div className="metric-row">
        <div className="metric">
          <b>{packet.behavior_ids.length}</b>
          <span>rules</span>
        </div>
        <div className="metric">
          <b>{backlinks.length}</b>
          <span>links for rule</span>
        </div>
        <div className="metric">
          <b>{packet.events.length}</b>
          <span>events</span>
        </div>
        <div className="metric">
          <b>{packetDriftCount}</b>
          <span>drift findings</span>
        </div>
      </div>

      <SectionLabel count={packet.behavior_ids.length}>Rules</SectionLabel>
      <div className="rule-row">
        {packet.behavior_ids.length ? (
          packet.behavior_ids.map((id) => (
            <button
              key={id}
              type="button"
              className={`rule-anchor ${id === activeRule ? "active" : ""}`}
              onClick={() => onToggleRule(id)}
            >
              {id}
            </button>
          ))
        ) : (
          <span className="muted">No behavior IDs linked.</span>
        )}
      </div>

      <div className="impl-grid">
        <div>
          {activeRule ? (
            <RuleDetail packet={packet} ruleId={activeRule} />
          ) : (
            <Empty>Select a rule.</Empty>
          )}
        </div>
        <div className="impl-side">
          <SectionLabel count={backlinks.length}>Linked code</SectionLabel>
          <div className="file-list">
            {backlinks.length ? (
              backlinks.map((link) => {
                const key = fileKey(link.path, link.line);
                const label = link.line
                  ? `${link.path}:${link.line}`
                  : link.path;
                const stale = link.hash_ok === false;
                return (
                  <button
                    key={key}
                    type="button"
                    className={`file-button ${file === key ? "active" : ""} ${
                      stale ? "stale" : ""
                    }`}
                    onClick={() => onSelectFile(key)}
                  >
                    {label}
                    <span className="file-meta">
                      {stale
                        ? "Stale hash"
                        : link.hash_ok === true
                          ? "Hash ok"
                          : "Hash unchecked"}
                    </span>
                  </button>
                );
              })
            ) : (
              <Empty>No linked implementation evidence for this rule.</Empty>
            )}
          </div>
          <CodeWindow
            path={preferred?.path ?? null}
            line={preferred?.line ?? null}
            rule={activeRule}
          />
        </div>
      </div>

      {(packet.open_follow_ups || []).length ? (
        <>
          <SectionLabel count={packet.open_follow_ups!.length}>
            Open follow-ups
          </SectionLabel>
          <div className="side-card">
            <div className="history">
              {packet.open_follow_ups!.map((item) => (
                <div className="history-item" key={item.event_id}>
                  <div>
                    <strong>{item.event_id}</strong>
                    <small>
                      {item.actor || "actor"} · {fmt(item.timestamp)}
                    </small>
                    <p className="muted">{item.follow_ups}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      ) : null}
    </main>
  );
}
