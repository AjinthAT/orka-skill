# Revue documentaire indépendante AUT-01

Date : 27 octobre 2026. Périmètre : diff documentaire de la candidate locale 0.9.0 contre HEAD 0.8.0, nouvelle référence `autonomie.md`, fiche `docs/LOT-AUT-01.md` et références existantes utiles. Aucun accès réseau, lancement d'agent descendant, modification du dépôt ou consultation des dossiers d'expériences comportementales. Cette revue ne démontre pas le comportement d'un modèle.

## Constat actionnable

**P2 — Rendre cohérente l'optionalité du registre pour la reprise sur Codex.**

- `.agents/skills/orka/SKILL.md:40` conserve l'instruction : « Pour une mission Codex nécessitant suivi persistant, reprise ou capacité partagée entre coordinateurs, utiliser le registre de supervision locale […] avec une base explicitement choisie. »
- `.agents/skills/orka/references/autonomie.md:29` demande désormais de conserver un point de reprise pour le mode autonome. Son paragraphe de ligne 33 n'explicite le suivi documentaire sans registre que « Sur un autre hôte ».
- `docs/LOT-AUT-01.md:7-9` annonce au contraire un cœur utilisable sans Python et précise : « Le registre SQLite existant reste facultatif ».

Une mission autonome Codex avec reprise entre donc dans la condition impérative du `SKILL.md`, malgré l'optionalité annoncée par AUT-01. Cela peut imposer Python et une base SQLite à une mission qui devrait pouvoir se poursuivre avec son seul suivi documentaire. Aligner la règle d'entrée et le paragraphe de reprise : préciser que le suivi documentaire est également valable sur Codex quand le registre n'est pas utilisé, tout en conservant les obligations de même base et de transitions quand il l'est.

## Autres axes examinés

Aucun autre défaut actionnable constaté sur la portée du mandat, l'absence de nouvelle autorisation par un verdict, les règles d'arrêt et de suspension, la conservation des compteurs et effets incertains, la protection des rédacteurs actifs ou les capacités annoncées de l'hôte et d'un lanceur futur. Les règles examinées distinguent les fonctions documentées des mécanismes effectivement fournis.
