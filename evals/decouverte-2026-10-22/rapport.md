# Découverte d’Orka depuis le README

Propriétaire : coordinateur de maintenance. Version : 1. Date : 22 octobre 2026. Référence documentaire : commit `8104bac`, skill distribué 0.4.1. Un testeur IA en contexte neuf, sans la conversation principale ni les critiques antérieures. Aucune correction du README, des guides ou du skill pendant cet essai.

**Aucun blocage observé sur le parcours essayé : README anglais → guide d’installation → guide de démarrage français → téléchargement et extraction du ZIP → préparation d’une première mission.** La détection du skill par une nouvelle session et l’exécution d’une mission n’ont pas été testées. Ce résultat ne valide donc pas tout le démarrage dans un assistant réel.

## Ce qui a fonctionné

| Étape | Constat et preuve | État |
|---|---|---|
| Comprendre Orka depuis le README seul | Le [premier regard](sorties/premier-regard.md) distingue instructions, outils de l’hôte, sous-agents facultatifs et absence de service permanent. | Observé dans la restitution du testeur |
| Choisir une installation | Le README donne le ZIP, le dossier utilisateur Codex et `$orka`. Le testeur choisit la route manuelle. | Observé ; installation personnelle non tentée |
| Comprendre le rôle de Python | Le testeur distingue usage courant sans Python et outils locaux facultatifs. Aucun script livré n’est exécuté selon sa trace. | Compréhension observée ; pas de test dans un système dépourvu de Python |
| Trouver les compléments | Les deux guides consultés sont accessibles par les liens du README et cohérents avec la route retenue. Aucun manque bloquant n’a dû être comblé. | Navigation déclarée et fichiers recontrôlés |
| Obtenir et extraire le skill | ZIP public reçu avec HTTP 200 : 113 185 octets, 41 fichiers, une racine `orka`, version déclarée 0.4.1. | Vérification du paquet et de l’extraction réussie |
| Préparer une première demande | Le [parcours détaillé](sorties/parcours.md) contient un message concret adapté à l’exemple du README, avec résultat, destination et limites. | Message préparé ; ni envoyé ni exécuté |

Le recontrôle du coordinateur confirme que les fichiers extraits sont identiques au ZIP et que le paquet correspond exactement aux sources du skill à la référence documentaire, licence comprise. Le testeur n’avait pas effectué cette dernière comparaison ; sa restitution originale est conservée sans réécriture. Voir la [vérification](verification.json).

## Blocages et informations manquantes

**Aucun défaut bloquant ni information indispensable manquante n’a été relevé pour comprendre le produit, essayer la copie manuelle et préparer le premier message.** Les guides apportent des exemples supplémentaires et une lecture en français ; dans cet essai, ils ne résolvent pas un blocage du README.

Trois points restent non vérifiés : la découverte effective du skill dans une nouvelle session, les outils et la délégation réellement accessibles dans cette session, puis le comportement de la première mission. Ces inconnues découlent du périmètre de l’essai et des capacités de l’hôte ; elles ne sont pas classées comme défauts documentaires.

Le lien `latest` a conduit à la release 0.4.1. Pour reproduire cet essai ultérieurement, utiliser la version et l’empreinte enregistrées ; cela ne justifie pas à lui seul de modifier le lien d’accueil. La langue anglaise du README n’a pas bloqué ce testeur et ne permet pas de conclure sur l’expérience d’un lecteur non anglophone.

## Fiabilité et limites du test

Le protocole et le mandat ont été fixés avant lancement. Le premier regard devait être écrit avant ouverture des liens ; cet ordre est déclaré par le testeur. Le coordinateur l’a capturé pendant l’essai et confirme que son contenu n’a plus changé. Les fichiers de la copie publique figée sont restés intacts. Aucun retour de correction de fond n’a été adressé au testeur.

Le contexte a été lancé avec `fork_turns=none`. Les consignes générales et le catalogue de l’hôte peuvent rester visibles ; l’isolement des fichiers repose sur des consignes, sans sandbox dédiée ni audit complet des lectures. La trace ne déclare pas de recours à un skill personnel ou à une autre copie du projet. Le début du `SKILL.md` ouvert dans le ZIP provient du lien de téléchargement autorisé et a été traité comme documentation.

Un testeur IA ne remplace pas des utilisateurs humains. Une route manuelle Codex a été examinée ; Claude, Hermes, les variantes de configuration et le rendu visuel n’ont pas été éprouvés. L’extraction par les outils du test ne mesure pas la facilité d’utilisation d’un gestionnaire de fichiers humain.

Le modèle demandé était `gpt-6.1-sol`, effort `medium`. Les paramètres appliqués, tokens et coûts ne sont pas exposés. Les 149 secondes entre envoi et première observation de fin incluent latence et attente ; ce n’est pas une mesure de temps d’installation utilisateur.

## Décision avant correction

**Conserver l’accueil en l’état à l’issue de cet essai.** Aucun défaut observé ne justifie une correction. Le prochain essai utile, s’il est demandé, serait la détection et le démarrage effectifs dans un hôte et une configuration explicitement choisis, en conservant cette première observation.

Les [copies publiques des traces](README.md) masquent les paramètres temporaires signés des redirections de téléchargement et les cookies. Les originaux bruts et le ZIP sont conservés localement ; leurs empreintes et celles des copies publiées figurent dans le [manifeste](manifest.json). Cette expurgation de publication ne modifie ni les constats du testeur ni les documents évalués.
