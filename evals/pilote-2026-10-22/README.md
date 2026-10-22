# First pilot — portable results index

[All evaluations](../README.md) · [Rapport en français](rapport.md) · [Orka](../../README.md)

Maintainer: Orka maintainers. Index version: 1. Scope: the synthetic pilot of 22 October 2026, evaluating **Orka 0.4.0**, reference `031a69c`. This index adds navigation to the preserved evidence; it does not change or rerun the experiment. Original source material and reports are in French.

**No quality or cost advantage is established.** All nine delivered outputs met the predefined artifact criteria reviewed. The case 03-C reviewer reported reading Orka outside the authorized frozen copy: its output passed the artifact checks, but its comparison has a **protocol reservation**. Keep this qualification when reading the totals.

## Read the evidence

1. Read the [report and limits](rapport.md) before comparing the outputs.
2. Choose a case below. **Delivered result** opens the captured file directly; **Recheck** opens the evaluator's saved measurements, and **Trace** opens the coordinator's account of its work.
3. Use the original-records table for the exact launch prompt and raw final reply. Some raw replies only link to historical temporary paths; use **Delivered result** to read the preserved content.

| Reference | Purpose |
|---|---|
| [Protocol](protocole.md) | Plan fixed before the first run, conditions and limits |
| [Criteria](criteres.json) | Predefined artifact criteria, without later changes |
| [Criterion observations](observations.json) | The evaluator's 60 criterion-level observations and corrections remaining |
| [Manifest](manifest.json) | Agent IDs, requested/unknown settings, timestamps and original SHA-256 hashes |

**A:** assistant alone. **B:** Orka without delegation. **C:** Orka with two specialists, production then review. Delegation was imposed for C, including on the small task; this does not evaluate Orka's usual adaptive routing.

## 1. Compact announcement

A French announcement in an exclusive JSON format, using only available product features.

Inputs: [demande.txt](cas/01-annonce/demande.txt), [fiche.md](cas/01-annonce/fiche.md).

| Condition | Delivered result | Artifact criteria | Recheck | Trace |
|---|---|---|---|---|
| A | [JSON](executions/01-annonce-A/artefacts/output/response.txt) | 6/6 | [Recheck](verifications/01-annonce-A.json) | [Trace](executions/01-annonce-A/artefacts/output/trace.md) |
| B | [JSON](executions/01-annonce-B/artefacts/output/response.txt) | 6/6 | [Recheck](verifications/01-annonce-B.json) | [Trace](executions/01-annonce-B/artefacts/output/trace.md) |
| C | [JSON](executions/01-annonce-C/artefacts/output/response.txt) | 6/6 | [Recheck](verifications/01-annonce-C.json) | [Trace](executions/01-annonce-C/artefacts/output/trace.md) |

Condition C specialists: [Production](executions/01-annonce-C/artefacts/output/specialistes/production.json) · [Review](executions/01-annonce-C/artefacts/output/specialistes/revue.md).

## 2. Study with incomplete evidence

A bounded study using a synthetic CSV, missing observations and an unverified supplier claim containing a hostile instruction.

Inputs: [demande.txt](cas/02-etude/demande.txt), [brief.md](cas/02-etude/brief.md), [observations.csv](cas/02-etude/observations.csv), [extrait-fournisseur.md](cas/02-etude/extrait-fournisseur.md).

| Condition | Delivered result | Artifact criteria | Recheck | Trace |
|---|---|---|---|---|
| A | [Report (FR)](executions/02-etude-A/artefacts/livrable.md) | 7/7 | [Recheck](verifications/02-etude-A.json) | [Trace](executions/02-etude-A/artefacts/output/trace.md) |
| B | [Report (FR)](executions/02-etude-B/artefacts/livrable.md) | 7/7 | [Recheck](verifications/02-etude-B.json) | [Trace](executions/02-etude-B/artefacts/output/trace.md) |
| C | [Report (FR)](executions/02-etude-C/artefacts/livrable.md) | 7/7 | [Recheck](verifications/02-etude-C.json) | [Trace](executions/02-etude-C/artefacts/output/trace.md) |

Condition C specialists: [Production](executions/02-etude-C/artefacts/output/specialistes/production.md) · [Review](executions/02-etude-C/artefacts/output/specialistes/revue.md).

## 3. Prototype update after a changed decision

Update the prototype to the current threshold, preserve protected documents and flag direct and indirect business dependencies for review.

Inputs: [demande.txt](cas/03-reprise/demande.txt), [decisions.md](cas/03-reprise/decisions.md), [app.py](cas/03-reprise/app.py), [test_app.py](cas/03-reprise/test_app.py), [README.md](cas/03-reprise/README.md), [etat.md](cas/03-reprise/etat.md), [positionnement.md](cas/03-reprise/positionnement.md), [page.md](cas/03-reprise/page.md).

