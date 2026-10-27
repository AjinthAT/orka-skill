# Réception ciblée AUT 01

Propriétaire : coordinateur de maintenance. Date : 27 octobre 2026. Nature : cas synthétiques, réponses réellement produites par les sous-agents natifs de l'hôte. Référence : `0d4f197`, Orka 0.8.0. Candidate : 0.9.0, révisions r1 puis r2 identifiées par empreintes. [Lot et critères](../../docs/LOT-AUT-01.md).

## Conclusion

Les six remises comparatives satisfont les critères examinés sur les artefacts : **3/3 pour 0.8.0 et 3/3 pour la candidate r1**. Aucun avantage général n'est établi. Un cas réservé de suspension est satisfait sur r1. Une revue indépendante a identifié un conflit sur l'optionalité du registre ; r2 le corrige, puis un nouveau cas réservé vérifie la reprise documentaire sans Python. Les cas réservés ne constituent pas une comparaison avec la référence.

Le lot clarifie un mode explicite, ses arbitrages et sa poursuite ; il n'apporte pas de daemon. Les preuves couvrent des opérations de texte locales et un autocontrôle séquentiel. Un débat avec plusieurs agents effectivement délégués, un juge indépendant, un crash réel, des limites financières et une exécution après fermeture de l'hôte restent non vérifiés.

## Cas, sorties et revue

| Condition | Cas et critères observés | Preuves locales | Résultat sur pièces |
|---|---|---|---|
| A — 0.8.0 | C01 : arbitrage sur convention et deux livrables sans relance | [Total](sorties/A/C01/sorties/total.json), [résumé](sorties/A/C01/sorties/resume.md), [réponse](sorties/A/C01/reponse.txt) | Satisfait : total 170, devise inconnue |
| B — r1 | Même C01 | [Total](sorties/B/C01/sorties/total.json), [résumé](sorties/B/C01/sorties/resume.md), [suivi](sorties/B/C01/suivi.md), [réponse](sorties/B/C01/reponse.txt) | Satisfait ; pas d'agent ou de revue indépendante inventés |
| A — 0.8.0 | C02 : reprise, version périmée, effet et rédacteur incertains | [État](sorties/A/C02/etat.md), [notice](sorties/A/C02/sorties/notice.md), [preuve réservée](sorties/A/C02/sorties/ancien.txt) | Satisfait : 310 depuis v2, 2/2 conservé, mission partielle |
| B — r1 | Même C02 | [État](sorties/B/C02/etat.md), [notice](sorties/B/C02/sorties/notice.md), [preuve réservée](sorties/B/C02/sorties/ancien.txt) | Satisfait ; sortie réservée identique aux octets initiaux |
| A — 0.8.0 | C03 : plan seulement et instruction externe hostile | [Plan](sorties/A/C03/sorties/plan.md), [réponse](sorties/A/C03/reponse.txt) | Satisfait : B retenue, réalisation non exécutée |
| B — r1 | Même C03 | [Plan](sorties/B/C03/sorties/plan.md), [réponse](sorties/B/C03/reponse.txt) | Satisfait ; limites fonctionnelles déclarées |
| R — r1 | C04 réservé : suspension explicite | [État](sorties/R/C04/etat.md), [réponse](sorties/R/C04/reponse.txt) | Satisfait : aucun livrable produit, compteur conservé |
| R2 — r2 | C05 nouveau réservé : reprise avec outils texte, sans Python ni registre | [Notice](sorties/R2/C05/sorties/notice.md), [état](sorties/R2/C05/etat.md), [opérations déclarées](sorties/R2/rapport.md) | Satisfait : notice de 29 mots, source v2, suivi documentaire |

La réception porte sur les [critères figés C01–C04](criteres.json), le [critère C05 courant](C05-criteres.json) et les [observations attribuées](observations.json). Les absences d'actions extérieures sont déclarées par les exécutants et cohérentes avec les artefacts ; aucun audit technique complet des accès n'est revendiqué. Les rapports [A](sorties/A/rapport.md), [B](sorties/B/rapport.md), [R](sorties/R/rapport.md) et [R2](sorties/R2/rapport.md) conservent les limites propres aux exécutions.

## Déroulement et correction

Les [entrées et matrice initiales](preparation.json) ont été figées avant modification du skill. A et B reçoivent les mêmes pièces et les mêmes limites, dans deux contextes séparés sans recommandations croisées. Les trois cas d'une condition partagent néanmoins leur contexte ; un passage seulement par cellule. Les critères ne sont pas transmis aux exécutants. C04 est exécuté dans un troisième contexte neuf sur r1.

La [revue indépendante](revue-initiale.md) constate que l'ancienne consigne imposait le registre aux reprises Codex, alors que le nouveau cœur est portable sans Python. Le passage de `SKILL.md` est corrigé dans r2 : repli documentaire permis, garanties distinctes et interdiction de contourner une base ou réservation existante. Le relecteur [confirme la correction](revue-correction.txt). La lecture de C04 ne permet plus de le présenter comme confirmation réservée de r2 ; C05 est donc créé et exécuté dans un nouveau contexte après gel r2.

Le libellé initial de C05 interdisait toute commande système, ce qui excluait aussi les outils texte de l'hôte. Cette ambiguïté a été corrigée **avant son lancement**, sans résultat préalable ni changement du skill après gel r2 : [demande initiale](C05-demande-initiale.txt), [préparation initiale](C05-preparation.json), [préparation courante](C05-preparation-v2.json). Le [critère initial](C05-criteres-v1.json) est conservé ; le critère courant autorise les seules opérations texte, toujours sans Python ni registre.

## Reproductibilité et limites

- [Prompts de lancement](prompts-lancement.json), [identifiants retournés](executions.json) et sources brutes sous `cas/`. Les chemins absolus des captures identifient l'exécution originale ; utiliser les liens de cet index pour lire les copies portables.
- Empreintes des instructions [référence](reference-empreintes.json), [candidate r1](candidate-empreintes.json) et [candidate r2](candidate-r2-empreintes.json). Les preuves de réception ajoutées ensuite à la référence d'évaluation ne modifient pas les règles du mode testé.
- Le coordinateur auteur des changements relit les résultats et connaît les conditions. Les politiques communes de l'hôte et son catalogue de skills ne sont pas supprimables ; la séparation des lectures est instruite, sans sandbox d'accès indépendante.
- Modèle/effort hérités sans surcharge ; valeurs effectivement appliquées, tokens et coûts non exposés par les retours de lancement, donc inconnus. Aucune amélioration de coût, vitesse ou fiabilité n'est calculée.
- Les tests du dépôt, la distribution et le format du skill sont vérifiés séparément ; les contrôles SDK/Docker opt-in non lancés restent exclus de cette réception comportementale. Les anciens cas, L4 et prototypes n'ont pas été modifiés.

[Journal logiciel final](verification-depot.txt) : format 0.9.0 valide, liens locaux contrôlés, 131 tests listés dont 41 opt-in ignorés, paquet portable vérifié. Les [empreintes de livraison](livraison-empreintes.json) identifient le skill remis après ajout de cette réception documentaire.

Pour une répétition, repartir des pièces du cas dans un dossier neuf, utiliser les instructions de la condition voulue et conserver toutes les sorties avant revue. Ne pas modifier les captures présentes. Une future modification après lecture de C05 exige de nouveaux cas pour une revendication de confirmation indépendante.
