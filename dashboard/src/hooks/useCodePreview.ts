import { useEffect, useState } from "react";

export interface CodeWindowModel {
  path: string;
  hitLine: number;
  lineHint: number | null;
  start: number;
  end: number;
  lines: string[];
  needle: string;
}

interface Options {
  path: string | null;
  line: number | null;
  rule: string | null;
}

export function useCodePreview({ path, line, rule }: Options) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [model, setModel] = useState<CodeWindowModel | null>(null);

  useEffect(() => {
    if (!path) {
      setModel(null);
      setError(null);
      setLoading(false);
      return;
    }

    let cancelled = false;
    setLoading(true);
    setError(null);

    (async () => {
      try {
        const url = new URL("/api/file", window.location.href);
        url.searchParams.set("path", path);
        const response = await fetch(url.href);
        const content = await response.text();
        if (!response.ok) {
          throw new Error(content || `Unable to load ${path}`);
        }
        if (cancelled) return;

        const lines = content.split("\n");
        const needle = `spec: ${rule || ""}`;
        let hit = -1;
        if (typeof line === "number" && line > 0 && line <= lines.length) {
          const idx = line - 1;
          if (lines[idx].includes(needle) || lines[idx].includes(rule || "")) {
            hit = idx;
          }
        }
        if (hit < 0) hit = lines.findIndex((entry) => entry.includes(needle));
        if (hit < 0 && typeof line === "number" && line > 0) hit = line - 1;

        if (hit < 0) {
          setModel(null);
          setError(`No ${rule} backlink found in ${path}.`);
          return;
        }

        const start = Math.max(0, hit - 5);
        const end = Math.min(lines.length, hit + 6);
        setModel({
          path,
          hitLine: hit + 1,
          lineHint: typeof line === "number" ? line : null,
          start,
          end,
          lines: lines.slice(start, end),
          needle,
        });
        setError(null);
      } catch (err) {
        if (!cancelled) {
          setModel(null);
          setError(err instanceof Error ? err.message : String(err));
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [path, line, rule]);

  return { loading, error, model };
}
