import { useMemo, useState } from "react";
import { driftKindLabel, groupDriftIssues, uniqueByKey } from "../lib/format";
import type { Snapshot } from "../types";
import {
  Empty,
  ExternalLink,
  PathText,
  SectionLabel,
  Truncate,
  WarnBanner,
} from "./Shared";

const RULES_COLLAPSED = 3;

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
  const [expandedRules, setExpandedRules] = useState<Record<string, boolean>>(
    {},
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
          <div
            className="issue-scroll scroll-pane scroll-pane-tall"
            role="region"
            aria-label="Drift issues"
          >
            <table className="issue-table">
              <thead>
                <tr>
                  <th className="col-kind">Issue</th>
                  <th className="col-location">Location</th>
                  <th className="col-behaviors">Affected rules</th>
                  <th className="col-message">What to do</th>
                </tr>
              </thead>
              <tbody>
                {grouped.map((issue) => {
                  const copy = driftKindLabel(issue.kind);
                  const rowKey = `${issue.kind}|${issue.location}|${issue.message}`;
                  const rules = issue.behavior_ids;
                  const expanded = Boolean(expandedRules[rowKey]);
                  const shown = expanded
                    ? rules
                    : rules.slice(0, RULES_COLLAPSED);
                  const hidden = Math.max(0, rules.length - shown.length);

                  return (
                    <tr key={rowKey}>
                      <td className="col-kind">
                        <Truncate
                          title={`${copy.title} (${issue.kind})`}
                          className="issue-table-title"
                        >
                          {copy.title}
                        </Truncate>
                      </td>
                      <td className="col-location">
                        {issue.location ? (
                          <PathText path={issue.location} />
                        ) : (
                          <span className="muted">—</span>
                        )}
                      </td>
                      <td className="col-behaviors">
                        {rules.length ? (
                          <div
                            className={`issue-rules${expanded ? " expanded" : ""}`}
                          >
                            {shown.map((id) => (
                              <button
                                key={id}
                                type="button"
                                className="behavior-chip"
                                title={id}
                                onClick={() => onJumpToBehavior(id)}
                              >
                                {id}
                              </button>
                            ))}
                            {hidden > 0 ? (
                              <button
                                type="button"
                                className="behavior-more"
                                title={rules.slice(RULES_COLLAPSED).join(", ")}
                                onClick={() =>
                                  setExpandedRules((prev) => ({
                                    ...prev,
                                    [rowKey]: true,
                                  }))
                                }
                              >
                                +{hidden}
                              </button>
                            ) : null}
                            {expanded && rules.length > RULES_COLLAPSED ? (
                              <button
                                type="button"
                                className="behavior-more"
                                onClick={() =>
                                  setExpandedRules((prev) => ({
                                    ...prev,
                                    [rowKey]: false,
                                  }))
                                }
                              >
                                Show less
                              </button>
                            ) : null}
                          </div>
                        ) : (
                          <span className="muted">—</span>
                        )}
                      </td>
                      <td className="col-message">
                        <Truncate title={copy.guidance}>{copy.guidance}</Truncate>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
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
