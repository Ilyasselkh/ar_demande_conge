from odoo import _, fields, models
from odoo.exceptions import ValidationError


class ARDemandeCongeActionWizard(models.TransientModel):
    _name = "ar.demande.conge.action.wizard"
    _description = "Confirmation action demande conge"

    demande_id = fields.Many2one(
        "ar.demande.conge",
        string="Demande",
        required=True,
        readonly=True,
    )
    action_type = fields.Selection(
        [
            ("modify", "Modifier"),
            ("validate_solde", "Valider le solde"),
            ("validate_n1", "Valider N+1"),
            ("validate_rh", "Valider RH"),
            ("send_md", "Envoyer a MD"),
            ("validate_md", "Valider MD"),
            ("refuse", "Refuser"),
        ],
        string="Action",
        required=True,
        readonly=True,
    )

    def action_confirm(self):
        self.ensure_one()
        if not self.demande_id:
            raise ValidationError(_("Aucune demande selectionnee."))

        if self.action_type == "modify":
            self.demande_id.action_demander_modification()
        elif self.action_type == "validate_solde":
            self.demande_id.action_valider_solde()
        elif self.action_type == "validate_n1":
            self.demande_id.action_valider_n1()
        elif self.action_type == "validate_rh":
            self.demande_id.action_valider_rh()
        elif self.action_type == "send_md":
            self.demande_id.action_envoyer_a_md()
        elif self.action_type == "validate_md":
            self.demande_id.action_valider_md()
        elif self.action_type == "refuse":
            self.demande_id.action_refuser()
        else:
            raise ValidationError(_("Action inconnue."))

        return {"type": "ir.actions.act_window_close"}
