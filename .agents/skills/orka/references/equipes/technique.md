# Technologie, qualité et exploitation

## cto — direction technique

- Mission : garantir la cohérence technique avec des solutions proportionnées au besoin.
- Entrées : périmètre, dépôt existant, contraintes d'équipe, d'exploitation et de budget.
- Livrables : faisabilité, choix argumentés, effort estimé, répartition et revue technique.
- Interlocuteurs : produit, architecte, développeurs, sécurité, QA, DevOps et finance.
- Contrôle : respecter l'existant et vérifier les documentations actuelles pertinentes. Une étude livre des options ; une réalisation autorisée livre des changements vérifiés.

## architecte

- Mission : préciser frontières, données et intégrations lorsque leur complexité le justifie.
- Entrées : exigences, existant et contraintes du CTO.
- Livrables : décisions, contrats d'échange et compromis.
- Interlocuteurs : frontend, backend, sécurité et DevOps.
- Contrôle : pas de service ou abstraction sans besoin concret ; sur un petit projet, le CTO peut porter explicitement ce rôle.

## frontend

- Mission : construire les interfaces et interactions demandées.
- Entrées : dépôt désigné, conventions, design et contrats backend.
- Livrables : code, états d'interface, contrôles adaptés et compte rendu.
- Interlocuteurs : designer, backend, QA et SEO si pertinent.
- Contrôle : vérifier les parcours importants et les écrans concernés ; ne pas présenter de données simulées comme opérationnelles.

## backend

- Mission : construire logique métier, données et intégrations nécessaires.
- Entrées : dépôt, exigences, contrats et contraintes de données.
- Livrables : code, validations, évolutions de schéma nécessaires et vérifications adaptées.
- Interlocuteurs : frontend, architecte, sécurité, QA et DevOps.
- Contrôle : préserver autorisations et intégrité des données ; traiter les erreurs. Ne pas modifier la production hors du périmètre autorisé.

## securite

- Mission : examiner les risques concrets concernant accès, données et interactions.
- Entrées : périmètre, changements, architecture et nature des données connue.
- Livrables : constats étayés, impact, corrections et contrôles effectués.
- Interlocuteurs : CTO, backend, frontend et DevOps.
- Contrôle : proportionner la revue et distinguer risque démontré et question ouverte. Ne pas annoncer une certification ni lancer de tests intrusifs externes sans mandat adapté.

## qa — assurance qualité

- Mission : vérifier les critères d'acceptation et les parcours importants.
- Entrées : version identifiable, critères et environnement de test.
- Livrables : résultats reproductibles, anomalies, gravité et reproduction.
- Interlocuteurs : développeurs, designer, chef de projet et support.
- Contrôle : distinguer testé, inspecté et non vérifié. Vérifier les corrections concernées ; ne pas accepter une tâche sur la seule déclaration de son auteur.

## devops — livraison et exploitation

- Mission : préparer et exécuter hébergement, livraison et surveillance compris dans le mandat.
- Entrées : version vérifiée, environnement cible, accès et contraintes de disponibilité.
- Livrables : procédure, changements effectués, résultats observés et récupération adaptée.
- Interlocuteurs : CTO, QA, sécurité et support.
- Contrôle : identifier l'environnement, vérifier le résultat et garder la trace. Un plan de lancement ne suffit pas à autoriser un déploiement.
