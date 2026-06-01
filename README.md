# AR - Demande Conge

Module Odoo de gestion des demandes RH: conge, teletravail, recuperation et heures supplementaires.

## Objectif

Cette documentation explique le perimetre fonctionnel du module, les roles utilisateurs, le workflow, la configuration et les principaux objets techniques.

## Utilisateurs concernes

- Collaborateur
- Service administratif
- Manager N+1
- RH
- MD
- Administrateur Odoo

## Workflow metier

1. Expression de besoin
2. Service administratif
3. Validation N+1
4. Validation RH
5. Validation MD si necessaire
6. Acceptee
7. Refusee

## Fonctionnement operationnel

- Choisir le type de demande.
- Renseigner dates, motif et commentaire.
- Ajouter piece jointe ou lignes heures supplementaires.
- Soumettre au workflow.
- Valider chaque etape.
- Consulter historique dans le chatter.

## Configuration recommandee

- Verifier employes, managers et departements.
- Configurer groupes RH et MD.
- Verifier sequence, templates mail et rapport.
- Adapter les regles par type de demande.

## Dependances Odoo

- `base`
- `mail`
- `hr`
- `website`

## Modeles principaux

- `ar.demande.conge`
- `ar.demande.conge.hs.line`
- `ar.demande.conge.documentation`
- `ar.demande.conge.action.wizard`

## Structure importante du module

- `security/ir.model.access.csv`
- `security/record_rules.xml`
- `security/security.xml`
- `data/demande_conge_report.xml`
- `data/mail_templates.xml`
- `data/sequence.xml`
- `views/ar_demande_conge_documentation_views.xml`
- `views/ar_demande_conge_menu.xml`
- `views/ar_demande_conge_views.xml`
- `wizard/__init__.py`
- `wizard/ar_demande_conge_modify_wizard.py`
- `models/__init__.py`
- `models/ar_demande_conge.py`
- `models/ar_demande_conge_documentation.py`

## Securite

Les droits sont geres par les fichiers du dossier `security`. Il faut verifier les groupes, les regles enregistrement et les acces CSV apres installation ou modification du module.

## Notifications et suivi

Les modules qui dependent de `mail` utilisent le chatter Odoo pour tracer les changements. Les templates mail presents dans le dossier `data` servent a notifier les acteurs concernes par les transitions.

## Installation

1. Copier le module dans le dossier addons Odoo.
2. Redemarrer le serveur Odoo si necessaire.
3. Mettre a jour la liste des applications.
4. Installer ou mettre a jour le module.
5. Verifier les droits utilisateurs et tester un dossier de bout en bout.

## Maintenance

- Ajouter toute nouvelle etape a la fois dans le modele Python, les vues XML, les droits et les notifications.
- Tester les workflows avec plusieurs roles utilisateurs.
- Mettre a jour les rapports et templates mail quand la procedure interne change.
- Eviter de modifier les donnees de production sans sauvegarde.
- Documenter toute evolution fonctionnelle dans ce README.
