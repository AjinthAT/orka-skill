# L4 — isolated file environments prepared

Owner: maintenance coordinator. Version 1, 23 October 2026. Scope: preparation after the [L4 preflight](../precontrole-L4-2026-10-22/README.md), with no evaluated model or subagent launched. **Twelve development file environments are ready and locally tested; a future model conversation and its tool routing remain unvalidated.** The [frozen campaign](../preparation-L4-2026-10-22/README.md) is unchanged.

## Prepared locally

The durable local directory is outside the maintenance repository:

```text
/Users/ajin/Projets/orka-l4-essais-2026-10-23/
  controle/
    environnement.json          # Operator-only mapping and hashes
    prompts/<execution>.txt     # Exact frozen initial messages
    complements-developpement/ # Three exact case-02 replies, outside all mounts
    conservation-initiale.json  # Original public records/settings hashes
    SESSION-CONTRACT.json       # Requirements for a future client, not loaded config
    fichiers.py                # Bounded file adapter; no model launcher
    PREPARATION.md              # Local operating notes
  essais/<execution>/
    entrees/
      .agents/skills/orka/      # Only that execution's complete frozen version
      dossier.md or index.md   # Only its allowed initial business piece
      sorties/                # Empty mountpoint
    sorties/                  # Separate writable directory, still empty
```

These are local artifacts, not downloadable contents of the public repository. Each of the twelve development slots has a distinct folder and a distinct **created, never-started** Docker container named `orka-l4-env-20261023-<execution>`. The operator mapping preserves original IDs, repetition numbers and version order. No reserved slot was provisioned. No expected answer, rubric, operator response, full private plan, private campaign manifest, authentication file or host config was copied into a production input tree.

The image is official `alpine:3.22`, resolved and fixed by immutable digest in [verification.json](verification.json). It was downloaded for this preparation; no Codex binary, SDK or model client was installed or invoked. The existing Docker daemon was used without changing its settings or touching unrelated containers. Only the new preparation's containers and disposable probes were created. The two personal Orka/settings files inspected for preservation were read and hashed, never mounted or edited.

The three exact replies for the quote-development case were separately hash-checked and staged in the operator-only control directory. They are outside every container mount and must be delivered only when their frozen trigger applies. No reserved or general operator procedure was opened to stage them.

## Verified boundary

| Control | Observed result |
|---|---|
| Exact instruction and input bytes | Every provisioned file matches the corresponding public frozen hash; each input tree contains only its selected version and initial piece |
| Working directory | `/essai`, inside the container, with no mounted repository, home directory, parent `AGENTS.md`, operator directory or other run |
| Input mount | `/essai` read-only; attempted creation under the input mount rejected |
| Output mount | Only `/essai/sorties` writable for business files; UTF-8 write/read/delete probe succeeded, then outputs left empty |
| Container root | Read-only; attempted creation under `/tmp` rejected |
| Permissions | Non-root user, all Linux capabilities dropped, no new privileges, no privileged mode and no Docker socket |
| Network | `none` network mode; only loopback interface, no external route, connection probe to a documentation-only address failed |
| Resources | Per software container: 128 MiB memory, 0.5 CPU and 32 processes; these do not limit future model tokens or cost |
| Environment | Only the image's ordinary path and explicit locale; no host credentials or personal configuration forwarded |
| Model activity | Zero model runs, zero observations imported; prepared containers remain stopped and outputs empty |

Nine disposable software probes ran under the same restrictions for each of the twelve slots: **108 passing local probes**, separate from L4 observations. Their checks and the prepared-slot list are in [verification.json](verification.json). These probes test filesystem/network behavior, not model adherence, complete security against container escape, or review quality.

An operator-side adapter is also prepared locally: `controle/fichiers.py`. It accepts one UTF-8 JSON request with `action: lister`, `lire` or `ecrire`; the operator fixes the execution ID separately, outside the model's request. Reads are limited to that slot's explicit file inventory and its two output files; writes are limited to `sorties/livrable.json` and `sorties/note.md`. There is no command, mount, URL, image, model or execution-ID field under model control. File operations use disposable containers with the same restrictions. Twenty-one software checks across both instruction versions cover ordinary reads, UTF-8 output round trips and refusal of traversal, absolute paths, arbitrary commands, another execution, duplicate keys and unprepared slots. Probe outputs were removed after verifying their bytes; business outputs remain empty. This adapter has not been registered with a model host or exposed as a connected service.

The first software probe found a missing nested output mountpoint. Its failed preparation is preserved locally in the sibling `orka-l4-essais-2026-10-23-tentative-1/`, including its inspection and cause. Its single never-started prepared container was removed after verifying ownership and state. The mountpoint was created before retrying; the successful preparation is separate. Neither attempt is a model repetition or a campaign result.

## Remaining host boundary

Docker constrains the **file-tool process** when that process actually runs in the prepared container. It does not change the permissions, history, skill catalogue or connectors of this current Codex conversation. The [official OpenAI configuration documentation](https://learn.chatgpt.com/docs/config-file/config-basic) describes user and project configuration layers; creating these folders does not clear them from an existing chat. [Subagents also inherit parent settings and permissions](https://learn.chatgpt.com/docs/agent-configuration/subagents).

`SESSION-CONTRACT.json` is an operator checklist, **not an installed Codex config, working model runner or connected tool service**. A future host must supply a genuinely new conversation with the exact selected prompt and instructions. Its file tools must operate only through the matching container; generic host shell, direct filesystem, browser, network, connectors, unrelated skills and delegation must not remain available as bypasses. No Docker socket or unrestricted Docker command tool may be given to production. Keep the controller and its operator files outside that context. No model/effort preference or personal configuration was changed to achieve this preparation.

Before an actual run, record the host and requested/applied settings that are exposed, confirm this tool arrangement is compatible with the frozen protocol and obtain native evidence for the fresh context. This has deliberately not been tested by starting a model. If the required arrangement changes the frozen host or protocol, preserve this campaign and prepare a new protocol/campaign; do not silently relabel a CLI or container-based model as the planned desktop condition. No new campaign was created here, and no reserved content was opened to prepare one.

The temporary tool probes are not connected to a model usage meter or native stop confirmation. Model telemetry, history isolation, operator reply delivery, model stop behavior and actual parameters remain unverified until a separately authorized execution. No budget, actual usage or qualification result is inferred from this setup.

## Preservation

The original L4 public preparation/preflight records and the inspected personal configuration/skill metadata remain byte-identical. No private plan or full sealed campaign was read: a full seal recheck would require opening reserved copies. No result directory was created in the frozen campaign. The reserved case and its six slots remain unprovisioned. No personal installation, preference, authentication, automatic task or background model process was changed or started.

The official image remains cached and the twelve prepared containers consume metadata/disk only while stopped. Local folders and prepared containers are not backed up by this public commit. Cleanup must identify only this preparation's exact names/IDs from its local control manifest and verify that no writer is running; never use a global Docker prune or remove unrelated resources.
