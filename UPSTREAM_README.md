# GOP TOE foundation 1.0.0

**Release: FROZEN_LIMITED. Candidate: F2a. Universal claim: CONJECTURE_UNESTABLISHED.** This is an executable frozen research reference with preserved negative results. It is not a validated physical or clinical theory. Some requested coverage is not performed; see coverage_matrix.json.

Author: Emirhan Yıldırım, occupational therapy student, as stated in the supplied conceptual manuscript. AI-assisted author-review draft; not submitted or published.

Start with SONUC_OZETI_TR.md, FOUNDATION_CARD.md and manuscript/paper.pdf. The mathematical core is in core/, and results/ contains actual new synthetic results. Unchanged historical inputs are in history/original_inputs/.

Core SHA256: `cc99f94bd75a67c0035c8342ef3fdc4ba1d937a586bef2ede4354f1d829ce8b7`. CORE_MANIFEST.json defines canonical path/hash entries. It excludes its own bytes and the self-referential freeze; the latter has a separately checked hash. The ZIP stays immutable. Intake modifies only evidence/ and changes/requests/ in a working copy.

## Verify archived results

From this directory, with Python3.12, NumPy and SciPy installed:

```bash
python -m unittest discover -s tests -v
python -m src.verify_release
python -m gop_intake verify --core .
sha256sum -c SHA256SUMS.txt
```

The verifier recomputes4,536 scalar score rows from arrays, checks260 prediction trace records, and replays a fitted F2 flow. Final world IDs were generated after the freeze. Same-environment reproducibility is not independent replication.

## Reproduce the numerical suite in a fresh copy

Keep the original ZIP unchanged. Copy/extract into a new directory, keep its core and frozen configs, and move results/direct_generator/*.jsonl and physical result outputs to a separate archive before recomputing. The scripts refuse to silently overwrite completed scalar split outputs. Run sequentially:

```bash
python -m src.experiment training
python -m src.experiment development
python -m src.experiment calibration
python -m src.experiment final
python -m src.physical
python -m src.scoring.summarize
```

Do not rerun comparator selection or change the core/TEST_PLAN after viewing final results. A replay is the same analysis, not fresh confirmation. Preserve the original CORE_MANIFEST and FREEZE. All numerical modules use one BLAS thread. No inherited pickle or network service is required.

## Attach a new study

```bash
python -m gop_intake init --core . --study-dir ../new_study
python -m gop_intake ingest --core . --record ../new_study/study_record.json
python -m gop_intake assess --core . --study-id ACTUAL_ID
python -m gop_intake verify --core .
python -m gop_intake export --core . --study-id ACTUAL_ID --out ../study_addon.zip
```

Fill the draft using actual source bytes, locators, units and claim IDs. Draft templates are rejected; all imports begin unreviewed. Repeated identical imports are idempotent; changed sources create immutable record versions. The CLI supports one writer at a time. It validates integrity and proposed mappings, not scientific truth. A revision request is a proposal and cannot execute a core change.

To apply an add-on to a compatible extracted working copy:

```bash
python -m gop_intake replay --core . --bundle ../study_addon.zip
```

The historical audit import demonstrates this workflow without adding fresh support. Four empty program templates are under integration/templates/. No fictional clinical or human data are included.

## Limitations that affect use

The learned comparison covers three scalar mechanisms with per-world32-reset adaptation, tiny reset sensor noise and noiseless evaluation sensing. The known sensor gains are supplied. Physical checks use configured/oracle coefficients. General unknown-gain identification, full legacy ten-family replay, clipped resource regulation, tanh coupling, central-force trajectories and full thermodynamic path accounting are not new executed coverage. At the frozen Ito EM resolution the lift-manifold residual does not meet1e-5. The degree7 exact-closure obstruction remains. No post-final scientific repair is authorized by this release.

A derived metadata erratum corrects generic physical-trace horizon labels to actual index/time semantics. It changes no core, prediction or score. See history/METADATA_ERRATUM.json; raw numerical replay retains the documented generic-label limitation.
