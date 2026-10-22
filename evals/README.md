# Evaluations

This directory contains evaluation protocols, captured agent outputs and explicit observations. Product cases are synthetic; no private project data or evidence of market demand is included.

| Evaluation | Scope |
|---|---|
| [L3 software example](outillage-L3-2026-10-22/README.md) | Six prepared slots and five fabricated observations exercising preparation, imports, partial reporting and denominators. No model or agent launched; not the L4 comparison. |
| [L2 progressive-context acceptance](contexte-L2-2026-10-22/README.md) | Three synthetic tasks in fresh contexts, one run each; targeted requests, preserved counter, version changes and hostile source handling. Candidate-only checks, no comparative advantage or independent access audit established. |
| [README discovery test](decouverte-2026-10-22/README.md) | One fresh-context agent, README-only first impression, then linked guides and ZIP extraction. No blocker observed on that route; host activation and mission execution not tested. |
| [First comparative pilot](pilote-2026-10-22/README.md) | Three synthetic cases, three conditions per case; no quality or cost advantage established, one protocol reservation. |

## First comparative pilot

Start with the **[portable results index](pilote-2026-10-22/README.md)** for direct links to every captured deliverable, check, trace and original prompt. The [full report](pilote-2026-10-22/rapport.md) is in French. The original traces and hashes are preserved; the index supplies relative links for navigation on GitHub or in a downloaded repository.

The first pilot evaluates Orka **0.4.0** on three tasks: a compact JSON announcement, a study using incomplete supplied documents, and a prototype update after a changed decision. Each task has three separate conversation contexts: assistant alone, Orka without delegation, and Orka with two specialists. The specialist condition deliberately forces delegation, including on the simple task; it is not Orka's normal adaptive routing policy.

All nine delivered outputs met the predefined artifact criteria reviewed. This does **not** establish a quality or cost advantage. In case 03-C, a reviewer reported reading Orka outside the authorized frozen copy; the artifact checks passed, but that cell has a protocol reservation. Read the report before comparing totals. The original attempt is retained.

Read the [predefined criteria](pilote-2026-10-22/criteres.json), [execution manifest](pilote-2026-10-22/manifest.json) and captured files under `pilote-2026-10-22/executions/`. The manifest identifies the frozen skill and case inputs by hash. Native model calls were made through the host's agent tools, not through a Python model launcher.

To repeat a model run, create a fresh workspace from the relevant `cas/` inputs and a fresh conversation. Use the recorded treatment prompt, adapting only historical workspace paths. Keep the criteria out of the evaluated agent's context, preserve its outputs before review, and record actual agent IDs and available settings. The common host instructions and skill catalogue are not fully removable; filesystem separation was instructed, not enforced by a separate sandbox.

The optional command below only rechecks captured outputs and executes the small captured Python prototypes in temporary copies. It does **not** rerun agents or reproduce their model responses:

```sh
python3 -B evals/pilote-2026-10-22/verifier_sorties.py
```

Some raw responses and launch prompts preserve absolute paths from the original temporary workspace. Use the index's **Delivered result** links for reading; those historical paths are not portable links. Rechecking writes new verification JSON files, so use a working copy if the original measurements must remain byte-for-byte unchanged. Criterion-level review is performed by the maintenance coordinator, who knows the conditions. One run per cell is an exploratory pilot, not a statistically established comparison or a model quality benchmark. Missing token and cost telemetry remains unknown.
