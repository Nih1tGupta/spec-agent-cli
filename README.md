# Spec Agent CLI

Spec Agent turns unclear feature requests into approved, product-only specifications
before any implementation planning begins. It installs three Agent Skills under the
open `.agents/skills` convention and keeps specification evolution and code drift
observation available without mixing them into implementation work.

## Install

Python 3.11 or newer is required.

```sh
uv tool install spec-agent-cli
```

Alternatives:

```sh
pipx install spec-agent-cli
pip install spec-agent-cli
```

## Initialize a repository

```sh
cd /path/to/your-project
spec-agent init
```

This creates only missing project files and installs:

```text
.agents/skills/spec-request-flow/
.agents/skills/spec-drift-sync/
.agents/skills/spec-evolution/
AGENTS.md                         # managed rules block; user content is preserved
SPEC.md                           # created only when absent
spec/features/
spec/evolution/events.jsonl
spec/evolution/timeline.md
spec/traceability.json
```

Use `spec-agent init --check` for a read-only status check. Use
`spec-agent init --force` to refresh locally modified managed skill files after a CLI
upgrade. `--force` never replaces project specifications or history.

## Start a feature

Ask a compatible agent:

```text
Use spec-request-flow to define feature X. Do not implement it.
```

The Spec Agent repeatedly clarifies blocking product questions, compares meaningful
product approaches, writes `spec.md` and `acceptance.md`, asks for approval, records
the approved product evolution, and then gives you the prompt for a separate Code
Agent. That handoff requires `spec: BEHAVIOR-ID` backlinks in relevant production code
and tests.

## Validate implementation traceability

After an approved implementation, the Code Agent establishes the derived baseline and
then validates it:

```sh
spec-agent traceability-sync --repo .
spec-agent validate --repo .
```

`validate` is read-only and returns failure for missing, unknown, unbaselined, moved,
or changed backlink evidence. `traceability-sync` is used only after approved
implementation or explicit reconciliation; it must not be used to hide unexplained
drift.

## License

MIT
