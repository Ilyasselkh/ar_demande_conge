from odoo import models, fields, api, _
from odoo.exceptions import AccessError, ValidationError


class ARDemandeConge(models.Model):
    _name = "ar.demande.conge"
    _description = "Demande Congé"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    name = fields.Char(
        string="Référence",
        default="Nouveau",
        readonly=True,
        copy=False,
        tracking=True
    )

    state = fields.Selection([
        ("expression_besoin", "Expression de besoin"),
        ("validation_solde", "Service administratif"),
        ("validation_n1", "Validation N+1"),
        ("validation_rh", "Validation RH"),
        ("validation_md", "Validation MD"),
        ("acceptee", "Acceptée"),
        ("refusee", "Refusée"),
    ], string="État", default="expression_besoin", tracking=True, required=True)

    demande_type = fields.Selection([
        ("heures_supp", "Demande des heures supplémentaires"),
        ("teletravail", "Demande de télétravail"),
        ("recuperation", "Demande d'ajout de récupération"),
        ("conge", "Demande de congé"),
    ], string="Type de demande", required=True, tracking=True)

    demandeur_id = fields.Many2one(
        "hr.employee",
        string="Demandeur",
        default=lambda self: self._default_employee(),
        readonly=True,
        tracking=True
    )

    manager_id = fields.Many2one(
        "hr.employee",
        string="Manager N+1",
        compute="_compute_manager_id",
        store=True,
        readonly=True,
        tracking=True
    )

    department_id = fields.Many2one(
        "hr.department",
        string="Département",
        compute="_compute_department_id",
        store=True,
        readonly=True,
        tracking=True
    )

    demandeur_user_id = fields.Many2one(
        "res.users",
        string="Utilisateur demandeur",
        compute="_compute_demandeur_user_id",
        store=True
    )

    fonction = fields.Char(string="Fonction", tracking=True)
    date_debut = fields.Datetime(string="Date de début", tracking=True)
    date_fin = fields.Datetime(string="Date de fin", tracking=True)
    tel_portable = fields.Char(string="Tél. portable", tracking=True)

    situation = fields.Selection([
        ("mariage", "Mariage"),
        ("naissance", "Naissance"),
        ("deces", "Décès"),
        ("autres", "Autres motifs"),
        ("deduire_annuel", "A déduire du congé annuel"),
    ], string="Motifs", tracking=True)

    autre_motif = fields.Text(string="Autre motif", tracking=True)

    commentaire = fields.Text(
        string="Commentaire général",
        required=True,
        tracking=True
    )

    piece_jointe = fields.Binary(string="Pièce jointe", attachment=True, tracking=True)
    piece_jointe_filename = fields.Char(string="Nom du fichier")

    heures_supp_line_ids = fields.One2many(
        "ar.demande.conge.hs.line",
        "demande_id",
        string="Lignes heures supplémentaires",
        tracking=True
    )

    can_validate_solde = fields.Boolean(compute="_compute_access_flags")
    can_validate_n1 = fields.Boolean(compute="_compute_access_flags")
    can_validate_rh = fields.Boolean(compute="_compute_access_flags")
    can_validate_md = fields.Boolean(compute="_compute_access_flags")
    can_refuse = fields.Boolean(compute="_compute_access_flags")
    can_modify = fields.Boolean(compute="_compute_access_flags")

    is_rh_user = fields.Boolean(
        string="Utilisateur RH",
        compute="_compute_access_flags"
    )

    date_validation_n1 = fields.Datetime(
        string="Date validation N+1",
        readonly=True,
        tracking=True
    )

    date_validation_solde = fields.Datetime(
        string="Date validation du solde",
        readonly=True,
        tracking=True
    )

    date_validation_rh = fields.Datetime(
        string="Date validation RH",
        readonly=True,
        tracking=True
    )

    date_validation_md = fields.Datetime(
        string="Date validation MD",
        readonly=True,
        tracking=True
    )

    date_acceptation = fields.Datetime(
        string="Date d'acceptation",
        readonly=True,
        tracking=True
    )

    date_refus = fields.Datetime(
        string="Date de refus",
        readonly=True,
        tracking=True
    )

    validateur_rh_id = fields.Many2one(
        "res.users",
        string="Validateur RH",
        readonly=True,
        tracking=True
    )

    validateur_md_id = fields.Many2one(
        "res.users",
        string="Validateur MD",
        readonly=True,
        tracking=True
    )

    date_creation = fields.Datetime(
        string="Date de création",
        default=fields.Datetime.now,
        readonly=True,
        tracking=True
    )

    md_requis = fields.Boolean(
        string="Validation MD requise",
        default=False,
        readonly=True,
        tracking=True
    )

    can_edit_hs_lines = fields.Boolean(
        string="Peut modifier lignes HS",
        compute="_compute_can_edit_hs_lines"
    )

    compteur_conge = fields.Char(
        string="Compteur de congé",
        tracking=True
    )

    motif_refus = fields.Text(
        string="Motif de refus",
        tracking=True
    )

    @api.depends("state", "demandeur_user_id")
    def _compute_can_edit_hs_lines(self):
        for rec in self:
            rec.can_edit_hs_lines = bool(
                rec.state == "expression_besoin"
                and rec.demandeur_user_id
                and rec.demandeur_user_id == self.env.user
            )

    @api.constrains("situation", "autre_motif")
    def _check_autre_motif(self):
        for rec in self:
            if rec.demande_type == "conge" and rec.situation == "autres" and not rec.autre_motif:
                raise ValidationError(_("Le champ 'Autre motif' est obligatoire lorsque la situation est 'Autres motifs'."))

    @api.constrains("situation", "piece_jointe", "demande_type")
    def _check_piece_jointe_obligatoire(self):
        for rec in self:
            if rec.demande_type == "conge" and rec.situation in ("mariage", "naissance", "deces") and not rec.piece_jointe:
                raise ValidationError(_("La pièce jointe est obligatoire lorsque la situation est Mariage, Naissance ou Décès."))

    @api.constrains("fonction", "commentaire", "tel_portable", "situation", "demande_type", "date_debut", "date_fin", "heures_supp_line_ids")
    def _check_champs_obligatoires_selon_demande(self):
        for rec in self:
            if not rec.fonction:
                raise ValidationError(_("Le champ 'Fonction' est obligatoire."))

            if not rec.commentaire:
                raise ValidationError(_("Le champ 'Commentaire général' est obligatoire."))

            if rec.demande_type == "heures_supp":
                if not rec.heures_supp_line_ids:
                    raise ValidationError(_("Vous devez ajouter au moins une ligne dans le tableau des heures supplémentaires."))
                continue

            if rec.demande_type in ("teletravail", "conge") and not rec.tel_portable:
                raise ValidationError(_("Le champ 'Tél. portable' est obligatoire pour une demande de télétravail ou de congé."))

            if rec.demande_type == "conge" and not rec.situation:
                raise ValidationError(_("Le champ 'Motifs' est obligatoire pour une demande de congé."))

            if rec.demande_type in ("teletravail", "recuperation", "conge"):
                if not rec.date_debut:
                    raise ValidationError(_("Le champ 'Date de début' est obligatoire."))
                if not rec.date_fin:
                    raise ValidationError(_("Le champ 'Date de fin' est obligatoire."))

    @api.onchange("situation")
    def _onchange_situation(self):
        for rec in self:
            if rec.situation != "autres":
                rec.autre_motif = False

    @api.onchange("demande_type")
    def _onchange_demande_type(self):
        for rec in self:
            if rec.demande_type == "heures_supp":
                rec.tel_portable = False
                rec.situation = False
                rec.autre_motif = False
                rec.piece_jointe = False
                rec.piece_jointe_filename = False
                rec.date_debut = False
                rec.date_fin = False

    def _clean_header(self, value):
        if not value:
            return False
        return str(value).replace("\n", "").replace("\r", "").strip()

    def _get_user_email(self, user):
        if not user:
            return False
        user = user.sudo()
        email = user.partner_id.email or user.email
        return self._clean_header(email) if email else False

    def _get_employee_email(self, employee):
        if not employee:
            return False

        employee = employee.sudo()

        email = False
        if employee.user_id:
            email = employee.user_id.partner_id.email or employee.user_id.email

        if not email:
            email = employee.work_email

        return self._clean_header(email) if email else False

    def _send_template(self, xmlid, email_to_list):
        self.ensure_one()
        template = self.env.ref(xmlid, raise_if_not_found=False)
        if not template:
            return

        recipients = [self._clean_header(e) for e in (email_to_list or [])]
        recipients = [e for e in recipients if e]
        if not recipients:
            return

        reply_to = (
            self.env.user.partner_id.email
            or self.env.user.email
            or ""
        )

        email_values = {
            "email_to": self._clean_header(",".join(recipients)),
            "reply_to": self._clean_header(reply_to),
        }

        template.send_mail(self.id, force_send=True, email_values=email_values)

    def _send_to_manager_n1(self, template_xmlid):
        self.ensure_one()
        email = self._get_employee_email(self.manager_id)
        if email:
            self._send_template(template_xmlid, [email])

    def _send_to_rh(self, template_xmlid):
        self.ensure_one()

        group = self.env.ref(
            "ar_demande_conge.group_demande_conge_validateur_rh",
            raise_if_not_found=False
        )
        if not group:
            return

        emails = []
        for user in group.sudo().user_ids:
            email = self._get_user_email(user)
            if email:
                emails.append(email)

        if emails:
            self._send_template(template_xmlid, emails)

    def _send_to_md(self, template_xmlid):
        self.ensure_one()

        group = self.env.ref(
            "ar_demande_conge.group_demande_conge_validateur_md",
            raise_if_not_found=False
        )
        if not group:
            return

        emails = []
        for user in group.sudo().user_ids:
            email = self._get_user_email(user)
            if email:
                emails.append(email)

        if emails:
            self._send_template(template_xmlid, emails)

    def _send_to_demandeur_and_manager_n1(self, template_xmlid_demandeur, template_xmlid_manager):
        self.ensure_one()

        demandeur_email = self._get_employee_email(self.demandeur_id)
        if demandeur_email:
            self._send_template(template_xmlid_demandeur, [demandeur_email])

        manager_email = self._get_employee_email(self.manager_id)
        if manager_email:
            self._send_template(template_xmlid_manager, [manager_email])

    def _send_to_demandeur(self, template_xmlid):
        self.ensure_one()
        email = self._get_employee_email(self.demandeur_id)
        if email:
            self._send_template(template_xmlid, [email])

    def _send_notification_for_current_state(self):
        self.ensure_one()

        if self.state == "validation_solde":
            self._send_to_rh(
                "ar_demande_conge.mail_template_demande_conge_to_solde"
            )

        elif self.state == "validation_n1":
            self._send_to_manager_n1(
                "ar_demande_conge.mail_template_demande_conge_to_n1"
            )

        elif self.state == "validation_rh":
            self._send_to_rh(
                "ar_demande_conge.mail_template_demande_conge_to_rh"
            )

        elif self.state == "validation_md":
            self._send_to_md(
                "ar_demande_conge.mail_template_demande_conge_to_md"
            )

        elif self.state == "acceptee":
            self._send_to_demandeur_and_manager_n1(
                "ar_demande_conge.mail_template_demande_conge_accepted_to_demandeur",
                "ar_demande_conge.mail_template_demande_conge_accepted_to_manager_n1"
            )

        elif self.state == "refusee":
            self._send_to_demandeur_and_manager_n1(
                "ar_demande_conge.mail_template_demande_conge_refused_to_demandeur",
                "ar_demande_conge.mail_template_demande_conge_refused_to_manager_n1"
            )

    @api.model
    def _default_employee(self):
        return self.env["hr.employee"].search([("user_id", "=", self.env.user.id)], limit=1)

    @api.depends("demandeur_id")
    def _compute_demandeur_user_id(self):
        for rec in self:
            rec.demandeur_user_id = rec.demandeur_id.user_id.id if rec.demandeur_id and rec.demandeur_id.user_id else False

    @api.depends("demandeur_id")
    def _compute_manager_id(self):
        for rec in self:
            rec.manager_id = rec.demandeur_id.parent_id.id if rec.demandeur_id else False

    @api.depends("demandeur_id")
    def _compute_department_id(self):
        for rec in self:
            rec.department_id = rec.demandeur_id.department_id.id if rec.demandeur_id else False

    @api.depends("state", "demandeur_user_id", "manager_id", "manager_id.user_id")
    def _compute_access_flags(self):
        for rec in self:
            user = self.env.user

            is_real_manager_n1 = bool(
                rec.manager_id
                and rec.manager_id.user_id
                and rec.manager_id.user_id == user
            )

            rec.can_validate_n1 = (
                user.has_group("ar_demande_conge.group_demande_conge_validateur_n1")
                and is_real_manager_n1
            )

            rec.can_validate_solde = user.has_group("ar_demande_conge.group_demande_conge_validateur_rh")
            rec.can_validate_rh = user.has_group("ar_demande_conge.group_demande_conge_validateur_rh")
            rec.can_validate_md = user.has_group("ar_demande_conge.group_demande_conge_validateur_md")
            rec.is_rh_user = user.has_group("ar_demande_conge.group_demande_conge_validateur_rh")

            if rec.state == "validation_solde":
                rec.can_refuse = rec.can_validate_solde
            elif rec.state == "validation_n1":
                rec.can_refuse = rec.can_validate_n1
            elif rec.state == "validation_rh":
                rec.can_refuse = rec.can_validate_rh
            elif rec.state == "validation_md":
                rec.can_refuse = rec.can_validate_md
            else:
                rec.can_refuse = False

            rec.can_modify = (
                user == rec.demandeur_user_id
                or rec.can_validate_solde
                or rec.can_validate_n1
                or rec.can_validate_rh
                or rec.can_validate_md
            )

    @api.constrains("date_debut", "date_fin", "demande_type")
    def _check_dates(self):
        for rec in self:
            if rec.demande_type == "heures_supp":
                continue

            if rec.date_debut and rec.date_fin and rec.date_fin < rec.date_debut:
                raise ValidationError(_("La date de fin doit être supérieure ou égale à la date de début."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            demande_type = vals.get("demande_type") or self.env.context.get("default_demande_type")

            if vals.get("name", "Nouveau") == "Nouveau":
                sequence_number = self.env["ir.sequence"].next_by_code("ar.demande.conge") or "0000"
                prefix = self._get_demande_prefix(demande_type)
                vals["name"] = f"{prefix}{sequence_number}"

            if demande_type and not vals.get("demande_type"):
                vals["demande_type"] = demande_type

        records = super().create(vals_list)

        for rec in records:
            if not rec.fonction and rec.demandeur_id and rec.demandeur_id.job_id:
                rec.fonction = rec.demandeur_id.job_id.name or ""

        return records

    def write(self, vals):
        if "compteur_conge" in vals:
            if not self.env.user.has_group("ar_demande_conge.group_demande_conge_validateur_rh"):
                raise AccessError(_("Seuls les utilisateurs RH peuvent modifier le champ 'Compteur de congé'."))
        return super().write(vals)

    def _is_demandeur_n1(self):
        self.ensure_one()
        return bool(
            self.demandeur_id
            and self.manager_id
            and self.demandeur_id.user_id
            and self.manager_id.user_id
            and self.demandeur_id.user_id == self.manager_id.user_id
        )

    def _is_demandeur_rh(self):
        self.ensure_one()
        return bool(
            self.demandeur_id
            and self.demandeur_id.user_id
            and self.demandeur_id.user_id.has_group("ar_demande_conge.group_demande_conge_validateur_rh")
        )

    def _is_demandeur_md(self):
        self.ensure_one()
        return bool(
            self.demandeur_id
            and self.demandeur_id.user_id
            and self.demandeur_id.user_id.has_group("ar_demande_conge.group_demande_conge_validateur_md")
        )

    def _get_demande_prefix(self, demande_type):
        prefixes = {
            "heures_supp": "RH-HS-",
            "teletravail": "RH-TT-",
            "recuperation": "RH-REC-",
            "conge": "RH-CG-",
        }
        return prefixes.get(demande_type, "DMD-")

    def action_soumettre(self):
        for rec in self:
            if rec.state != "expression_besoin":
                continue

            now = fields.Datetime.now()

            if rec.demande_type == "conge":
                if rec._is_demandeur_rh():
                    rec.date_validation_solde = now
                    rec.validateur_rh_id = rec.demandeur_id.user_id.id if rec.demandeur_id.user_id else False

                    if rec._is_demandeur_n1():
                        rec.date_validation_n1 = now
                        rec.state = "acceptee"
                        rec.date_acceptation = now
                    else:
                        rec.state = "validation_n1"
                else:
                    rec.state = "validation_solde"
            else:
                if rec._is_demandeur_n1():
                    rec.date_validation_n1 = now

                    if rec._is_demandeur_rh():
                        rec.date_validation_rh = now
                        rec.validateur_rh_id = rec.demandeur_id.user_id.id if rec.demandeur_id.user_id else False
                        rec.state = "acceptee"
                        rec.date_acceptation = now
                    else:
                        rec.state = "validation_rh"
                else:
                    rec.state = "validation_n1"

            rec._send_notification_for_current_state()

    def _is_current_user_real_manager_n1(self):
        self.ensure_one()
        return bool(
            self.manager_id
            and self.manager_id.user_id
            and self.manager_id.user_id == self.env.user
        )

    def action_valider_solde(self):
        for rec in self:
            if rec.state != "validation_solde":
                continue

            if not self.env.user.has_group("ar_demande_conge.group_demande_conge_validateur_rh"):
                raise AccessError(_("Vous n'avez pas le droit de valider le solde."))

            if rec.demande_type == "conge" and not rec.compteur_conge:
                raise ValidationError(_("Veuillez renseigner le champ 'Compteur de congé' avant de valider."))

            rec.date_validation_solde = fields.Datetime.now()
            rec.validateur_rh_id = self.env.user.id

            if rec._is_demandeur_n1():
                rec.date_validation_n1 = fields.Datetime.now()
                rec.state = "acceptee"
                rec.date_acceptation = fields.Datetime.now()
            else:
                rec.state = "validation_n1"

            rec._send_notification_for_current_state()

    def action_valider_n1(self):
        for rec in self:
            if rec.state != "validation_n1":
                continue

            if not self.env.user.has_group("ar_demande_conge.group_demande_conge_validateur_n1"):
                raise AccessError(_("Vous n'avez pas le droit de valider au niveau N+1."))

            if not rec._is_current_user_real_manager_n1():
                raise AccessError(_("Vous n'êtes pas le manager N+1 réel de ce demandeur."))

            rec.date_validation_n1 = fields.Datetime.now()

            if rec.demande_type == "conge":
                rec.state = "acceptee"
                rec.date_acceptation = fields.Datetime.now()
            else:
                if rec._is_demandeur_rh():
                    rec.date_validation_rh = fields.Datetime.now()
                    rec.validateur_rh_id = rec.demandeur_id.user_id.id if rec.demandeur_id.user_id else False

                    if rec.md_requis:
                        rec.state = "validation_md"
                    else:
                        rec.state = "acceptee"
                        rec.date_acceptation = fields.Datetime.now()
                else:
                    rec.state = "validation_rh"

            rec._send_notification_for_current_state()

    def action_valider_rh(self):
        for rec in self:
            if rec.state != "validation_rh":
                continue

            if not self.env.user.has_group("ar_demande_conge.group_demande_conge_validateur_rh"):
                raise AccessError(_("Vous n'avez pas le droit de valider au niveau RH."))

            rec.date_validation_rh = fields.Datetime.now()
            rec.validateur_rh_id = self.env.user.id

            rec.md_requis = False
            rec.state = "acceptee"
            rec.date_acceptation = fields.Datetime.now()

            rec._send_notification_for_current_state()

    def action_valider_md(self):
        for rec in self:
            if rec.state != "validation_md":
                continue

            if not self.env.user.has_group("ar_demande_conge.group_demande_conge_validateur_md"):
                raise AccessError(_("Vous n'avez pas le droit de valider au niveau MD."))

            rec.date_validation_md = fields.Datetime.now()
            rec.validateur_md_id = self.env.user.id
            rec.state = "acceptee"
            rec.date_acceptation = fields.Datetime.now()

            rec._send_notification_for_current_state()

    def action_envoyer_a_md(self):
        for rec in self:
            if rec.state != "validation_rh":
                continue

            if not self.env.user.has_group("ar_demande_conge.group_demande_conge_validateur_rh"):
                raise AccessError(_("Vous n'avez pas le droit d'envoyer cette demande au niveau MD."))

            if rec.demande_type == "conge":
                raise ValidationError(_("L'envoi à MD n'est pas autorisé à l'étape RH pour une demande de congé."))

            rec.date_validation_rh = fields.Datetime.now()
            rec.validateur_rh_id = self.env.user.id
            rec.md_requis = True
            rec.state = "validation_md"

            rec._send_notification_for_current_state()

    def action_refuser(self):
        for rec in self:
            if not rec.motif_refus:
                raise ValidationError(_("Le champ 'Motif de refus' est obligatoire avant de refuser la demande."))

            if rec.state == "validation_solde":
                if not self.env.user.has_group("ar_demande_conge.group_demande_conge_validateur_rh"):
                    raise AccessError(_("Vous n'avez pas le droit de refuser cette demande au niveau Validation du solde."))

                if rec.demande_type == "conge" and not rec.compteur_conge:
                    raise ValidationError(_("Veuillez renseigner le champ 'Compteur de congé' avant de refuser."))

            elif rec.state == "validation_n1":
                if not self.env.user.has_group("ar_demande_conge.group_demande_conge_validateur_n1"):
                    raise AccessError(_("Vous n'avez pas le droit de refuser cette demande au niveau N+1."))

                if not rec._is_current_user_real_manager_n1():
                    raise AccessError(_("Vous n'êtes pas le manager N+1 réel de ce demandeur."))

            elif rec.state == "validation_rh":
                if not self.env.user.has_group("ar_demande_conge.group_demande_conge_validateur_rh"):
                    raise AccessError(_("Vous n'avez pas le droit de refuser cette demande au niveau RH."))

            elif rec.state == "validation_md":
                if not self.env.user.has_group("ar_demande_conge.group_demande_conge_validateur_md"):
                    raise AccessError(_("Vous n'avez pas le droit de refuser cette demande au niveau MD."))

            else:
                raise ValidationError(_("Le refus n'est possible qu'aux étapes de validation."))

            rec.state = "refusee"
            rec.date_refus = fields.Datetime.now()

            rec._send_notification_for_current_state()

    def action_demander_modification(self):
        for rec in self:
            allowed = (
                self.env.user == rec.demandeur_user_id
                or (
                    self.env.user.has_group("ar_demande_conge.group_demande_conge_validateur_n1")
                    and rec._is_current_user_real_manager_n1()
                )
                or self.env.user.has_group("ar_demande_conge.group_demande_conge_validateur_rh")
                or self.env.user.has_group("ar_demande_conge.group_demande_conge_validateur_md")
            )
            if not allowed:
                raise AccessError(_("Vous n'avez pas le droit de modifier cette demande."))

            rec.state = "expression_besoin"
            rec.date_validation_solde = False
            rec.date_validation_n1 = False
            rec.date_validation_rh = False
            rec.date_validation_md = False
            rec.validateur_rh_id = False
            rec.validateur_md_id = False
            rec.date_acceptation = False
            rec.date_refus = False
            rec.md_requis = False
            rec.compteur_conge = False
            rec.motif_refus = False

            rec.message_post(
                body=_("La demande a été remise à l'état Expression de besoin. Le workflow a été relancé depuis le début.")
            )
            rec._send_to_demandeur(
                "ar_demande_conge.mail_template_demande_conge_back_to_demandeur_for_modification"
            )

    def _open_action_wizard(self, action_type):
        self.ensure_one()
        return {
            "name": _("Confirmation"),
            "type": "ir.actions.act_window",
            "res_model": "ar.demande.conge.action.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_demande_id": self.id,
                "default_action_type": action_type,
            }
        }

    def action_open_modify_wizard(self):
        self.ensure_one()
        return self._open_action_wizard("modify")

    def action_open_validate_n1_wizard(self):
        self.ensure_one()
        return self._open_action_wizard("validate_n1")

    def action_open_validate_rh_wizard(self):
        self.ensure_one()
        return self._open_action_wizard("validate_rh")

    def action_open_send_md_wizard(self):
        self.ensure_one()
        return self._open_action_wizard("send_md")

    def action_open_validate_md_wizard(self):
        self.ensure_one()
        return self._open_action_wizard("validate_md")

    def action_open_refuse_wizard(self):
        self.ensure_one()
        if not self.can_refuse:
            raise AccessError(_("Vous n'avez pas le droit de refuser cette demande."))
        return self._open_action_wizard("refuse")

    def action_open_validate_solde_wizard(self):
        self.ensure_one()
        return self._open_action_wizard("validate_solde")


class ARDemandeCongeHSLine(models.Model):
    _name = "ar.demande.conge.hs.line"
    _description = "Ligne Heures Supplémentaires"
    _order = "id asc"

    demande_id = fields.Many2one(
        "ar.demande.conge",
        string="Demande",
        required=True,
        ondelete="cascade"
    )

    matricule = fields.Char(
        string="Matricule",
        required=True,
        tracking=True
    )

    employee_id = fields.Many2one(
        "hr.employee",
        string="Nom & Prénom",
        required=True,
        tracking=True
    )

    date_debut = fields.Datetime(
        string="Date début",
        required=True,
        tracking=True
    )

    date_fin = fields.Datetime(
        string="Date fin",
        required=True,
        tracking=True
    )

    commentaire = fields.Text(
        string="Commentaire",
        tracking=True
    )

    @api.constrains("date_debut", "date_fin")
    def _check_dates_line(self):
        for rec in self:
            if rec.date_debut and rec.date_fin and rec.date_fin <= rec.date_debut:
                raise ValidationError(_("Dans les lignes d'heures supplémentaires, la date de fin doit être strictement supérieure à la date de début."))

    def _check_demandeur_access(self):
        for rec in self:
            if not rec.demande_id:
                continue
            if rec.demande_id.state != "expression_besoin":
                raise AccessError(_("Vous ne pouvez modifier les lignes que lorsque la demande est à l'état Expression de besoin."))
            if rec.demande_id.demandeur_user_id != self.env.user:
                raise AccessError(_("Seul le demandeur peut ajouter, modifier ou supprimer les lignes des heures supplémentaires."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            demande = self.env["ar.demande.conge"].browse(vals.get("demande_id"))
            if demande:
                if demande.state != "expression_besoin":
                    raise AccessError(_("Vous ne pouvez ajouter des lignes que lorsque la demande est à l'état Expression de besoin."))
                if demande.demandeur_user_id != self.env.user:
                    raise AccessError(_("Seul le demandeur peut ajouter une ligne d'heures supplémentaires."))
        return super().create(vals_list)

    def write(self, vals):
        self._check_demandeur_access()
        return super().write(vals)

    def unlink(self):
        self._check_demandeur_access()
        return super().unlink()
