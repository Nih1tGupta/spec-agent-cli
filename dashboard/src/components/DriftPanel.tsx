import { useMemo } from "react";
import { groupDriftIssues, uniqueByKey } from "../lib/format";
import type { Snapshot } from "../types";
import {
  Empty,
  ExternalLink,
  PathText,
  SectionLabel,
  Truncate,
  WarnBanner,
} from "./Shared";

export function DriftPanel({
  data,
  onJumpToBehavior,
}: {
  data: Snapshot;
  onJumpToBehavior: (id: string) => void;
}) {
  const grouped = useMemo(
    () => groupDriftIssues(data.drift.issues || []),
    [data.drift.issues],
  );
  const changes = useMemo(
    () =>
      uniqueByKey(
        data.recent_changes || [],
        (change) => change.full_id || change.id,
      ),
    [data.recent_changes],
  );
  const rawCount = (data.drift.issues || []).length;
  const baseline = data.traceability.baseline_commit;

  return (
    <main id="main-panel" className="panel evidence-panel view-active">
      <div className="kicker">Evidence integrity</div>
      <div className="evidence-head">
        <div>
          <h1 className="page-title">Drift &amp; freshness</h1>
          <p className="lead">
            Structural drift, hash freshness against the traceability index, and
            recent specification commits.
          </p>
        </div>
        <span
          className={`status ${data.drift.status === "drift" ? "drift" : ""}`}
        >
          {data.drift.status}
        </span>
      </div>

      <div className="meta-strip">
        <span>
          Baseline{" "}
          {baseline ? (
            <ExternalLink href={data.traceability.baseline_url}>
              {baseline.slice(0, 12)}
            </ExternalLink>
          ) : (
            "—"
          )}
        </span>
        <span>
          Behaviors indexed <b>{data.traceability.behavior_count}</b>
        </span>
        <span>
          Linked files <b>{data.traceability.linked_file_count}</b>
        </span>
        <span>
          Hash mismatches <b>{data.traceability.hash_mismatches || 0}</b>
        </span>
        {data.drift.error ? (
          <span>Checker error · {data.drift.error}</span>
        ) : null}
      </div>

      {(data.warnings || []).length ? (
        <WarnBanner title="Warnings" items={data.warnings} />
      ) : null}

      <SectionLabel
        count={
          <>
            {grouped.length}
            {rawCount !== grouped.length ? ` · ${rawCount} findings` : ""}
          </>
        }
      >
        Drift issues
      </SectionLabel>
      <div className="side-card">
        {grouped.length ? (
          <div className="scroll-pane scroll-pane-tall issue-card-list">
            {grouped.map((issue) => (
              <article
                className="issue-card"
                key={`${issue.kind}|${issue.location}|${issue.message}`}
              >
                <header className="issue-card-head">
                  <span className="issue-kind mono">{issue.kind}</span>
                  <p className="issue-message">{issue.message}</p>
                </header>
                {issue.location ? (
                  <div className="issue-meta">
                    <small>Location</small>
                    <PathText path={issue.location} />
                  </div>
                ) : null}
                <div className="issue-meta">
                  <small>Behaviors</small>
                  <div className="behavior-chip-row">
                    {(issue.behavior_ids.length
                      ? issue.behavior_ids
                      : ["—"]
                    ).map((id) =>
                      id === "—" ? (
                        <span className="mono" key={id}>
                          {id}
                        </span>
                      ) : (
                        <button
                          key={id}
                          type="button"
                          className="behavior-chip"
                          title={id}
                          onClick={() => onJumpToBehavior(id)}
                        >
                          {id}
                        </button>
                      ),
                    )}
                  </div>
                </div>
              </article>
            ))}
          </div>
        ) : (
          <Empty>No structural drift detected.</Empty>
        )}
      </div>

      <SectionLabel count={changes.length}>
        Recent specification commits
      </SectionLabel>
      <div className="side-card">
        <div
          className="change-list scroll-pane"
          role="region"
          aria-label="Recent specification commits"
        >
          {changes.length ? (
            changes.map((change) => (
              <div className="change-row" key={change.full_id || change.id}>
                <div className="change-sha">
                  {change.url ? (
                    <a
                      className="sha"
                      href={change.url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {change.id}
                    </a>
                  ) : (
                    <span className="sha">{change.id}</span>
                  )}
                  {change.pr_url ? (
                    <>
                      {" "}
                      ·{" "}
                      <a
                        className="sha"
                        href={change.pr_url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        #{change.pr_number}
                      </a>
                    </>
                  ) : null}
                </div>
                <div className="subject" title={change.subject}>
                  <Truncate>{change.subject}</Truncate>
                </div>
                <div
                  className="who"
                  title={`${change.author || ""} · ${change.date || ""}`}
                >
                  {change.author || ""} · {change.date || ""}
                </div>
              </div>
            ))
          ) : (
            <Empty>No recent commits found.</Empty>
          )}
        </div>
      </div>
    </main>
  );
}
