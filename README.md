# AR - Demande Congé

Module Odoo de gestion des demandes RH : congé, télétravail, récupération et heures supplémentaires.

## Objectif

Ce module structure les demandes RH avec une chaîne de validation incluant le service administratif, le manager N+1, les RH et la direction selon le type de demande.

## Dépendances

- `base`
- `mail`
- `hr`

## Modèles principaux

- `ar.demande.conge` : demande RH.
- `ar.demande.conge.hs.line` : lignes d'heures supplémentaires.
- `ar.demande.conge.documentation` : documentation métier.
- `ar.demande.conge.action.wizard` : assistant de confirmation.

## Types de demande

- Heures supplémentaires.
- Télétravail.
- Ajout de récupération.
- Congé.

## Workflow

1. `expression_besoin` : création de la demande.
2. `validation_solde` : contrôle administratif/solde.
3. `validation_n1` : validation manager.
4. `validation_rh` : validation RH.
5. `validation_md` : validation direction.
6. `acceptee` : demande acceptée.
7. `refusee` : demande refusée.

## Fonctionnement

- La référence est générée automatiquement.
- Les informations demandeur, manager et département proviennent de l'employé lié à l'utilisateur.
- Les champs visibles et les boutons varient selon le type de demande et l'état.
- Les validations enregistrent les validateurs, dates, commentaires et motifs.
- Le chatter trace le cycle complet.

## Rapports et notifications

Le module charge une séquence, des templates e-mail et un rapport de demande de congé.

## Sécurité

Les groupes, règles et droits sont définis dans :

- `security/security.xml`
- `security/record_rules.xml`
- `security/ir.model.access.csv`

