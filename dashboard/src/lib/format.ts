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

export function cleanMarkdown(value?: string | null): string {
  return String(value || "")
    .replace(/^#{1,6}\s*/gm, "")
    .replace(/\*\*(.*?)\*\*/g, "$1")
    .replace(/`([^`]*)`/g, "$1")
    .replace(/\s+/g, " ")
    .trim();
}

export function ruleText(
  source: string,
  id: string,
  acceptance = false,
): string {
  const lines = source.split("\n");
  const index = lines.findIndex((line) => line.includes(id));
  if (index < 0) {
    return acceptance
      ? "No acceptance text references this rule."
      : "Rule text is not available in the packet source.";
  }
  return cleanMarkdown(
    lines.slice(index, Math.min(index + 3, lines.length)).join(" "),
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
