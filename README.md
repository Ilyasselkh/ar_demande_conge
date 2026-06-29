# AR - Demande Conge

Module Odoo de gestion des demandes RH : conge, teletravail, recuperation et heures supplementaires.

Le module centralise les demandes collaborateur, controle les champs obligatoires, gere les validations Service administratif, Manager N+1, RH et MD, puis archive les demandes acceptees ou refusees.

## Objectif fonctionnel

Digitaliser les demandes RH courantes et assurer une validation tracable.

Le module permet de :

- creer une demande RH ;
- choisir le type de demande ;
- renseigner les dates, motifs et commentaires ;
- joindre une piece justificative ;
- saisir des lignes d'heures supplementaires ;
- valider le solde par le service administratif ;
- valider par Manager N+1 ;
- valider par RH ;
- envoyer vers MD lorsque requis ;
- accepter ou refuser avec motif ;
- notifier les acteurs par email ;
- imprimer un rapport de demande.

## Roles fonctionnels

### Demandeur

Le demandeur initie la demande.

Il peut :

- creer une demande ;
- renseigner le type, les dates et le commentaire ;
- ajouter une piece jointe ;
- saisir les lignes d'heures supplementaires ;
- soumettre la demande ;
- consulter son historique.

### Service administratif

Le service administratif intervient pour la validation du solde lorsque le flux le demande.

Il verifie les donnees avant transmission au Manager N+1.

### Manager N+1

Le Manager N+1 valide la demande du collaborateur.

Condition importante : l'utilisateur doit etre le manager reel du demandeur.

### RH

RH valide la demande apres le Manager N+1 et peut refuser si les conditions RH ne sont pas respectees.

### MD

MD valide les demandes qui necessitent une validation direction.

## Types de demande

Le champ `Type de demande` peut prendre les valeurs suivantes :

- demande des heures supplementaires ;
- demande de teletravail ;
- demande d'ajout de recuperation ;
- demande de conge.

## Etats du workflow

Les etats principaux sont :

- `Expression de besoin`
- `Service administratif`
- `Validation N+1`
- `Validation RH`
- `Validation MD`
- `Acceptee`
- `Refusee`

## Flux standard

1. `Expression de besoin`
2. `Service administratif`
3. `Validation N+1`
4. `Validation RH`
5. `Validation MD` si requis
6. `Acceptee`

Un refus est possible aux etapes de validation autorisees.

## Heures supplementaires

Pour les demandes d'heures supplementaires, le demandeur renseigne des lignes dediees.

Les lignes permettent de detailler les periodes et les informations necessaires au controle RH.

## Motifs et pieces jointes

Le module permet de renseigner :

- situation ;
- autre motif ;
- commentaire general ;
- piece jointe.

Pour les motifs `Autres`, le commentaire doit permettre au validateur de comprendre la demande.

## Notifications

Les templates email couvrent les transitions vers :

- service administratif ;
- Manager N+1 ;
- RH ;
- MD ;
- demandeur apres acceptation ;
- demandeur apres refus ;
- demandeur apres demande de modification ;
- Manager N+1 selon acceptation ou refus.

Fichier principal :

- `data/mail_templates.xml`

## Rapports

Le module fournit un rapport de demande RH.

Fichier principal :

- `data/demande_conge_report.xml`

## Modeles principaux

- `ar.demande.conge`
- `ar.demande.conge.hs.line`
- `ar.demande.conge.documentation`
- `ar.demande.conge.action.wizard`

## Structure du module

- `security/security.xml`
- `security/record_rules.xml`
- `security/ir.model.access.csv`
- `data/sequence.xml`
- `data/mail_templates.xml`
- `data/demande_conge_report.xml`
- `views/ar_demande_conge_views.xml`
- `views/ar_demande_conge_menu.xml`
- `views/ar_demande_conge_documentation_views.xml`
- `wizard/ar_demande_conge_modify_wizard.py`
- `models/ar_demande_conge.py`
- `models/ar_demande_conge_documentation.py`
- `static/src/scss/ar_demande_conge.scss`
- `static/src/js/demande_conge_animations.js`

## Installation

1. Copier le module dans le dossier addons Odoo.
2. Redemarrer le serveur Odoo si necessaire.
3. Mettre a jour la liste des applications.
4. Installer le module.
5. Verifier les groupes Service administratif, Manager, RH et MD.
6. Verifier les managers dans les fiches employes.
7. Tester chaque type de demande.

## Maintenance fonctionnelle

Lorsqu'une regle RH change, verifier aussi :

- les champs obligatoires ;
- le champ `state` ;
- les boutons du formulaire ;
- les assistants de validation/refus ;
- les templates email ;
- le rapport ;
- ce README.
