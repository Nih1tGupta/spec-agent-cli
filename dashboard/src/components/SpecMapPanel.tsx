import type { Packet, Snapshot } from "../types";
import { Empty, WarnBanner } from "./Shared";

function packetHint(packet: Packet): string {
  const coverage = packet.coverage || [];
  const driftN = coverage.filter(
    (row) => row.status === "drift" || row.status === "stale",
  ).length;
  const unlinked = coverage.filter((row) => row.status === "unlinked").length;
  if (driftN) return `${driftN} attention`;
  if (unlinked) return `${unlinked} unlinked`;
  return `${packet.behavior_ids.length} rules`;
}

export function SpecMapPanel({
  data,
  selected,
  onSelect,
}: {
  data: Snapshot;
  selected: string | null;
  onSelect: (slug: string) => void;
}) {
  const warnings = data.warnings || [];
  const traceError = data.traceability?.error;

  return (
    <aside id="packet-panel" className="panel left-panel view-active">
      <div className="kicker">Specification</div>
      <div className="project-card">
        <small>Project</small>
        <h1 className="page-title">{data.project.title}</h1>
        <small>
          Status · {data.project.status}
          {data.project.head_commit
            ? ` · HEAD ${data.project.head_commit}`
            : ""}
        </small>
      </div>

      {warnings.length ? (
        <WarnBanner title="Data warnings" items={warnings} />
      ) : traceError ? (
        <WarnBanner title="Traceability" items={[traceError]} />
      ) : null}

      <div className="section-label">
        Packets <span>{data.packets.length}</span>
      </div>
      <div className="packet-list">
        {data.packets.length ? (
          data.packets.map((packet) => (
            <button
              key={packet.slug}
              type="button"
              className={`packet ${packet.slug === selected ? "active" : ""}`}
              onClick={() => onSelect(packet.slug)}
            >
              <strong>{packet.title}</strong>
              <small>
                {packet.status} · {packetHint(packet)}
              </small>
            </button>
          ))
        ) : (
          <Empty>No packets yet</Empty>
        )}
      </div>
    </aside>
  );
}
