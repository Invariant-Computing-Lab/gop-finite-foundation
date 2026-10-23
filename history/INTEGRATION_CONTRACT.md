# Study-to-foundation integration contract v1.0

**Purpose:** let later work change the evidence and expose needed revisions without invisibly rewriting the frozen mathematical core. This document specifies functions Astra must implement in the final release; the scientific intake CLI is not implemented by this command bundle.

## A. Import is not endorsement

Only ingest materials supplied or explicitly authorized for that study. Do not claim to have examined all of the author's work. Preserve the source's terminology, causal scope, population, methods, reference version, limitations and result direction. A missing source stays missing. New interpretation is separately marked.

Every imported source receives a content hash and locator. Extract claims at the smallest useful granularity; deduplicate claims repeated in reports, papers or derivative summaries. Record dataset/run/source-lineage IDs so reuse does not become a new replication. A statement in an abstract is `reported`, not full-method verified or reproduced.

For a proposed proof, separate theorem, assumptions, derivation, numerical example and conjecture. For empirical work, separate intervention and observation. For synthetic work, identify the generator and whether targets came from the candidate. For personal/qualitative accounts retain their source and interpretive context; they are not numerical evidence of a physical mechanism. Design and creative artifacts may inform concepts or tools without proving causal/clinical effectiveness.

## B. Minimum study package

Use the supplied JSON Schema as a baseline, producing a compatible documented final schema. Required elements:

- stable study/evidence IDs, schema version, target foundation ID and core hash;
- owning program (`RARI`, `OCIL_OCIR`, `AFC`, `SACRA` or `UNASSIGNED`) and optional cross-program links, not a new umbrella program;
- original source name/hash, exact locator and access level;
- a source-derived claim and a separate integration interpretation;
- linked core claim/assumption/equation IDs, or `UNMAPPED` with reason;
- population/system class, variables, units, interventions, observation/inference access, independent sampling unit and lineage group;
- reported results including nulls/contradictions, uncertainty and limits, without fabricated values when unavailable;
- evidence/reproduction/review statuses and proposed relation;
- requested action and any core-change request, never silently approved.

Allowed relations: `supports`, `challenges`, `constrains`, `extends_scope`, `informs_design`, `context_only`, `unmapped`. Justification must name matched and mismatched assumptions. If a logical transfer is claimed, supply the bridge and its assumptions; “both use the word invariant” is not sufficient.

## C. Effects of a new study

1. **Evidence-only:** append a record and assessment snapshot. No equation/code/claim-definition changes.
2. **Adapter extension:** new versioned mapping using the existing operator/lift/observation contract. State any newly fitted parameters and testing scope. It must not hide new physics or change core budgets. Freeze an adapter before its own held-out evaluation.
3. **Core revision proposal:** if an equation, admissible operator, ontology, universal quantifier, bound or global fitted law parameter must change, generate a request with counterexample, exact proposed change, complexity cost, affected claims, regression tests and independent validation needs. Do not implement a revised core without explicit authorization.
4. **Not mappable:** preserve the source and explain the absent bridge. Do not reject valuable work just because its evidence type is not numeric, and do not manufacture a bridge to satisfy the program.

A core claim can be assessed as challenged or contradicted by later evidence while its original definition and tested version remain fixed. Assessment snapshots must not make a negative vanish. Retractions/corrections use `supersedes` relations, keeping the prior entry and reason.

## D. Practical CLI to build, test and document

Implement a small standard-library-first CLI, not a database service or new web platform. Proposed invocations, to be made real and tested by Astra:

```text
python -m gop_intake init --core ./GOP_TOE_FOUNDATION_v1_0 --study-dir ./new_study
python -m gop_intake ingest --core ./GOP_TOE_FOUNDATION_v1_0 --record ./new_study/study_record.json
python -m gop_intake assess --core ./GOP_TOE_FOUNDATION_v1_0 --study-id <actual_id>
python -m gop_intake verify --core ./GOP_TOE_FOUNDATION_v1_0
python -m gop_intake export --core ./GOP_TOE_FOUNDATION_v1_0 --study-id <actual_id> --out ./study_addon.zip
```

These are requested API behavior, not commands to assume already exist. Astra may adjust actual package/module names consistently and must place tested exact commands in the final README and future-study prompt. User-facing operation must not require editing Python source. A structured record plus attached documents is sufficient for the assisted workflow; a new study can remain `UNMAPPED` rather than receive guessed classifications.

- `init` creates an explicitly unreviewed draft and never changes core files.
- `ingest` validates schema/paths/hashes, is idempotent on duplicate source/record identity, and appends a new version for changed material. Require supplied valid hashes rather than deriving them from filenames.
- `assess` stores a scope-aware interpretation with review status. It does not infer scientific support from file count or automatically promote a draft to accepted evidence. Human/user review can be required where substantive judgment remains unresolved.
- `verify` checks record integrity, source lineage and unchanged core hash. It is not a theorem prover or scientific validation.
- `export` creates an add-on containing records, permitted sources, assessments and compatibility report; no credentials or unrelated personal data.

Minimum tests: duplicate import, changed-source version, invalid record, template rejection, unresolved units, contradiction, shared-dataset duplication, unreviewed status preservation, missing source, no core mutation, actual new-core request prohibition and clean add-on replay. Use disposable fixtures marked `TEST_FIXTURE`; never publish them as real evidence.

## E. Demonstration and future handoff

During the finalization run, perform one historical import of the supplied audit/result. This verifies the integration mechanism; it is not fresh scientific support. Include exact source locators and mark the known F0-G/F0-P distinction and no-lift counterexamples appropriately. Add empty templates, not imaginary completed evidence, for each existing program.

Each later handoff produces: a short Turkish account of what the study changes, scope/assumption comparison, source/claim links, an add-on ZIP, unchanged-core verification, and a revision request only when warranted. By default, it must end without rerunning all foundational experiments or changing the universal candidate. Evidence accumulation is allowed to strengthen, weaken or contradict the hypothesis; it is not a mechanism to force every future study to confirm it.
