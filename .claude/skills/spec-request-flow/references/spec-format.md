# Specification Format

Root `SPEC.md` is the product-wide contract and feature index. Each material feature
lives in `spec/features/<feature-slug>/` and contains exactly two product artifacts:

- `spec.md`: normative product rules, actors, conceptual data, flows, states,
  permissions, constraints, and approved decisions;
- `acceptance.md`: observable acceptance scenarios, failure outcomes, edge cases,
  and exception policy mapped to stable behavior IDs.

Both files describe **what must be true**, never how software will be built. They must
not contain repository paths, code symbols, libraries, frameworks, storage choices,
implementation sequences, test filenames, commands, deployment instructions, or code
backlinks. Root `SPEC.md` links both files. Derived code linkage belongs only in
`spec/traceability.json`, which is not normative.

## Lifecycle

- `draft`: product behavior or acceptance remains incomplete or unapproved;
- `product-approved`: the presented product decisions are approved and may be written;
- `approved`: both self-reviewed files received explicit written-spec approval;
- `superseded`: a later approved contract replaced this feature specification.

Implementation and verification status never changes the meaning or status of an
approved product specification. Keep behavior IDs stable across revisions. Record
approved transitions in evolution history; keep current truth in the two spec files.

Use `scripts/create_feature.py <feature-slug> --title "Feature Title"` to create the
two-file packet without overwriting existing work. Replace every instruction with
feature-specific content before requesting approval.

## Requirements-completeness checklist

Before writing, evaluate actors, business rules, conceptual entities and invariants,
primary and alternate flows, failure and recovery behavior, states, edge cases,
permissions, privacy, defaults, constraints, non-goals, and measurable outcomes.
Label every unresolved item `blocking` or `non-blocking`; approved specs have no
blocking items.

## Spec self-review

Run every check on both files before requesting written-spec approval.

1. **Placeholder scan:** Remove templates, empty required sections, `TBD`, `TODO`, and
   vague promises.
2. **Internal consistency:** Ensure terms, rules, data, flows, states, and outcomes do
   not contradict one another.
3. **Scope:** Keep one independently valuable feature per packet.
4. **Ambiguity:** Define actors, terms, authority, defaults, boundaries, and outcomes.
5. **Testability:** Make every rule observable without prescribing engineering tests.
6. **Failure, security, and privacy:** State failure, recovery, authorization, data
   handling, and non-disclosure outcomes, or explicitly mark them not applicable.
7. **Unique ownership:** Give each normative rule one stable behavior ID and one owner.
8. **Acceptance coverage:** Map every behavior ID to at least one acceptance scenario;
   ensure every scenario names the behavior it covers.
9. **Implementation-content scan:** Remove paths, code names, technology choices,
   ordered build steps, commands, and backlinks.

After approval, revise product meaning only through the complete clarification and
approval workflow. Git owns line diffs; evolution history owns decision sequence.
