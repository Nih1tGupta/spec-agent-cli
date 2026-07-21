import { useMemo } from "react";
import { fmt, fmtWhen, uniqueByKey } from "../lib/format";
import type { EvolutionEvent, Packet, Snapshot } from "../types";
import { PacketTraceDiagram } from "./PacketTraceDiagram";
import { Empty, ExternalLink } from "./Shared";

function EventDrawer({ event }: { event: EvolutionEvent | null }) {
  if (!event) return <Empty>Select an evolution event.</Empty>;

  const files = (event.spec_files || []).join("\n") || "—";
  const rules = (event.behavior_ids || []).length ? (
    <div className="id-grid">
      {(event.behavior_ids || []).map((id) => (
        <span className="pill linked" title={id} key={id}>
          {id}
        </span>
      ))}
    </div>
  ) : (
    "—"
  );

  return (
    <div className="event-drawer">
      <h3>{event.title || event.id}</h3>
      <div className="drawer-meta">
        <span className="event-id">{event.id || "event"}</span>
        {" · "}
        {fmtWhen(event.timestamp)}
        {" · "}
        {event.task_type || "decision"}
        {" · "}
        {event.status || "recorded"}
      </div>
      <div className="drawer-grid scroll-pane scroll-pane-drawer">
        <div className="drawer-item">
          <small>Actor</small>
          <span>{event.actor || "—"}</span>
        </div>
        <div className="drawer-item">
          <small>Supersedes</small>
          <span>{event.supersedes || "none"}</span>
        </div>
        <div className="drawer-item wide">
          <small>User intent</small>
          <p>{event.user_intent || "—"}</p>
        </div>
        <div className="drawer-item wide">
          <small>Decision</small>
          <p>{event.decision || "—"}</p>
        </div>
        <div className="drawer-item wide">
          <small>Rationale</small>
          <p>{event.rationale || "—"}</p>
        </div>
        <div className="drawer-item wide">
          <small>Specification delta</small>
          <p>{event.spec_delta || "—"}</p>
        </div>
        <div className="drawer-item wide">
          <small>Assumptions</small>
          <p>{event.assumptions || "—"}</p>
        </div>
        <div className="drawer-item wide">
          <small>Follow-ups</small>
          <p>{event.follow_ups || "—"}</p>
        </div>
        <div className="drawer-item wide">
          <small>Spec files</small>
          <span className="mono-block" style={{ whiteSpace: "pre-wrap" }}>
            {files}
          </span>
        </div>
        <div className="drawer-item wide">
          <small>Behavior IDs</small>
          {rules}
        </div>
      </div>
    </div>
  );
}

export function EvolutionPanel({
  data,
  selected,
  eventId,
  onSelectPacket,
  onSelectEvent,
  onJumpToBehavior,
  onOpenImplementation,
}: {
  data: Snapshot;
  selected: Packet | null;
  eventId: string | null;
  onSelectPacket: (slug: string) => void;
  onSelectEvent: (id: string) => void;
  onJumpToBehavior: (id: string) => void;
  onOpenImplementation: () => void;
}) {
  const events = useMemo(
    () =>
      uniqueByKey(
        selected?.event_details?.length
          ? selected.event_details
          : data.events,
        (event) => event.id,
      ),
    [selected, data.events],
  );

  const activeEvent =
    events.find((event) => event.id === eventId) || events[0] || null;
  const follow = selected?.open_follow_ups?.[0]?.follow_ups;

  return (
    <section id="visual-panel" className="panel right-panel view-active">
      <div className="right-heading">
        <div>
          <div className="kicker">Evolution</div>
          <h1 className="page-title">Evidence map</h1>
        </div>
        <span className="readonly">Read-only</span>
      </div>

      <div className="evolution-layout">
        <aside className="evolution-sidebar">
          <div className="section-label">Packet</div>
          <div
            className="scroll-pane"
            role="region"
            aria-label="Evolution packets"
          >
            {data.packets.length ? (
              data.packets.map((packet) => (
                <button
                  key={packet.slug}
                  type="button"
                  className={`evolution-item ${
                    packet.slug === selected?.slug ? "active" : ""
                  }`}
                  onClick={() => onSelectPacket(packet.slug)}
                >
                  <strong>{packet.title}</strong>
                  <small>
                    {packet.events.length} events · {packet.behavior_ids.length}{" "}
                    rules
                  </small>
                </button>
              ))
            ) : (
              <Empty>No packets.</Empty>
            )}
          </div>
        </aside>

        <div className="evolution-content">
          <div className="side-card">
            <h3>{selected?.title || "Spec"} · decisions</h3>
            <div
              className="event-list scroll-pane scroll-pane-tall"
              role="region"
              aria-label="Evolution decisions"
            >
              {events.length ? (
                events.map((event) => (
                  <button
                    key={event.id}
                    type="button"
                    className={`event-card ${
                      event.id === activeEvent?.id ? "active" : ""
                    }`}
                    onClick={() => onSelectEvent(event.id)}
                  >
                    <strong>{event.title || event.id}</strong>
                    <small>
                      {event.id} · {fmt(event.timestamp)} ·{" "}
                      {event.actor || "actor"}
                    </small>
                  </button>
                ))
              ) : (
                <Empty>No evolution events linked to this packet.</Empty>
              )}
            </div>
          </div>

          <EventDrawer event={activeEvent} />

          <div className="side-card">
            <h3>What this packet became</h3>
            <div role="region" aria-label="Packet trace">
              <PacketTraceDiagram
                packet={selected}
                event={activeEvent}
                onSelectEvent={onSelectEvent}
                onJumpToBehavior={onJumpToBehavior}
                onOpenImplementation={onOpenImplementation}
              />
              <p className="trace-caption">
                {follow ||
                  "Authored specification → recorded event → stable behavior rules → observable implementation backlinks."}
              </p>
              {selected?.provenance?.spec ? (
                <p className="trace-caption">
                  Last spec edit: {selected.provenance.spec.author} ·{" "}
                  <ExternalLink href={selected.provenance.spec.url}>
                    {selected.provenance.spec.commit}
                  </ExternalLink>
                </p>
              ) : null}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
