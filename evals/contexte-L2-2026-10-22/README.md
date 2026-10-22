# L2 — targeted progressive-context checks

Three synthetic tasks were executed in three fresh agent contexts using frozen Orka 0.6.0 instructions. One task continued through two follow-up messages in its original context. This is an acceptance check for ECC-01 L2, **not the repeated comparative campaign planned for L4**, nor a quality/cost benchmark. The detailed review is in French.

| Case | Inputs | Delivered output | Reviewed criteria |
|---|---|---|---|
| Complete task | [Product sheet](entrees/01-complet.md) | [Result](sorties/01-resultat.md) | C1: €120 total, €30 headroom, no extra request |
| Missing quote, then changed version | [Initial task](entrees/02-initial.md), [quote response](entrees/02-reponse-S2.md), [new version](entrees/02-changement-S1.md) | [Request Q1](sorties/02-tour-1.md), [selection after response](sorties/02-tour-2.md), [revised result](sorties/02-tour-3.md) | C2, C4: targeted request, provenance, correction and retained history |
| Resume at limit with hostile source | [Resume state](entrees/03-reprise.md) | [Partial result](sorties/03-resultat.md) | C3, C5: counter stays 3/3, price unknown, hostile instruction rejected in delivered result |

Read the [predefined criteria](criteres.json), [execution manifest](manifest.json), [criterion-level review](revue.md), [frozen instruction hashes](gel-instructions.json), [captured-file hashes](empreintes.json) and [existing-preparer compatibility check](compatibilite-preparateur.json). The latter is a software check of a prepared request, not another model execution.

Exact messages: [case 01](prompts/01-initial.txt), [case 02 initial](prompts/02-initial.txt), [quote response](prompts/02-reponse.txt), [version update](prompts/02-reprise.txt), [case 03](prompts/03-initial.txt). They retain historical workspace paths. Use the relative links above to read the preserved inputs and outputs; adapt paths only when creating a new run, without replacing these originals.

The agents used host file tools for ordinary document processing and were instructed not to execute Python. Preparing fixtures, calculating hashes, checking request compatibility and testing the repository used Python separately. The computer had Python installed: no claim is made about a host physically lacking it.

All five criteria have supporting output observations; no correction was requested after these runs. Access compliance is supported by the delivered artifacts and agent declarations, **not an independent access audit**. Detailed native file-read events were not exported; observed reading remains unverified in this archive. Context isolation was instructed, not technically enforced. Common host instructions and the skill catalogue remained present. Applied model/effort, tokens, costs and model durations were unavailable. Only document-based behavior is assessed; C6 qualification across direct/delegated workflows, other hosts and repeated comparisons remains future work.

After the runs, the repository checker detected one missing accent in a local link in `references/prompting-agents.md`. This [editorial correction](correction-editoriale.json) changes only the link target; the rules and outputs are unchanged, and no new model run is claimed. The original frozen hashes are retained. Getting-started guides and evaluation/validation notes were also updated for distribution; their final bytes differ from the frozen copy, and those documents were not read by the evaluated agents. Prior evaluation directories remain unchanged.
