import type { ReactNode } from "react";
import type { EvolutionEvent, Packet } from "../types";

type NodeKind = "authored" | "decision" | "rules" | "observed";

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
  const shownRules = ruleIds.slice(0, 3);
  const extraRules = Math.max(0, ruleIds.length - shownRules.length);
  const fileCount = packet?.linked_files.length || 0;

  return (
    <div className="flow-diagram" role="img" aria-label="Packet evidence flow">
      <div className="flow-rail">
        <FlowNode kind="authored" label="Authored">
          <strong>spec.md</strong>
          <small>{packet?.source_dir || "specification packet"}</small>
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
          <strong title={eventId}>{eventId}</strong>
          <small>{event?.task_type || "recorded decision"}</small>
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
                    onClick={(e) => {
                      e.stopPropagation();
                      onJumpToBehavior(id);
                    }}
                  >
                    {id}
                  </button>
                ) : (
                  <span key={id} className="flow-rule-chip">
                    {id}
                  </span>
                ),
              )}
              {extraRules ? (
                <span className="flow-rule-more">+{extraRules}</span>
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
