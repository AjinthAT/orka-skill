# Repeated evaluations — optional repository tool

`tools/evaluer.py` freezes a campaign, records supplied observations and produces a JSON report. It uses Python 3.10+ and the standard library only. It never launches models, agents, inspected code or network requests. It is a repository maintenance tool, not part of the installed skill ZIP. The [document-based procedure](../.agents/skills/orka/references/evaluation-agents.md#préparer-et-relire-des-répétitions) remains usable without Python.

## Workflow

From a reviewed repository, prepare a new campaign in the default ignored workspace:

```sh
python3 -B tools/evaluer.py preparer --plan /path/to/plan.json
```

The destination is `.orka/evaluations/<id>/`; `--racine /path/to/new-campaigns` changes its parent. The tool creates an exclusive directory, copies the declared inputs and exact UTF-8 prompts, freezes the plan and criteria, and assigns IDs such as `e0001`. Existing destinations, including empty folders or symbolic links, are refused. Preparation does not authorize or perform an execution.

Inspect `manifest.json` for the case/version/repetition matrix. The preparation output and a subsequent report include each `empreinte_execution`, which ties a supplied observation to this frozen campaign and run. Inputs are independent copies: changes to the original source files do not update them. Changes to a frozen copy or a manifest with an inconsistent hash block import and reporting. A new intended input version needs a new campaign ID.

After a separately authorized execution, import its supplied observation and listed output files:

```sh
python3 -B tools/evaluer.py enregistrer --campagne .orka/evaluations/example --execution e0001 --resultat /path/to/observation/declaration.json
python3 -B tools/evaluer.py bilan --campagne .orka/evaluations/example
python3 -B tools/evaluer.py bilan --campagne .orka/evaluations/example --output /path/to/new-report.json
```

Import preserves the original declaration bytes and output bytes under `resultats/<execution>/`, with hashes. A slot accepts one immutable observation; duplicate imports and overwritten reports are refused. For a retry, create a new plan and ID with `origine` identifying the earlier campaign/run and the reason. Keep the initial result visible in the overall qualification review; this tool does not merge campaigns or silently replace a failed repetition with a retry.

The report is read-only unless a new `--output` file is explicitly requested. It can describe a partial or interrupted campaign without turning unrecorded slots into completed runs. Code 0 means the command completed, including a partial report or a report containing failures. Code 2 means invalid arguments, data, paths, unreadable files or inconsistent hashes. Criterion failures are report data, not successful qualification.

## Plan format 1

The [complete synthetic plan](../evals/outillage-L3-2026-10-22/entrees/plan.json) is a runnable example. All examples in that directory are fabricated software-test data, not model measurements.

| Field | Contract |
|---|---|
| `format`, `id` | Integer 1 and a unique portable lowercase identifier, 1–64 letters/digits/underscores/hyphens; Windows device names are refused |
| `origine`, `hypothese` | Provenance/purpose and the question being tested; identify the earlier run when planning a retry |
| `nature` | `simulation` for fabricated observations or `reelle` for separately observed executions; the campaign does not mix these categories |
| `hote` | Expected host; a different reported host is retained as a protocol deviation |
| `repetitions`, `max_executions` | Positive integers; cases × versions × repetitions must fit the explicit maximum |
| `limites` | Nonempty list of limits, including allowed tools, actions, context, global agents and stopping conditions; the tool does not enforce external permissions or spending |
| `versions` | Nonempty list of unique `id`, `provenance`, `instructions` (file paths) and `reglages_demandes` (null for inherited/unknown, or `modele`/`effort` strings) |
| `cas` | Nonempty list of unique `id`, `origine`, `usage` (`developpement` or `reserve`), `entrees` (paths), `prompt` (one exact text file) and `criteres` |

File paths are relative to the plan's folder; absolute paths, parent traversal, nonportable components, symbolic links and reparse points are refused. Stage any necessary external references in that folder before preparation. Only explicitly listed files are copied. Version provenance describes those supplied files, not an authenticated Git checkout. Each file is limited to 16 MiB.

The order alternates the version list between case/repetition combinations. It is frozen before observation; it is not randomized or automatically balanced across hosts. The prompt remains byte-for-byte the supplied text. Provide the correct frozen instructions and context separately through authorized host mechanisms; do not pass the entire manifest, expected answers or review criteria to the production agent. Filesystem isolation and reserved-case secrecy are not enforced by this tool.

Each criterion has a unique `id`, `description`, Boolean `obligatoire` and `type`. At least one criterion per case must be indispensable. Supported types:

| Type | Additional fields and behavior |
|---|---|
| `json_egal` | `fichier`, `chemin`, `attendu`; compare the structured selected JSON value exactly, including scalar types, without matching a phrase in prose |
| `json_nombre` | `fichier`, `chemin` and at least one inclusive `minimum`/`maximum`; check a finite number, rejecting strings and Booleans |
| `revue` | No automatic-check fields; use an attributed judgment supplied with the observation, or leave it unverified |

`chemin` is a list of object keys and nonnegative array indices, such as `["budget", "total"]`. An empty list selects the whole document. Missing or malformed outputs, wrong structures and unmet deterministic checks produce `non_satisfait`, with the observed value or error. A reviewer cannot override these checks by importing a review for their IDs. Arbitrary commands, Python expressions and executable plugins are not supported.

JSON keys must be unique and unknown schema fields are refused. Documents and reports use UTF-8. Versioned manifests and imported records contain integrity hashes; these detect accidental changes, not deliberate forgery by someone able to rewrite data and hashes.

## Observation format 1

Start from a supplied result such as this **simulated** declaration, replacing its fingerprint with the one printed for the prepared slot:

```json
{
  "format": 1,
  "execution": "e0001",
  "empreinte_execution": "fingerprint-from-the-prepared-campaign",
  "nature": "simulation",
  "etat": "terminee",
  "provenance": {
    "source": "Fabricated observation for a software test",
    "hote": "fixture-locale",
    "id_natif": null
  },
  "sorties": ["livrable.json"],
  "ecarts": [],
  "revues": {}
}
```

`etat` is `terminee`, `interrompue` or `hors_protocole`; a deviation needs a nonempty reason in `ecarts`. Reasons are retained even when the caller declares another state. Known host or applied-setting differences also classify the row as outside protocol. The original declared state remains in the detail. Output paths are relative to the declaration's folder. An empty output list is accepted to retain an execution that produced nothing; required deterministic output criteria then fail.

For `nature: reelle`, a nonempty native context ID is required and cannot be reused in the same campaign. For a simulation, it must be null. This is a provenance contract, not a native-host verification: a fabricated string is not proof of execution. The source and host must always be supplied. A prepared slot has no observation and cannot be imported as executed merely by changing its label.

`revues` maps only review-criterion IDs to `etat` (`satisfait`, `non_satisfait`, `non_verifie`), `auteur`, `source` and `preuve`. All text fields must be nonempty. Review evidence remains a judgment, not a deterministic proof or a vote-based approval. Missing review evidence remains unverified.

Optional measurement fields are null or omitted when unavailable:

| Field | Required contents when supplied |
|---|---|
| `reglages_appliques` | `modele`, `effort`, `source`; never inferred from the request |
| `tokens` | Unique measurement `id`, `source`, `perimetre: execution_exclusive`, nonnegative integer `entree`/`sortie`; exclude children and cumulative snapshots |
| `cout` | `montant` as a nonnegative decimal string (up to 18 integer and 9 fractional digits), `nature: estime` or `constate`, uppercase three-letter `devise`, `source` |
| `traces` | `couverture: non_verifiee`, `partielle` or `complete_declaree`, and `source`; not an access audit |
| `duree_observee` | Nonnegative finite `secondes`, `nature: murale`, `source`; not model compute time |

The tool rejects reused measurement IDs and cumulative token labels. Distinct IDs may still hide overlaps: the operator must verify exclusivity and coverage. A single cost per observation avoids adding its estimate to its actual amount. No tariffs, currency conversions, account quota inference or automatic telemetry are provided.

## Read the report

The report preserves every planned row and all criterion observations. It groups results by case/version and shows states, successes, failures and inconclusive rows, without selecting a best repetition.

- `prevues` counts matrix slots; `enregistrees` counts supplied observations. `executees_reelles_declarees` counts real observations with the required declared provenance; `observations_simulees` remains separate.
- Effective states partition the slots: still prepared, completed, interrupted or outside protocol. The original state and deviations remain in each imported row.
- Only completed rows within protocol can be comparable successes, failures or inconclusive results. A mandatory failure is a failure; otherwise a mandatory unknown makes the row inconclusive. Success requires every mandatory criterion to pass.
- `evaluables` is successes plus failures. Read `succes_sur_evaluables` together with `succes_sur_prevues`, prepared/interrupted rows and unknowns. The latter is a count against the planned denominator, not a claim that missing runs failed.
- Criterion counts also retain unverified and unevaluated slots. Judgments and deterministic controls are labeled separately.
- Usage totals are known subtotals over all imported rows, including noncomparable ones, with measurement-coverage counts. Unknown per-row values stay null; no known token measurements yields null totals. Cost subtotals remain separated by currency and estimate/actual nature.

An overall `etat: complet` means all planned rows have a definite completed result, including failures. It does not mean qualification passed. The tool does not promote a candidate or establish a quality/cost advantage. L4 remains a separately authorized comparison and review.

## Preservation and limits

The [software regressions](../tests/test_evaluer.py) use temporary folders and fabricated data. Existing evaluation directories, personal installations, settings and SQLite registers are not migrated or rewritten. Frozen campaigns can be moved with their copies intact. A prototype output is copied and hashed, never imported as code or executed; rechecking a prototype separately must use another temporary copy and its own authorization.

Use copies that are not being edited concurrently. Static path checks, exclusive creation and hashes do not constitute a sandbox against concurrent filesystem changes. A hard interruption during creation may leave an incomplete folder; inspect and preserve it before choosing a new ID rather than silently replacing it. Publication and redaction remain manual, authorized work; the tool does not export private sessions or certify provenance.
