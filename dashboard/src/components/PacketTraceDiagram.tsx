import type { ReactNode } from "react";
import type { EvolutionEvent, Packet } from "../types";
import { Truncate } from "./Shared";

type NodeKind = "authored" | "decision" | "rules" | "observed";

function shortenId(value: string, max = 28): string {
  if (value.length <= max) return value;
  const head = Math.ceil((max - 1) / 2);
  const tail = Math.floor((max - 1) / 2);
  return `${value.slice(0, head)}…${value.slice(-tail)}`;
}

function FlowArrow() {
  return (
    <div className="flow-arrow" aria-hidden="true">
      <span className="flow-arrow-line" />
      <span className="flow-arrow-head" />
    </div>
  );
}

function FlowNode({
  kind,
  label,
  active,
  onClick,
  children,
}: {
  kind: NodeKind;
  label: string;
  active?: boolean;
  onClick?: () => void;
  children: ReactNode;
}) {
  const className = `flow-node flow-node-${kind}${active ? " active" : ""}${
    onClick ? " interactive" : ""
  }`;

  if (onClick) {
    return (
      <button type="button" className={className} onClick={onClick}>
        <span className="flow-node-label">{label}</span>
        <div className="flow-node-body">{children}</div>
      </button>
    );
  }

  return (
    <div className={className}>
      <span className="flow-node-label">{label}</span>
      <div className="flow-node-body">{children}</div>
    </div>
  );
}

export function PacketTraceDiagram({
  packet,
  event,
  onSelectEvent,
  onJumpToBehavior,
  onOpenImplementation,
}: {
  packet: Packet | null;
  event: EvolutionEvent | null;
  onSelectEvent?: (id: string) => void;
  onJumpToBehavior?: (id: string) => void;
  onOpenImplementation?: () => void;
}) {
  const eventId = event?.id || packet?.event_details?.[0]?.id || "event";
  const ruleIds = packet?.behavior_ids || [];
  const shownRules = ruleIds.slice(0, 2);
  const extraRules = Math.max(0, ruleIds.length - shownRules.length);
  const fileCount = packet?.linked_files.length || 0;
  const packetPath = packet?.source_dir || "specification packet";

  return (
    <div className="flow-diagram" role="img" aria-label="Packet evidence flow">
      <div className="flow-rail">
        <FlowNode kind="authored" label="Authored">
          <strong>spec.md</strong>
          <small title={packetPath}>
            <Truncate>{packetPath}</Truncate>
          </small>
        </FlowNode>

        <FlowArrow />

        <FlowNode
          kind="decision"
          label="Decision"
          active={Boolean(event)}
          onClick={
            event?.id && onSelectEvent
              ? () => onSelectEvent(event.id)
              : undefined
          }
        >
          <strong title={eventId}>{shortenId(eventId)}</strong>
          <small title={event?.task_type || undefined}>
            <Truncate>{event?.task_type || "recorded decision"}</Truncate>
          </small>
        </FlowNode>

        <FlowArrow />

        <FlowNode kind="rules" label="Rules">
          {shownRules.length ? (
            <div className="flow-rule-stack">
              {shownRules.map((id) =>
                onJumpToBehavior ? (
                  <button
                    key={id}
                    type="button"
                    className="flow-rule-chip"
                    title={id}
                    onClick={(e) => {
                      e.stopPropagation();
                      onJumpToBehavior(id);
                    }}
                  >
                    {shortenId(id, 22)}
                  </button>
                ) : (
                  <span key={id} className="flow-rule-chip" title={id}>
                    {shortenId(id, 22)}
                  </span>
                ),
              )}
              {extraRules ? (
                <span
                  className="flow-rule-more"
                  title={ruleIds.slice(2).join(", ")}
                >
                  +{extraRules} more
                </span>
              ) : null}
            </div>
          ) : (
            <strong>behavior IDs</strong>
          )}
        </FlowNode>

        <FlowArrow />

        <FlowNode
          kind="observed"
          label="Observed"
          onClick={onOpenImplementation}
        >
          <strong>
            {fileCount} code file{fileCount === 1 ? "" : "s"}
          </strong>
          <small>implementation backlinks</small>
        </FlowNode>
      </div>
    </div>
  );
}
