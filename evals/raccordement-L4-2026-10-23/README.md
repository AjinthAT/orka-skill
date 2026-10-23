# L4 — MCP connection preparation, without a model

Owner: maintenance coordinator. Version 1, 23 October 2026. Scope: prepare a narrow connection for the [isolated file adapter](../environnement-L4-2026-10-23/README.md) and check it on independent fictitious data. **The transport works with a software client. No Codex conversation or model was created, and no personal setting or frozen campaign was changed.**

## Delivered

- Repository-only [MCP stdio bridge](../../tools/raccorder_fichiers.py), Python 3.10+ and standard library only. It starts the explicitly selected file adapter, never a model or Codex client. It is outside the installed skill ZIP.
- Three tools: `lister`, `lire`, `ecrire`. The operator fixes the adapter path, its SHA-256 and the execution ID on the server command line; those are absent from the tools' schemas. There is no command, URL, model, sampling or execution-selection tool.
- Fourteen **inactive, uninstalled** connection templates: twelve for the existing development slots and two for the software probes. They remain outside any automatically loaded `.codex/` folder and have `enabled = false`; no `codex mcp add`, user config edit, login or installation was performed.
- Two independent fictional datasets, ALPHA and BETA, with no Orka instructions, business inputs, expected answers or reserved content. The byte-identical file adapter was copied into this probe workspace and bound to those datasets only.
- [Ten software regressions](../../tests/test_raccorder_fichiers.py) and two actual end-to-end software connections: MCP stdio → fixed adapter → restricted Docker file process. The [captured parsed messages and responses](traces-sondes.json) contain synthetic data only. The [verification record](verification.json) states what was and was not tested.

The durable local workspace is `/Users/ajin/Projets/orka-l4-raccordement-2026-10-23/`. Its `controle/` folder contains the reviewed bridge copy, the inactive `connexions/*.toml` templates, their operator index and a launch checklist. Its separate `sonde/` folder contains only the two fictional input/output trees and the copied adapter. These local artifacts are not supplied by a public clone. The original twelve environments, their connection contract and prepared containers were preserved.

## Checks actually performed

Each probe starts a fresh **server process and software protocol connection**, not a fresh model chat. It sends `initialize`, `notifications/initialized`, `tools/list`, then tool calls. The two clients negotiate protocol `2025-11-25`; only `tools` capability is advertised. No server-wide model instructions or additional workflow were inserted.

The client lists the three tools, reads its own ALPHA or BETA notice, writes a UTF-8 note and reads back the exact bytes. It verifies that absolute paths, traversal toward the operator directory, selection of another execution and arbitrary commands are refused. Listing tools again shows the unchanged three-tool surface. The process exits on end-of-input; stderr contains no diagnostics. The synthetic output notes and parsed transcripts are retained as software evidence, outside every L4 output directory.

After making the adapter subprocess's UTF-8 mode explicit for cross-platform behavior and enforcing UTF-8 decoding of transport frames, both software connections were rechecked after each adjustment and returned identical parsed responses. The earlier bridge copies and first capture remain archived locally; the verification record distinguishes two initial connections, two intermediate rechecks and two final rechecks. These are software reruns, not additional model repetitions.

The regression suite additionally covers lifecycle gating, protocol negotiation, notifications that cannot invoke tools, malformed or duplicate JSON keys, oversized frames, a changed adapter hash, backend failures, and real subprocess stdio with no protocol pollution. The tests use temporary fake adapters and no Docker, network or model, so they run in the repository CI.

The bridge implements only the documented tools-only subset of MCP `2025-11-25` and compatible `2025-06-18`, rather than claiming complete support for every newer MCP revision. A client proposing another revision receives the supported revision and must accept it or disconnect. Compatibility with an actual installed Codex client remains untested. References: [MCP lifecycle](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle), [tools](https://modelcontextprotocol.io/specification/2025-11-25/server/tools), [stdio transport](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/stdio).

## Route to a future new session

The prepared command launches only the MCP bridge. The local templates bind one execution per connection and restrict its exposed tool names. The [official Codex MCP documentation](https://learn.chatgpt.com/docs/extend/mcp) describes how clients load stdio server commands and project/user configuration. **A connection template does not create or isolate a conversation, disable other host tools or override inherited settings.** Nothing was loaded into this chat.

Before any separately authorized model execution, the host must demonstrably provide:

1. A new conversation without preparation history or reused/resumed conversation ID; the selected frozen prompt and instruction copy only. Do not fork this maintenance chat.
2. Only the three bound file tools. No generic shell, direct host filesystem, Docker socket/command, Web, connector, memory, unrelated skill or delegation bypass. The trusted operator retains control of the adapter, its parent directories and the binding; hashes detect changes but do not authenticate a malicious controller.
3. The same recorded host conditions and requested settings for both versions, with applied values unknown unless a native source exposes them. Preserve the original inherited request; this preparation chooses no model or effort.
4. Native context identity, effective tool catalogue, available traces/settings and confirmed end-of-writer observations before accepting an actual run. The bridge's EOF and per-call timeouts are not a native model stop test or spending limit.

The current host exposes no tool in this conversation for registering such a server while simultaneously replacing the full inherited tool catalogue and history. That limits what this preparation can certify; it does not establish that every client lacks this capability. Actual registration, fresh-context proof, native tool restrictions, model telemetry and qualification are **not verified**. No personal configuration was changed to bypass that limitation. The local `SESSION-READINESS.json` is a checklist, not an invented API payload or effective config.

If the host cannot meet these conditions under the frozen protocol, preserve the original campaign and prepare a separate host/protocol proposal. Do not relabel a CLI/custom runner as the planned desktop condition or overwrite the sealed plan to fit a tool. No new campaign or reserved case was created here.

## Preservation and limits

The reserved fixtures, exact criteria, operator procedure, private plan and full campaign manifest were not opened. Public records and inspected personal settings/skill metadata were checked unchanged against the pre-work snapshot; a complete campaign seal recheck was deliberately not attempted. The twelve development output directories remain empty, their prepared containers were not started, and no result was imported into L4. Only disposable file processes for the independent software probes ran.

This is a preparation and transport result, not a model benchmark, complete MCP certification, independent security audit or evidence of improved quality/cost. The controller remains a trusted local process with its existing host permissions; protecting the model tool surface and starting a fresh model context are separate host responsibilities. No background server, automation, credential copy or personal installation was introduced, and no model cost is inferred from these probes. The skill remains 0.7.0 and usable without Python; the bridge is optional repository maintenance tooling.
