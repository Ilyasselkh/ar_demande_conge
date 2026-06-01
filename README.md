# AR - Demande Cong?


> Documentation des demandes RH : cong?, t?l?travail, r?cup?ration et heures suppl?mentaires.


## Vue d?ensemble

Le module structure plusieurs types de demandes RH dans un seul workflow. Il prend en compte le demandeur, le manager, le d?partement, les dates, les justificatifs, les heures suppl?mentaires et les validations administratives/RH/direction.

## Utilisateurs concern?s

- Collaborateur : cr?e la demande RH.
- Service administratif : contr?le solde ou informations administratives.
- Manager N+1 : valide le besoin.
- RH : valide le volet RH.
- MD : valide les demandes n?cessitant la direction.
- Administrateur : configure acc?s et mod?les.

## Workflow m?tier

1. Expression de besoin
2. Service administratif
3. Validation N+1
4. Validation RH
5. Validation MD si n?cessaire
6. Accept?e
7. Refus?e

## Fonctionnement op?rationnel

- Choisir le type de demande.
- Renseigner dates, motif, commentaire et pi?ce jointe si n?cessaire.
- Ajouter les lignes d?heures suppl?mentaires le cas ?ch?ant.
- Soumettre au workflow.
- Chaque validateur traite son ?tape.
- Consulter l?historique dans le chatter.

## Configuration recommand?e

- V?rifier les employ?s, managers et d?partements.
- Configurer les groupes RH/MD et record rules.
- V?rifier la s?quence, templates e-mail et rapport.
- Adapter les r?gles selon le type de demande.

## D?pendances Odoo

- `base`
- `mail`
- `hr`

## Mod?les techniques

- `ar.demande.conge` : Demande Congé (`models/ar_demande_conge.py`)
- `ar.demande.conge.hs.line` : Ligne Heures Supplémentaires (`models/ar_demande_conge.py`)
- `ar.demande.conge.documentation` : Demande Congé - Documentation (`models/ar_demande_conge_documentation.py`)
- `ar.demande.conge.action.wizard` : Confirmation action demande conge (`wizard/ar_demande_conge_modify_wizard.py`)

## ?tats d?tect?s dans le code

- `models/ar_demande_conge.py` : `expression_besoin` (Expression de besoin), `validation_solde` (Service administratif), `validation_n1` (Validation N+1), `validation_rh` (Validation RH), `validation_md` (Validation MD), `acceptee` (Acceptée), `refusee` (Refusée)

## Actions serveur principales

- `action_soumettre` (`models/ar_demande_conge.py`)
- `action_valider_solde` (`models/ar_demande_conge.py`)
- `action_valider_n1` (`models/ar_demande_conge.py`)
- `action_valider_rh` (`models/ar_demande_conge.py`)
- `action_valider_md` (`models/ar_demande_conge.py`)
- `action_envoyer_a_md` (`models/ar_demande_conge.py`)
- `action_refuser` (`models/ar_demande_conge.py`)
- `action_demander_modification` (`models/ar_demande_conge.py`)
- `action_open_modify_wizard` (`models/ar_demande_conge.py`)
- `action_open_validate_n1_wizard` (`models/ar_demande_conge.py`)
- `action_open_validate_rh_wizard` (`models/ar_demande_conge.py`)
- `action_open_send_md_wizard` (`models/ar_demande_conge.py`)
- `action_open_validate_md_wizard` (`models/ar_demande_conge.py`)
- `action_open_refuse_wizard` (`models/ar_demande_conge.py`)
- `action_open_validate_solde_wizard` (`models/ar_demande_conge.py`)
- `action_confirm` (`wizard/ar_demande_conge_modify_wizard.py`)

## Fichiers charg?s par le manifest

- `data/sequence.xml`
- `data/mail_templates.xml`
- `data/demande_conge_report.xml`
- `security/security.xml`
- `security/record_rules.xml`
- `security/ir.model.access.csv`
- `views/ar_demande_conge_views.xml`
- `views/ar_demande_conge_menu.xml`
- `views/ar_demande_conge_documentation_views.xml`

## S?curit? et droits

Le module s?appuie sur les fichiers suivants pour d?finir les groupes, r?gles d?enregistrement et droits d?acc?s :

- `security/ir.model.access.csv`
- `security/record_rules.xml`
- `security/security.xml`

## Assets et interface

- `static/src/js/demande_conge_animations.js`
- `static/src/scss/ar_demande_conge.scss`

## Bonnes pratiques d?utilisation

- V?rifier que chaque utilisateur Odoo est li? au bon employ? lorsque le module d?pend de `hr.employee`.
- Tester le workflow avec un dossier de test avant utilisation en production.
- Contr?ler les groupes de s?curit? apr?s installation afin que seuls les bons r?les voient les boutons de validation.
- Garder les templates e-mail et rapports align?s avec les proc?dures internes.
- Sauvegarder la base avant toute modification structurelle du module.

## Maintenance

- Les ?volutions fonctionnelles doivent ?tre ajout?es dans les mod?les Python, les vues XML et les r?gles de s?curit? correspondantes.
- Apr?s modification des vues, mettre ? jour le module depuis Odoo ou red?marrer le serveur selon le type de changement.
- Apr?s modification des assets, vider le cache navigateur et recompiler les assets si n?cessaire.
- Toute nouvelle ?tape de workflow doit ?tre accompagn?e des droits, boutons, notifications et filtres correspondants.
