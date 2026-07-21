import type { ViewId } from "../types";

const VIEWS: { id: ViewId; label: string }[] = [
  { id: "spec", label: "Spec map" },
  { id: "implementation", label: "Implementation" },
  { id: "evolution", label: "Evolution" },
  { id: "drift", label: "Drift" },
];

export function AppHeader({
  context,
  view,
  onViewChange,
}: {
  context: string;
  view: ViewId;
  onViewChange: (view: ViewId) => void;
}) {
  return (
    <>
      <header>
        <div className="brand">
          <img
            className="brand-logo"
            src="/ui_assets/potpie-logo.jpeg"
            alt="potpie.ai"
          />
          <span className="brand-divider" aria-hidden="true" />
          <small>Spec Agent</small>
        </div>
      </header>

      <div className="subnav">
        <nav className="view-nav" aria-label="Workspace views">
          {VIEWS.map((item) => (
            <button
              key={item.id}
              type="button"
              className={item.id === view ? "active" : undefined}
              onClick={() => onViewChange(item.id)}
            >
              {item.label}
            </button>
          ))}
        </nav>
        <span className="subnav-context">{context}</span>
      </div>
    </>
  );
}
