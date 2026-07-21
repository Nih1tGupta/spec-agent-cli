import { AppHeader } from "./components/AppHeader";
import { DriftPanel } from "./components/DriftPanel";
import { EvolutionPanel } from "./components/EvolutionPanel";
import { ImplementationPanel } from "./components/ImplementationPanel";
import { SpecMapPanel } from "./components/SpecMapPanel";
import { Empty } from "./components/Shared";
import { useSnapshot, useWorkspace } from "./hooks/useWorkspace";
import "./styles.css";

export default function App() {
  const { data, error, loading } = useSnapshot();
  const {
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
  } = useWorkspace(data);

  if (loading) {
    return (
      <div className="app">
        <AppHeader context="Loading…" view="spec" onViewChange={setView} />
        <div className="workspace">
          <main className="panel evidence-panel view-active">
            <Empty>Loading specification evidence…</Empty>
          </main>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="app">
        <AppHeader context="Unavailable" view="spec" onViewChange={setView} />
        <div className="workspace">
          <main className="panel evidence-panel view-active">
            <Empty>Unable to load workspace: {error || "unknown error"}</Empty>
          </main>
        </div>
      </div>
    );
  }

  const head = data.project.head_commit ? ` · ${data.project.head_commit}` : "";
  const context = `${data.project.title}${head}`;
  const view = workspace.view;

  const onSelectFile = (key: string) => setFile(key);

  return (
    <div className="app">
      <AppHeader context={context} view={view} onViewChange={setView} />
      <div className="workspace">
        {view === "spec" ? (
          <SpecMapPanel
            data={data}
            selected={workspace.selected}
            onSelect={selectPacket}
          />
        ) : null}

        {view === "implementation" && selectedPacket ? (
          <ImplementationPanel
            data={data}
            packet={selectedPacket}
            rule={workspace.rule}
            file={workspace.file}
            onToggleRule={toggleRule}
            onSelectFile={onSelectFile}
            onFileKey={setFile}
          />
        ) : null}

        {view === "drift" ? (
          <DriftPanel
            data={data}
            knownBehaviorIds={knownBehaviorIds}
            onJumpToBehavior={jumpToBehavior}
          />
        ) : null}

        {view === "evolution" ? (
          <EvolutionPanel
            data={data}
            selected={selectedPacket}
            eventId={workspace.eventId}
            onSelectPacket={selectEvolutionPacket}
            onSelectEvent={selectEvent}
            onJumpToBehavior={jumpToBehavior}
            onOpenImplementation={() => setView("implementation")}
          />
        ) : null}

        {view === "implementation" && !selectedPacket ? (
          <main className="panel evidence-panel view-active">
            <Empty>No packets available.</Empty>
          </main>
        ) : null}
      </div>
    </div>
  );
}
