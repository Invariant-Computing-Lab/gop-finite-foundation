# Final-release rules and stop contract

These are newly specified operational rules for the continuation, not results from the previous run.

## 1. Three distinct versions

- **Command contract:** v2.0, the present instructions.
- **Candidate:** F2, one selected specification, with optional F2a → F2b *before* final freeze. The archived F0/F1 nomenclature is not reused or overwritten.
- **Foundation release:** 1.0.0, the fixed reproducible reference for subsequent studies. A scientific rejection does not mean its archived bytes should disappear.

A mathematical or empirical contradiction must remain visible. “Final foundation” is not “final correct theory.” The purpose is to stop the present foundational search at a documented boundary and change the mode of work to evidence-driven integration.

## 2. Phases with terminal behavior

`INGEST → BUILD_F2 → DEVELOPMENT → FREEZE_SPEC → FINAL_EVALUATION → AUDIT → PACKAGE → FROZEN`

At most one substantive development repair. After `FREEZE_SPEC`, a change to equations, lift budget, assumptions, target definition, test distribution or model selection is a scientific change requiring a future version. Do not call it a numerical repair.

An implementation bug can be fixed in a retained patch branch after an erratum specifies the bug, affected outputs, original and corrected hashes, and why the scientific contract is unchanged. Reprocessing an exposed test is a correction/reanalysis, not fresh confirmation. If the distinction is uncertain, flag it rather than silently choose “bug.”

Resource/platform blocking yields `BLOCKED_TECHNICAL` with checkpoints and exact unfinished gates, not a fake FROZEN status. Budget expiry ends search; all completed work is packaged and unperformed work marked. Do not create new candidates automatically.

## 3. Release status versus scientific status

`release_status`:
- `FROZEN_COMPLETE`: all integrity/execution/intake gates completed, including preserved negative results.
- `FROZEN_LIMITED`: usable frozen core, traceability and intake completed; some declared non-core sector evaluations could not be executed and are explicitly excluded from coverage. This is NOT completion of the entire requested battery.
- `BLOCKED_TECHNICAL`: no usable direct-law implementation or essential integrity/intake gate remains incomplete. Deliver checkpoint and a blocked handoff, not a success claim.

`universal_claim_status`:
- `CONJECTURE_UNESTABLISHED`;
- `BOUNDED_INSTANCE_SUPPORTED` (only with named scope; never a universal validation);
- `BOUNDED_INSTANCE_CONTRADICTED`;
- `NOT_EVALUABLE_UNDER_CURRENT_SPEC`.

Use per-claim status when one global category would obscure different outcomes. One may freeze a contradicted bounded candidate as the historical basis for later work, but must not recommend it as a validated physical or clinical model.

## 4. Essential acceptance gates

G1. **Source integrity:** original archives unchanged; source→new-claim map complete; inaccessible inputs flagged.
G2. **Explicit candidate:** equations, symbols, dimensions/units, all operators and finite budgets; a non-vacuous statement of what is ruled out.
G3. **Direct-law traceability:** each scored F2 forecast linked to the actual candidate and parameter/adapter/inference hashes; no F0-P substitution.
G4. **Core execution:** actual direct generator/instrument execution including nonlinear dynamics and the two-endpoint loop; no fabricated numerical values. All declared sector runs have truthful disposition.
G5. **Evaluation integrity:** prospective split/freeze and valid target/mask rules; failed and divergent runs retained; all baselines reported.
G6. **Physical scope:** imported, derived, tested and unresolved law content separated; no de-scoping of the universal target to avoid a negative.
G7. **Repeatability:** fresh-directory smoke replay and score recomputation; no uninspected pickle loading requirement.
G8. **Future intake:** schema, CLI and conflict/idempotency/no-core-mutation tests actually pass.
G9. **Final packaging:** hashes/manifests resolve; paper and supplements match equations, code and result tables.

`FROZEN_COMPLETE` requires G1–G9 and the full declared core battery. `FROZEN_LIMITED` is permitted only when G1–G3 and G5–G9 pass and a usable G4 core exists; identify every uncovered required sector and do not describe the requested run as fully completed. A failed scientific tolerance does not fail G4 execution, but an absent execution does.

## 5. The immutable core and separate updates

Required tree (additional implementation files are allowed; avoid unnecessary bureaucracy):

```text
GOP_TOE_FOUNDATION_v1_0/
  README.md
  FOUNDATION_CARD.md
  RELEASE_REPORT.json
  CORE_MANIFEST.json
  SHA256SUMS.txt
  STATE.json / PROGRESS.md / NEXT_ACTION.md
  core/
    EQUATION_CARD.md
    UNIVERSALITY_STATEMENT.md
    FORMAL_CORE.tex
    PROOFS_AND_COUNTEREXAMPLES.md
    LIFTING_CONTRACT.json
    ASSUMPTIONS.jsonl
    CLAIMS.jsonl
    TRACEABILITY.jsonl
    specification.json
  src/
    candidate/        # the actual F2 implementation
    reference/        # independent target generators
    inference/
    scoring/
    intake/           # actually implemented study integration
  configs/
    BUDGET.json / TEST_PLAN.json / FREEZE.json
  results/
    direct_generator/ / legacy_predictor/ / physical_consistency/
    coverage_matrix.json / hypothesis_status.json
  parameters/ / predictions/ / logs/ / tests/
  evidence/
    registry.jsonl
    assessments/      # append-only derived assessments, not original claims
    records/
  schemas/
  adapters/
  changes/
    requests/         # proposals; no automatic acceptance
  history/
    source_manifest.json
    prior_failure_map.md
  manuscript/
    paper.md / paper.tex / paper.pdf
    supplement.tex / supplement.pdf / references.bib
  integration/
    INTEGRATION_CONTRACT.md
    templates/
    NEXT_STUDY_PROMPT_TR.txt
  SONUC_OZETI_TR.md
```

Do not create two authoritative copies of the same core. `CORE_MANIFEST.json` identifies the actual immutable scientific files: formal specification, equations, approved operator/lifting rules, claims and assumptions, reference implementation, core test definitions and frozen methodological contracts. Record a deterministic core content hash. The manifest cannot recursively include its own hash; define the hash as canonical sorted (relative path, SHA-256) entries excluding self-referential fields. State canonicalization explicitly.

Learned study/world parameters, incoming studies and evidence assessments live outside the immutable core. They refer to the core hash and retain their own hashes. Study fitting does not silently alter global structure; any globally refitted law constants are a new candidate snapshot.

The release ZIP itself is immutable. To attach a study, work in an extracted copy or sidecar that references the core. Do not overwrite the original ZIP. Produce an evidence/add-on ZIP and updated evidence snapshot; verify the core content hash remains identical. A new scientific core uses a new release ID and preserves the former one.

Do not maintain an infinitely retried “pending improvements” gate. The unmet-physics and empirical-obligation ledgers are future work inputs, not permission to restart this run.
