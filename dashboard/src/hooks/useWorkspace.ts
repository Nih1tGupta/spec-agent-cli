import { useCallback, useEffect, useMemo, useState } from "react";
import type { Packet, Snapshot, ViewId, WorkspaceState } from "../types";

const initialWorkspace: WorkspaceState = {
  selected: null,
  rule: null,
  view: "spec",
  file: null,
  eventId: null,
};

export function useSnapshot() {
  const [data, setData] = useState<Snapshot | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const response = await fetch("/api/snapshot");
        if (!response.ok) {
          throw new Error(`Snapshot request failed (${response.status})`);
        }
        const payload = (await response.json()) as Snapshot;
        if (!cancelled) {
          setData(payload);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : String(err));
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  return { data, error, loading };
}

export function useWorkspace(data: Snapshot | null) {
  const [workspace, setWorkspace] = useState<WorkspaceState>(initialWorkspace);

  useEffect(() => {
    if (!data) return;
    setWorkspace((prev) => {
      if (prev.selected) return prev;
      const first = data.packets[0];
      return {
        ...prev,
        selected: first?.slug ?? null,
        rule: first?.behavior_ids[0] ?? null,
        eventId:
          first?.event_details?.[0]?.id ?? data.events[0]?.id ?? null,
      };
    });
  }, [data]);

  const selectedPacket: Packet | null = useMemo(() => {
    if (!data) return null;
    return data.packets.find((packet) => packet.slug === workspace.selected) ?? data.packets[0] ?? null;
  }, [data, workspace.selected]);

  const setView = useCallback((view: ViewId) => {
    setWorkspace((prev) => ({ ...prev, view }));
  }, []);

  const selectPacket = useCallback(
    (slug: string) => {
      if (!data) return;
      const packet = data.packets.find((item) => item.slug === slug);
      setWorkspace((prev) => ({
        ...prev,
        selected: slug,
        rule: packet?.behavior_ids[0] ?? null,
        file: null,
        eventId: packet?.event_details?.[0]?.id ?? prev.eventId,
        view: "implementation",
      }));
    },
    [data],
  );

  const selectEvolutionPacket = useCallback(
    (slug: string) => {
      if (!data) return;
      const packet = data.packets.find((item) => item.slug === slug);
      setWorkspace((prev) => ({
        ...prev,
        selected: slug,
        rule: packet?.behavior_ids[0] ?? null,
        eventId: packet?.event_details?.[0]?.id ?? null,
        view: "evolution",
      }));
    },
    [data],
  );

  const selectEvent = useCallback((id: string) => {
    setWorkspace((prev) => ({ ...prev, eventId: id, view: "evolution" }));
  }, []);

  const toggleRule = useCallback((id: string) => {
    setWorkspace((prev) => ({
      ...prev,
      rule: id,
      file: null,
      view: prev.view === "implementation" ? prev.view : "implementation",
    }));
  }, []);

  const setFile = useCallback((key: string | null) => {
    setWorkspace((prev) => ({ ...prev, file: key }));
  }, []);

  const jumpToBehavior = useCallback(
    (behaviorId: string) => {
      if (!data) return;
      const packet = data.packets.find((item) =>
        item.behavior_ids.includes(behaviorId),
      );
      // Only navigate when the rule exists in some packet's Implementation view.
      if (!packet) return;
      setWorkspace((prev) => ({
        ...prev,
        selected: packet.slug,
        rule: behaviorId,
        file: null,
        view: "implementation",
      }));
    },
    [data],
  );

  const knownBehaviorIds = useMemo(() => {
    const ids = new Set<string>();
    for (const packet of data?.packets || []) {
      for (const id of packet.behavior_ids || []) ids.add(id);
    }
    return ids;
  }, [data]);

  return {
    workspace,
    selectedPacket,
    setView,
    selectPacket,
    selectEvolutionPacket,
    selectEvent,
    toggleRule,
    setFile,
    jumpToBehavior,
    knownBehaviorIds,
  };
}
