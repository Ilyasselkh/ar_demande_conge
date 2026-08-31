{
    "name": "AR - Demande Congé",
    "version": "1.0.0",
    "summary": "Gestion des demandes RH",
    "description": """
Module de gestion des demandes :
- Heures supplémentaires
- Télétravail
- Récupération
- Congé

Avec workflow :
- Expression de besoin
- Validation N+1
- Validation RH
- Validation MD
- Acceptée
- Refusée
    """,
    "author": "AR IT Department",
    "website": "",
    "category": "Human Resources",
    "license": "LGPL-3",
    "depends": [
        "base",
        "web",
        "mail",
        "hr",
    ],
    "data": [
        "data/sequence.xml",
        "data/mail_templates.xml",
        "data/demande_conge_report.xml",
        "security/security.xml",
        "security/record_rules.xml",
        "security/ir.model.access.csv",
        "views/ar_demande_conge_views.xml",
        "views/ar_demande_conge_menu.xml",
        "views/ar_demande_conge_documentation_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ar_demande_conge/static/src/scss/ar_demande_conge.scss",
            "ar_demande_conge/static/src/js/demande_conge_animations.js",
            "ar_demande_conge/static/src/js/demande_conge_list_filters.js",
        ],
    },
    "application": True,
    "installable": True,
}
