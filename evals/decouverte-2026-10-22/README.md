# README discovery test

[All evaluations](../README.md) · [Report in French](rapport.md) · [Orka](../../README.md)

One agent in a fresh conversation tested the public welcome flow at commit `8104bac`, starting with the README alone, then following its linked guides and download. **No blocker was observed on the route tested.** The public ZIP was downloaded and extracted, and a first mission message was prepared. Host activation and mission execution were not tested. No welcome documents were corrected.

| Evidence | Contents |
|---|---|
| [Report](rapport.md) | Findings, coordinator checks, remaining unknowns and limits; in French |
| [Protocol](protocole.md) | Plan and scope fixed before launch |
| [First impression](sorties/premier-regard.md) | README-only checkpoint, captured before the final delivery |
| [Journey](sorties/parcours.md) | Steps, findings and prepared first message |
| [Trace](sorties/trace.json) | Declared documents, actions and available measurements |
| [Archive inventory](sorties/archive-manifest.json) | The 41 ZIP entries |
| [Download headers](sorties/zip-http-headers.txt) | Recorded HTTP response chain, with cookies and temporary signed parameters redacted |
| [Coordinator checks](verification.json) | Archive hash, extracted-file equality and comparison to the frozen sources |
| [Manifest](manifest.json) | Reference, input hashes, requested/unknown settings, agent ID and output hashes |
| [Mandate](prompt.txt) · [Launch](lancement.txt) | Exact test instructions; historical temporary paths are retained |

The original agent outputs remain unchanged locally. Public copies redact only temporary signed download parameters and cookie headers; both original and public-copy hashes are recorded. Navigation links here are relative; historical paths inside raw records are not portable entry points.

This is an exploratory AI-agent test of one route, not a human usability study or a cross-host qualification. Requested model: `gpt-6.1-sol`, effort `medium`; applied settings, token usage and cost were unavailable. Read the report before generalizing the result.
