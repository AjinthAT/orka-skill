# Bien démarrer avec Orka

[English guide](GUIDE.md)

Orka organise une équipe IA autour de votre projet : clarifier une idée, étudier un marché, préparer du marketing, coordonner un développement ou suivre les résultats. Vous donnez une mission ; Orka choisit les points de vue utiles, vérifie les preuves accessibles et vous remet un résultat avec ses limites et la prochaine étape recommandée. Les rôles disponibles ne sont pas tous lancés à chaque mission.

**Vous pouvez commencer sans Python.** Le cœur du skill est en Markdown : l'assistant lit les instructions et utilise ses outils. Une copie complète du dossier `orka` ou l'import de son ZIP dans une interface compatible suffit pour l'installation manuelle. Les fonctions disponibles restent celles de votre assistant ; installer Orka ne lui ajoute pas automatiquement le Web ou des sous-agents.

| Usage | Python |
|---|---|
| Lire le skill, cadrer, étudier, rédiger et coordonner avec les outils de l'assistant | Non requis par Orka |
| Installer avec le script `install.py` | Python 3.10+, facultatif si vous installez manuellement |
| Utiliser préparateur, registre SQLite ou bilan local | Python 3.10+, uniquement si ces contrôles sont utiles |
| Maintenir et tester le dépôt Orka | Python et dépendances de développement, hors usage courant |

Commencez avec les documents de mission. Le registre devient utile pour partager des réservations entre coordinateurs, conserver les tentatives et contrôler les versions après interruption ; le préparateur rend des mandats répétables et le bilan exploite des mesures fournies. Ils ne sont pas nécessaires à chaque mission et ne lancent pas les modèles. Les exigences de votre propre projet restent distinctes de celles du skill.

## 1. Ouvrir Orka

Si l'installation pose question, vous pouvez la vérifier **sans Python** : ouvrez le dossier `orka` configuré, vérifiez `SKILL.md`, les deux guides, la licence et les ressources de l'archive ; essayez leurs liens, puis vérifiez séparément la sélection d'Orka dans une nouvelle session. La [procédure complète](references/diagnostic-installation.md) décrit aussi le diagnostic Python facultatif en lecture seule et la comparaison avec une référence connue. Aucun contrôle automatique n'est nécessaire avant chaque mission.

Dans votre assistant, sélectionnez Orka avec son mécanisme de skills. Les points d'entrée documentés dans le dépôt sont `$orka` pour Codex et `/orka` pour Claude Code ou Hermes ; sur une autre interface, demandez d'utiliser Orka. Si le skill n'est pas encore visible, ouvrez une nouvelle session.

Pour être guidé, copiez ce message après avoir sélectionné le skill :

```text
Orka, présente-moi brièvement ton fonctionnement et aide-moi à choisir ma première mission à partir de mon projet. Utilise les informations déjà présentes et demande seulement ce qui manque pour commencer.
```

Si vous avez déjà donné une mission concrète, Orka commence celle-ci directement. Vous pouvez demander ce guide à tout moment ; il n'est pas nécessaire de le relire à chaque projet.

## 2. Donner une mission utile

Précisez ce que vous savez : le projet ou problème, le résultat attendu, le dossier de travail et les contraintes importantes. Ajoutez la cible, le pays, l'échéance ou le budget seulement lorsqu'ils sont connus et pertinents. Une idée encore floue suffit pour commencer le cadrage ; Orka doit distinguer vos choix, les faits vérifiés et les hypothèses.

Choisissez le prompt correspondant à votre besoin. Les exemples qui reprennent une idée ou un dossier supposent que vous l'avez déjà décrit ou rendu accessible.

**Clarifier une idée :**

```text
Orka, reprends l'idée que je viens de décrire. Aide-moi à préciser le problème, les utilisateurs, l'acheteur et le résultat recherché. Préserve mon ambition, vérifie les faits accessibles et pose les quelques questions qui peuvent changer la prochaine décision.
```

**Lancer une étude :**

```text
Orka, étudie ce projet : besoin, alternatives et concurrents, faisabilité, adoption et hypothèses économiques. Mobilise les spécialistes utiles si la délégation est disponible et autorisée. Livre une synthèse de décision avec sources datées, inconnues et prochain test proportionné.
```

**Préparer le marketing :**

