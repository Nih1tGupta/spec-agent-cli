export type ViewId = "spec" | "implementation" | "evolution" | "drift";

export interface Backlink {
  path: string;
  line: number | null;
  file_sha256?: string | null;
  current_sha256?: string | null;
  hash_ok?: boolean | null;
}

export interface CoverageRow {
  behavior_id: string;
  file_count: number;
  link_count: number;
  hash_mismatches: number;
  drift_count: number;
  last_event_id: string;
  last_event_at: string;
  status: string;
}

export interface Provenance {
  path: string;
  author: string;
  email?: string;
  date: string;
  commit: string;
  full_commit?: string;
  subject?: string;
  url?: string | null;
  pr_number?: string | null;
  pr_url?: string | null;
}

export interface EvolutionEvent {
  id: string;
  timestamp?: string;
  title?: string;
  task_type?: string;
  user_intent?: string;
  decision?: string;
  rationale?: string;
  spec_delta?: string;
  assumptions?: string;
  follow_ups?: string;
  actor?: string;
  status?: string;
  supersedes?: string;
  behavior_ids?: string[];
  spec_files?: string[];
}

export interface FollowUp {
  event_id: string;
  follow_ups: string;
  actor: string;
  timestamp: string;
}

export interface Packet {
  slug: string;
  source_dir: string;
  title: string;
  status: string;
  created?: string;
  behavior_ids: string[];
  spec: string;
  acceptance: string;
  linked_files: string[];
  events: string[];
  event_details?: EvolutionEvent[];
  behavior_backlinks?: Record<string, Backlink[]>;
  coverage?: CoverageRow[];
  open_follow_ups?: FollowUp[];
  provenance?: {
    spec?: Provenance | null;
    acceptance?: Provenance | null;
  };
}

export interface DriftIssue {
  kind: string;
  behavior_id: string;
  message: string;
  location: string;
}

export interface GroupedDriftIssue {
  kind: string;
  location: string;
  message: string;
  behavior_ids: string[];
}

export interface RecentChange {
  id: string;
  full_id: string;
  date: string;
  author: string;
  subject: string;
  url?: string | null;
  pr_number?: string | null;
  pr_url?: string | null;
}

export interface Snapshot {
  project: {
    title: string;
    status: string;
    path?: string;
    remote?: string | null;
    web_base?: string | null;
    git_root?: string | null;
    head_commit?: string | null;
  };
  packets: Packet[];
  events: EvolutionEvent[];
  recent_changes: RecentChange[];
  drift: {
    status: string;
    issues: DriftIssue[];
    error?: string;
  };
  traceability: {
    available: boolean;
    error?: string | null;
    behavior_count: number;
    linked_file_count: number;
    baseline_commit?: string | null;
    baseline_url?: string | null;
    hash_mismatches?: number;
  };
  warnings: string[];
}

export interface WorkspaceState {
  selected: string | null;
  rule: string | null;
  view: ViewId;
  file: string | null;
  eventId: string | null;
}
