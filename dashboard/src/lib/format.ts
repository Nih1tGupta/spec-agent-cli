import type { DriftIssue, GroupedDriftIssue } from "./types";

export function fmt(value?: string | null): string {
  if (!value) return "undated";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export function fmtWhen(value?: string | null): string {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

const BEHAVIOR_LINE = /\b[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d{3}\b/;

function cleanInline(value: string): string {
  return value
    .replace(/^#{1,6}\s*/, "")
    .replace(/\*\*(.*?)\*\*/g, "$1")
    .replace(/`([^`]*)`/g, "$1")
    .replace(/^[-*]\s+/, "")
    .replace(/\s+/g, " ")
    .trim();
}

/** Lines belonging to one behavior/acceptance block (stops before the next ID). */
export function ruleBlockLines(
  source: string,
  id: string,
  acceptance = false,
): string[] {
  const lines = source.split("\n");
  const start = lines.findIndex((line) => line.includes(id));
  if (start < 0) return [];

  const block: string[] = [];
  for (let i = start; i < lines.length; i += 1) {
    const raw = lines[i];
    if (i > start) {
      const otherId = raw.match(BEHAVIOR_LINE)?.[0];
      if (otherId && otherId !== id) break;
      if (acceptance && /^\s*AC-[A-Z0-9-]+/i.test(raw) && !raw.includes(id)) {
        break;
      }
      if (!raw.trim() && block.length > 0) {
        if (block[block.length - 1] === "") break;
        block.push("");
        continue;
      }
    }
    const cleaned = cleanInline(raw);
    if (cleaned) block.push(cleaned);
    if (!acceptance && block.length >= 4) break;
    if (acceptance && block.length >= 8) break;
  }
  return block.filter((line, index, all) => !(line === "" && all[index - 1] === ""));
}

export function ruleText(
  source: string,
  id: string,
  acceptance = false,
): string {
  const lines = ruleBlockLines(source, id, acceptance);
  if (!lines.length) {
    return acceptance
      ? "No acceptance text references this rule."
      : "Rule text is not available in the packet source.";
  }
  return lines.join("\n");
}

/** User-facing labels for machine drift kinds (kind string stays in data/API). */
const DRIFT_KIND_COPY: Record<string, { title: string; guidance: string }> = {
  "code-changed": {
    title: "Linked code was updated",
    guidance:
      "This file changed since the last baseline. Confirm the specification still matches, then refresh traceability.",
  },
  "stale-trace": {
    title: "Code link went missing",
    guidance:
      "A recorded code link moved or disappeared. Restore the backlink, or refresh the baseline after confirming the change.",
  },
  unlinked: {
    title: "Rule has no code link",
    guidance:
      "This approved rule is not linked to implementation. Add spec backlinks in code or tests, then refresh traceability.",
  },
  phantom: {
    title: "Code references an unknown rule",
    guidance:
      "Code points at a behavior ID that is not in the specification. Fix the backlink ID or add the missing rule.",
  },
  unbaselined: {
    title: "New link not in baseline",
    guidance:
      "This backlink is not in the traceability baseline yet. Review it, then refresh traceability.",
  },
  "silent-implementation": {
    title: "Planned rule already in code",
    guidance:
      "A planned rule already has implementation backlinks. Confirm product status or remove premature links.",
  },
  "dead-ref": {
    title: "Broken code reference",
    guidance: "A specification code reference points to a path that no longer exists.",
  },
  "stale-verification": {
    title: "Verification is out of date",
    guidance:
      "Linked code changed after the last verification. Re-verify or update the recorded verification.",
  },
  unknown: {
    title: "Drift finding",
    guidance: "Review this finding against the linked rules and files.",
  },
};

export function driftKindLabel(kind: string): { title: string; guidance: string } {
  return (
    DRIFT_KIND_COPY[kind] || {
      title: kind.replace(/-/g, " "),
      guidance: "Review this finding against the linked rules and files.",
    }
  );
}

export function groupDriftIssues(issues: DriftIssue[]): GroupedDriftIssue[] {
  const groups = new Map<string, GroupedDriftIssue>();
  for (const issue of issues || []) {
    const key = [issue.kind || "", issue.location || "", issue.message || ""].join(
      "\u0000",
    );
    if (!groups.has(key)) {
      groups.set(key, {
        kind: issue.kind || "unknown",
        location: issue.location || "",
        message: issue.message || "",
        behavior_ids: [],
      });
    }
    const id = issue.behavior_id;
    const group = groups.get(key)!;
    if (id && !group.behavior_ids.includes(id)) {
      group.behavior_ids.push(id);
    }
  }
  return [...groups.values()].map((group) => {
    group.behavior_ids.sort();
    return group;
  });
}

export function uniqueByKey<T>(
  items: T[] | undefined,
  keyFn: (item: T) => string | null | undefined,
): T[] {
  const seen = new Set<string>();
  return (items || []).filter((item) => {
    const key = keyFn(item);
    if (!key || seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

export function fileKey(path: string, line?: number | null): string {
  return `${path}::${line ?? ""}`;
}

/** Shorten a path for display: keep end segments, full string stays in title. */
export function shortenPath(path: string, maxChars = 42): string {
  if (path.length <= maxChars) return path;
  const parts = path.split("/");
  if (parts.length <= 2) {
    return `…${path.slice(-(maxChars - 1))}`;
  }
  let result = parts[parts.length - 1];
  for (let i = parts.length - 2; i >= 0; i -= 1) {
    const next = `${parts[i]}/${result}`;
    if (next.length + 1 > maxChars) {
      return `…/${result}`;
    }
    result = next;
  }
  return result;
}
