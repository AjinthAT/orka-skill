# L4 — frozen campaign, not executed

Owner: maintenance coordinator. Protocol version 1, 22 October 2026. **18 slots prepared; zero model runs, observations or qualification results.** The synthetic inputs describe no real customer or business evidence.

This preparation compares Orka **0.4.1 at `252f058727eb7758383d74cd3b3431ce0c734830`** with **0.7.0 at `9b7727f6c5c9edd20f11a5a9d8faa3d777831145`**, in direct mode, three repetitions per case and version. It compares the whole instruction versions, not an isolated L2 effect. Both skill trees and their licenses were copied byte-for-byte from these Git commits before preparing the campaign. The 0.4.1 reference is the commit named in ECC-01, not an assumption that every commit declaring 0.4.1 is identical.

| New synthetic case | Purpose | Phase |
|---|---|---|
| `tournee-complete` | Make a useful logistics decision from sufficient information without an artificial question | Development |
| `devis-a-obtenir` | Obtain the decisive quote, track its version and preserve a separate unavailable fact | Development |
| `revision-reservee` | Revisit dependent conclusions after a contradictory version, preserve history and respect source boundaries | Reserved final check |

Read the **[frozen protocol](protocole.md)** for limits, evidence requirements, ordering and qualification rules. The **[public commitment](gel-public.json)** contains the exact Git references, per-file SHA-256 hashes, criteria commitments, 18 slot IDs and operator order. The **[preparation checks](verification-preparation.json)** describe software and integrity checks only.

## Reserved material stays local

Exact prompts, inputs, expected answers, conditional operator replies and the full sealed manifest are retained in the ignored local workspace, outside the distributed skill and this public directory:

```text
.orka/preparations/ecc-01-l4-2026-10-22/
  plan.json                 # Exact criteria and source paths
  operateur/procedure.md    # Selective distribution and fixed replies
  operateur/ordre.json      # Twelve development slots, then six reserved slots
  versions/                # Complete frozen instruction copies and LICENSE
  cas/                     # Three new cases, including reserved content
  bilan-initial.json       # All 18 slots still prepared
.orka/evaluations/ecc-01-l4-2026-10-22/
  manifest.json            # Sealed plan, matrix and copied-file hashes
  pieces/                  # Frozen copies; no results directory
```

These are local paths from the repository root, not missing public download links. **A public clone does not include the private fixtures and cannot reconstruct this campaign from hashes alone.** Preserve the local folders together in an authorized backup; Git publication does not back them up. Distribute only the selected version and the current case's allowed pieces to each evaluated context. Never give it the complete manifest or operator folder.

The preparation author knows the cases and expected answers. Reserved means withheld from production and candidate tuning, not unknown to its author. Separation is procedural: no sandbox, encryption or independent access audit was added. The candidate was fixed before case creation. If a new candidate is developed after reserved exposure, a new reserved case and campaign are necessary for an independent confirmation.

The preparation uses the existing [optional repository tool](../../docs/EVALUATIONS.md); its report is not a model response. All decisions and manual checks remain readable without Python. No new skill release or personal installation change accompanies this preparation. Actual L4 qualification, delegated C6 and any claim of quality or cost improvement remain unperformed.