```text
Orka, utilise le dossier actuel pour préparer le positionnement, les messages et un plan de lancement. Vérifie les promesses par rapport au produit réellement disponible et livre les contenus à relire.
```

**Développer une fonction déjà définie :**

```text
Orka, réalise la fonction que nous avons définie dans le dépôt désigné. Reprends les critères d'acceptation, coordonne les travaux utiles, vérifie le résultat et mets à jour la documentation concernée. Demande le dépôt ou les critères s'ils ne sont pas accessibles.
```

**Reprendre un projet :**

```text
Orka, reprends le dossier actuel. Relis l'état, la synthèse et les décisions, vérifie ce qui reste valide et poursuis le travail autorisé. Signale les informations manquantes et propose la prochaine décision utile.
```

## 3. Lire le résultat et utiliser le prochain prompt

Si une entrée décisive manque, Orka demande la source ou l'extrait utile, puis garde sa provenance, sa version et son effet sur le résultat. La limite par défaut est de trois demandes de contexte par tâche, conservées à la reprise, sauf autre limite explicite dans le mandat. Sans accès ou preuve suffisante, le résultat reste partiel et ses inconnues sont visibles. Des entrées complètes n'appellent pas de question supplémentaire. Le [protocole de contexte progressif](references/prompting-agents.md#compléter-le-contexte-par-passes-bornées) et son [exemple de suivi compact](references/modeles.md#suivi-des-compléments-de-contexte) fonctionnent dans les documents ordinaires, sans Python.

Commencez par la synthèse : résultat, preuves, inconnues et décision attendue. Les détails doivent rester accessibles dans les fichiers liés. Pour une petite mission, un seul livrable peut suffire.

Orka termine ses réponses de mission par **« Prochain prompt à copier »**, avec une proposition adaptée à l'état réel du projet, dans votre langue. Copiez-la si cette suite vous convient, ou modifiez-la. La proposition n'exécute pas la suite et ne remplace pas votre décision. Le travail déjà demandé doit être terminé avant de vous proposer sa continuation ; en cas de blocage, le prompt aide à lever celui-ci.

Vous pouvez demander « uniquement le livrable » ou « sans prochain prompt » pour une réponse particulière. Si le projet n'a pas de suite immédiate utile, Orka propose une reprise liée à de futurs retours plutôt que d'inventer du travail.

## 4. Ajuster l'équipe et les moyens

Vous pouvez préciser : « petite équipe », « restitution courte », « examine aussi les objections » ou demander un modèle particulier. Orka adapte rôle, contexte et effort à la tâche dans les capacités de l'assistant. Les paramètres demandés et réellement appliqués restent distincts.

Les tokens et coûts ne sont connus que si des mesures sont disponibles. Le [bilan local des agents](references/bilan-agents.md) exploite un relevé fourni ; il ne collecte pas ces mesures. Sans sous-agents disponibles ou autorisés, Orka applique successivement les points de vue utiles et le signale.

Pour comparer plusieurs répétitions, la [procédure d’évaluation](references/evaluation-agents.md#préparer-et-relire-des-répétitions) conserve chaque résultat et ses critères, y compris échecs et inconnues. Elle fonctionne dans les documents ordinaires, sans Python. Un outil facultatif de préparation et de bilan existe dans le dépôt source pour sa maintenance ; il n’est pas dans le ZIP installé et ne lance aucun modèle. Préparer une campagne n’autorise pas son exécution.

## 5. Garder la maîtrise du projet

Une étude ne vaut ni preuve d'achat ni autorisation de lancement. Vous pouvez autoriser la réalisation dans votre demande ; envoi de messages, dépenses, publication ou déploiement nécessitent une instruction couvrant l'action. Les autorisations déjà données restent valables dans leur périmètre.

L'installation ajoute les fichiers du skill, dont ce guide. Elle ne lance ni agent ni service permanent. Conservez vos dossiers de mission : ils permettent la reprise ; l'installation du skill ne les sauvegarde pas automatiquement.

Pour aller plus loin, demandez à Orka le parcours utile : [expériences](references/experiences-apprentissage.md), [noms et domaines](references/noms-domaines.md) ou [ressources IA](references/ressources-agents.md). Vous n'avez pas besoin de lire toutes les références pour commencer.
