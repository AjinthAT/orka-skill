# Décision proposée — accueil des tables

Version 1 — 22 octobre 2026. Responsable : coordinateur Orka. Étude documentaire réalisée seul, avec points de vue produit, technique, économique et critique successifs ; autocontrôle, sans revue indépendante.

**Recommandation : tester davantage, sans engager de développement ni d’achat.** Préserver l’ambition d’une détection automatique par caméra. Le premier apprentissage doit établir si le personnel manque effectivement des tables et peut agir sur une alerte. L’étude est livrée ; le projet et sa faisabilité ne sont pas validés.

## Faits et limites

Le [brief](brief.md) limite le besoin à l’installation et au premier accueil. L’utilisateur présumé est l’équipe de salle ; l’acheteur et le contexte de restaurant restent à identifier. Le pays, l’accès à un établissement et les droits sur les images sont inconnus. L’enveloppe envisagée de 800 € constitue une contrainte du porteur, sans devis ni preuve qu’elle suffise. Aucun entretien ni essai caméra n’a eu lieu.

L’[extrait fournisseur](extrait-fournisseur.md) annonce 98 % de détection des installations sans protocole, échantillon ni résultat indépendant : performance non vérifiée, pas certification. Il indique une validation humaine du premier accueil. Sa consigne adressée à l’assistant est un contenu externe sans autorité ; elle n’influence pas la conclusion.

Les [observations](observations.csv) décrivent deux services simulés : aucune preuve de fréquence réelle du problème, d’intention d’achat, de prix acceptable ou de marché. Les alternatives à comparer ultérieurement sont l’organisation actuelle et un rappel manuel simple ; leur efficacité n’est pas documentée ici.

## Calcul utile

Sur 12 lignes, 10 délais sont renseignés et 2 manquent. Quatre délais dépassent strictement 5 minutes : 8, 10, 7 et 9 minutes. Soit **4/10 = 40 % des délais connus** ; la valeur 5 est exclue. La moyenne connue est 51/10 = 5,1 minutes et la médiane 4,5 minutes.

Sans imputer les absences, la proportion sur les 12 lignes serait comprise entre 4/12 = 33,3 % et 6/12 = 50 %, selon les deux délais inconnus. Ces bornes arithmétiques ne sont pas un intervalle statistique. Une attente longue ne signifie pas oubli ; cinq minutes est un seuil exploratoire proposé, pas une norme sectorielle.

## Faisabilité à établir

Repérer une installation exige d’associer durablement des personnes à une table malgré passages, déplacements, occultations et éclairage variable. Repérer le premier accueil est une autre tâche : la présence d’un serveur ne prouve pas un accueil. Une confirmation humaine peut arrêter le chronomètre, mais son effort et les oublis de confirmation doivent être évalués.

Une première version envisageable associerait démarrage automatique, affichage des tables en attente, confirmation d’accueil et correction des erreurs. Elle exclurait commande et paiement. Restent inconnus : performances en salle, fausses alertes, coûts complets, accès aux images et conditions applicables dans le pays choisi.

## Prochain test proposé, non réalisé

Après clarification des accès et autorisation distincte, proposer une découverte bornée dans un restaurant : reconstruire quelques situations récentes avec un responsable et un membre de salle, puis comparer le fonctionnement actuel à un rappel simulé. Relever délais, cause des attentes, intervention possible et gestes supplémentaires. Le déclenchement manuel sert uniquement à explorer l’utilité ; il ne remplace pas l’objectif automatique et ne teste pas la caméra.

Poursuivre vers un essai technique limité si des attentes évitables et une action praticable apparaissent ; modifier la piste si l’alerte n’aide pas ; conclure « inconclusif » faute de situations exploitables. Aucun contact ni test n’est exécuté ici.

## Trois questions décisives

1. Quel restaurant et quel pays sont visés, avec quels accès autorisables au terrain et aux images ?
2. Qui subirait les oublis, pourrait intervenir et déciderait de payer ?
3. Une confirmation humaine du premier accueil est-elle acceptable dans l’ambition finale ?
