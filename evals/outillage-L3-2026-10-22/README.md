# L3 software validation — fabricated observations only

This directory demonstrates the optional [evaluation tool](../../tools/evaluer.py). **No model or agent was launched.** The two instruction versions, outputs, reviews, usage figures and durations are fabricated to exercise software behavior. This is not the L4 comparative campaign or evidence that one model/version is better.

The [input plan](entrees/plan.json) fixes one fictitious budget case, two fictitious instruction versions and three repetitions, with a maximum of six slots. The [frozen campaign](demonstration-simulee/manifest.json) retains copied inputs, exact prompts, criteria and hashes. Five declarations were imported; the sixth slot remains prepared.

| Slot | Fictitious version / repetition | Supplied record | Reported outcome |
|---|---|---|---|
| e0001 | fictive-a / 1 | [Original observation](observations/e0001/declaration.json), [output](observations/e0001/livrable.json), [frozen record](demonstration-simulee/resultats/e0001/rapport.json) | Success: total 120, margin 30, attributed simulated review |
| e0002 | fictive-b / 1 | [Original observation](observations/e0002/declaration.json), [output](observations/e0002/livrable.json), [frozen record](demonstration-simulee/resultats/e0002/rapport.json) | Failure: observed total 121 differs from expected 120 |
| e0003 | fictive-b / 2 | [Original observation](observations/e0003/declaration.json), [output](observations/e0003/livrable.json), [frozen record](demonstration-simulee/resultats/e0003/rapport.json) | Interrupted; retained, outside the comparable denominator |
| e0004 | fictive-a / 2 | [Original observation](observations/e0004/declaration.json), [output](observations/e0004/livrable.json), [frozen record](demonstration-simulee/resultats/e0004/rapport.json) | Outside protocol; deviation retained, no comparable success counted |
| e0005 | fictive-a / 3 | [Original observation](observations/e0005/declaration.json), [output](observations/e0005/livrable.json), [frozen record](demonstration-simulee/resultats/e0005/rapport.json) | Inconclusive: required review absent, not automatically approved |
| e0006 | fictive-b / 3 | No imported observation | Still prepared, not executed |

The [captured report](bilan.json) shows **1 success / 2 evaluable rows** alongside **1 success / 6 planned slots**, one known failure, one interruption, one deviation, one inconclusive row and one prepared slot. It records five fabricated observations and **zero declared real executions**. These denominator checks, rather than a best-output selection, are the point of the example.

Only one observation has fabricated token figures: the report retains partial coverage, not a complete usage total. Fabricated EUR estimates and USD actual-labeled amounts remain separate because both amount nature and currency matter; the entire campaign is a simulation, so neither is a real cost. Applied settings remain unknown. The illustrative 9.5-second wall duration is not model compute time. Trace coverage is a declaration, not an audit.

Recompute the report without changing this directory:

```sh
python3 -B tools/evaluer.py bilan --campagne evals/outillage-L3-2026-10-22/demonstration-simulee
```

To replay the software workflow, prepare the [same plan](entrees/plan.json) with `--racine` pointing to a separate temporary folder, then import the five declarations there. Their fingerprints match a deterministic preparation of the same input bytes. Replaying these files does not rerun models. Do not import into the captured campaign or overwrite its report.

A [manual count](controle-manuel.md) reads the same matrix without running Python; it is a documentary self-check, not an independent agent trial.

The [acceptance record](../../docs/VALIDATION-L3.md) maps E1–E6 to the [regression tests](../../tests/test_evaluer.py), this example and preservation checks. The [file-hash index](empreintes.json) covers the captured example. Existing evaluation directories and their original hashes remain unchanged; only the parent navigation index gains this software example.
