-- Schema historique Orka 0.3.1, conserve pour les tests de migration.

CREATE TABLE configuration (id INTEGER PRIMARY KEY CHECK(id=1), racine TEXT NOT NULL,
    capacite INTEGER NOT NULL CHECK(capacite>0), version INTEGER NOT NULL);
CREATE TABLE taches (mission TEXT NOT NULL, id TEXT NOT NULL, requete TEXT NOT NULL,
    fichier TEXT NOT NULL, acceptation TEXT NOT NULL, etat TEXT NOT NULL,
    maximum INTEGER NOT NULL, tentatives INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY(mission,id));
CREATE TABLE dependances (mission TEXT NOT NULL, tache TEXT NOT NULL, amont TEXT NOT NULL,
    PRIMARY KEY(mission,tache,amont),
    FOREIGN KEY(mission,tache) REFERENCES taches(mission,id),
    FOREIGN KEY(mission,amont) REFERENCES taches(mission,id));
CREATE TABLE tentatives (id TEXT PRIMARY KEY, mission TEXT NOT NULL, tache TEXT NOT NULL,
    numero INTEGER NOT NULL, requete TEXT NOT NULL, fichier TEXT NOT NULL,
    active INTEGER NOT NULL, phase TEXT NOT NULL, agent TEXT, appliques TEXT,
    activite REAL NOT NULL, observations TEXT, empreinte TEXT,
    UNIQUE(mission,tache,numero), FOREIGN KEY(mission,tache) REFERENCES taches(mission,id));
CREATE UNIQUE INDEX sortie_active ON tentatives(fichier) WHERE active=1;
CREATE UNIQUE INDEX tache_active ON tentatives(mission,tache) WHERE active=1;
CREATE UNIQUE INDEX agent_actif ON tentatives(agent) WHERE active=1 AND agent IS NOT NULL;
CREATE TABLE evenements (id INTEGER PRIMARY KEY, date REAL NOT NULL, mission TEXT,
    tache TEXT, tentative TEXT, type TEXT NOT NULL, details TEXT NOT NULL);