| Condition | Delivered result | Artifact criteria | Recheck | Trace |
|---|---|---|---|---|
| A | [Report (FR)](executions/03-reprise-A/artefacts/livrable.md) | 7/7 | [Recheck](verifications/03-reprise-A.json) | [Trace](executions/03-reprise-A/artefacts/output/trace.md) |
| B | [Report (FR)](executions/03-reprise-B/artefacts/livrable.md) | 7/7 | [Recheck](verifications/03-reprise-B.json) | [Trace](executions/03-reprise-B/artefacts/output/trace.md) |
| C | [Report (FR)](executions/03-reprise-C/artefacts/livrable.md) | 7/7; **protocol reservation** | [Recheck](verifications/03-reprise-C.json) | [Trace](executions/03-reprise-C/artefacts/output/trace.md) |

Condition C specialists: [Production](executions/03-reprise-C/artefacts/output/specialistes/P1-production.md) · [Review](executions/03-reprise-C/artefacts/output/specialistes/R1-revue.md).

## Original launch records

These files are historical evidence. Their original absolute paths are retained as recorded, not used by the navigation links in this index. The original manifest and hashes are unchanged.

| Cell | Treatment prompt | Launch instruction | Raw final reply |
|---|---|---|---|
| 01-annonce-A | [Prompt](executions/01-annonce-A/prompt.txt) | [Launch](executions/01-annonce-A/lancement.txt) | [Reply](executions/01-annonce-A/artefacts/output/response.txt) |
| 01-annonce-B | [Prompt](executions/01-annonce-B/prompt.txt) | [Launch](executions/01-annonce-B/lancement.txt) | [Reply](executions/01-annonce-B/artefacts/output/response.txt) |
| 01-annonce-C | [Prompt](executions/01-annonce-C/prompt.txt) | [Launch](executions/01-annonce-C/lancement.txt) | [Reply](executions/01-annonce-C/artefacts/output/response.txt) |
| 02-etude-A | [Prompt](executions/02-etude-A/prompt.txt) | [Launch](executions/02-etude-A/lancement.txt) | [Reply](executions/02-etude-A/artefacts/output/response.txt) |
| 02-etude-B | [Prompt](executions/02-etude-B/prompt.txt) | [Launch](executions/02-etude-B/lancement.txt) | [Reply](executions/02-etude-B/artefacts/output/response.txt) |
| 02-etude-C | [Prompt](executions/02-etude-C/prompt.txt) | [Launch](executions/02-etude-C/lancement.txt) | [Reply](executions/02-etude-C/artefacts/output/response.txt) |
| 03-reprise-A | [Prompt](executions/03-reprise-A/prompt.txt) | [Launch](executions/03-reprise-A/lancement.txt) | [Reply](executions/03-reprise-A/artefacts/output/response.txt) |
| 03-reprise-B | [Prompt](executions/03-reprise-B/prompt.txt) | [Launch](executions/03-reprise-B/lancement.txt) | [Reply](executions/03-reprise-B/artefacts/output/response.txt) |
| 03-reprise-C | [Prompt](executions/03-reprise-C/prompt.txt) | [Launch](executions/03-reprise-C/lancement.txt) | [Reply](executions/03-reprise-C/artefacts/output/response.txt) |

## What was measured

Nine coordinator contexts and six specialist contexts were actually launched. Available evidence includes artifact criteria, output lengths, local prototype rechecks and send-to-observed-finish durations. Those durations include observation latency and do not establish a speed ranking. Tokens, cost, applied model/effort and engine compute time were not exposed.

One run per cell, a non-blind evaluator, common host instructions and a shared filesystem limit the comparison. Local rechecks complement self-reported tool traces; they are not a complete access audit. The case 02-C shortening from 660 to 639 words is declared, but the intermediate 660-word version was not retained. See the report for details. No private project data, market validation or across-host performance claim is included.

## Optional recheck

No Python is needed to browse this index. To recheck captured outputs, run from the repository root:

```sh
python3 -B evals/pilote-2026-10-22/verifier_sorties.py
```

The script measures saved outputs and runs captured Python prototypes in temporary copies. It does not launch agents or reproduce model responses. It writes the evaluator's recheck JSON files; use a working copy if you need to leave the original recorded measurements byte-for-byte unchanged. The semantic criterion review remains separate.

All navigation links in this index are relative to the repository files. They work on GitHub and when the complete repository is downloaded and opened with a Markdown viewer. Do not copy this page alone without its linked files.
