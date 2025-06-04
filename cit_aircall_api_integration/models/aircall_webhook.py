# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).           #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

import logging
import time
from datetime import datetime

import phonenumbers
import requests
from markupsafe import Markup
from odoo.http import request
import json
import urllib.parse
from odoo import api, models

_logger = logging.getLogger(__name__)

AIRCALL_API_URL = 'https://api.aircall.io/v1'


class AircallWebhook(models.TransientModel):
    _name = 'aircall.webhook'
    _description = 'Aircall Webhook'

    @api.model
    def validate_webhook_token(self, token):
        """ Method for validate the aircall webhook token. """
        true_token = self.env['ir.config_parameter'].sudo(
        ).get_param('cit_aircall_api_integration.default_aircall_integration_token')
        if true_token is False:
            _logger.warning(
                'Aircall integration token has not been set. Webhooks cannot work without it.')
        return true_token == token

    @api.model
    def get_aircall_api_config(self):
        """ Will throw an error if the config is not set """
        sudo_param = self.sudo().env['ir.config_parameter']
        return sudo_param.get_param(
            'cit_aircall_api_integration.default_api_id'), sudo_param.get_param(
            'cit_aircall_api_integration.default_api_token')

    @api.model
    def register(self, payload):
        """ Method where all webhook events are defined. """
        register_map = {
            'call.created': self._send_insight_card,
            'call.ended': self._register_call,
            # 'call.answered': self._register_call_answers,
            'call.commented': self._register_comment,
            'contact.created': self._register_contact,
        }
        try:
            method = register_map[payload['event']]
        except KeyError:
            _logger.warning(
                'An unimplemented webhook of type [{}] has been received. Uncheck it in aircall dashboard.'.format(
                    payload['event']))
            return
        method(payload)

    def create_call_detail(self, call_id, recording, waiting_time, i,
                           mail_data, data, talk_time, tags, comments):

        # Check if the call detail already exists
        existing_call_detail = self.env['aircall.details'].sudo().search_read([
            ('aircall_call_id', '=', call_id)])
        if existing_call_detail:
            # If a similar call detail already exists, do not create a duplicate
            return
        number = data['number']['digits'] if data.get('number') and data['number'].get(
            'digits') else ''

        if i and hasattr(i, 'parent_id'):
            parents = i.mapped('parent_id').filtered(lambda p: p) if i else False
            last_parent = parents[-1] if parents else i  # If no parent, fallback to `i`
        else:
            last_parent = i  # If `i` doesn't have `parent_id`, fallback to `i`

        self.env['aircall.details'].sudo().create({
            'aircall_call_id': call_id,
            'call_by_user': data['number']['name'],
            'customer_id': last_parent.id if last_parent else False,
            'recording_url': recording,
            'phonenumbers': data['raw_digits'],
            'call_qualification': data["direction"],
            'call_duration': time.strftime(
                '%H:%M:%S', time.gmtime(data['duration'])),
            'waiting_time': waiting_time,
            'call_time': talk_time,
            'air_call_number': number,
            'tags': tags,
            'notes': comments and comments[0] or ''
        })

        if tags and i:
            # Prepare a list of sanitized tags
            tag_list = [tag.strip() for tag in tags if isinstance(tag, str) and tag.strip()]
            if self.env.context.get('from_res_partner'):
                for tag in tag_list:
                    # Fetch or create the partner category
                    category = self.env['res.partner.category'].sudo().search(
                        [('name', '=', tag)],
                        limit=1)
                    if not category:
                        category = self.env['res.partner.category'].sudo().create(
                            {'name': tag})

                    # Append the category to the category_id field
                    i.sudo().write({'category_id': [(4, category.id)]})

            # Fetch configuration setting for Helpdesk tickets
            helpdesk_ticket = self.env['ir.config_parameter'].sudo().get_param(
                'cit_aircall_api_integration.helpdesk_log_note_setting'
            )

            # Check if the CRM module is installed before accessing crm.tag
            if self.env['ir.module.module'].sudo().search(
                    [('name', '=', 'crm'), ('state', '=', 'installed')]):
                # Fetch or create CRM tags and append them to the last created CRM lead
                crm_tag_ids = []
                for tag in tag_list:
                    tag_rec = self.env['crm.tag'].sudo().search([('name', '=', tag)], limit=1)
                    if not tag_rec:
                        tag_rec = self.env['crm.tag'].sudo().create({'name': tag})
                    crm_tag_ids.append(tag_rec.id)

                last_crm_lead = self.env['crm.lead'].sudo().search([],
                                                                   order='create_date desc',
                                                                   limit=1)
                if last_crm_lead:
                    for tag_id in crm_tag_ids:
                        last_crm_lead.sudo().write({'tag_ids': [(4, tag_id)]})  # Append tags
                    last_crm_lead._cr.commit()

            # Logic for Helpdesk tickets
            if helpdesk_ticket == 'open_new_ticket':
                helpdesk_tag_ids = []
                for tag in tag_list:
                    tag_rec = self.env['helpdesk.tag'].sudo().search([('name', '=', tag)],
                                                                     limit=1)
                    if not tag_rec:
                        tag_rec = self.env['helpdesk.tag'].sudo().create({'name': tag})
                    helpdesk_tag_ids.append(tag_rec.id)

                last_helpdesk_ticket = self.env['helpdesk.ticket'].sudo().search([],
                                                                                 order='create_date desc',
                                                                                 limit=1)
                if last_helpdesk_ticket:
                    for tag_id in helpdesk_tag_ids:
                        last_helpdesk_ticket.sudo().write(
                            {'tag_ids': [(4, tag_id)]})  # Append tags
                    last_helpdesk_ticket._cr.commit()

            elif helpdesk_ticket == 'add_log_note_exciting':
                tickets_with_log_note = self.env['helpdesk.ticket'].sudo().search(
                    [('x_add_log_note', '=', True)]
                )
                if tickets_with_log_note:
                    helpdesk_tag_ids = []
                    for tag in tag_list:
                        tag_rec = self.env['helpdesk.tag'].sudo().search([('name', '=', tag)],
                                                                         limit=1)
                        if not tag_rec:
                            tag_rec = self.env['helpdesk.tag'].sudo().create({'name': tag})
                        helpdesk_tag_ids.append(tag_rec.id)

                    for ticket in tickets_with_log_note:
                        for tag_id in helpdesk_tag_ids:
                            ticket.sudo().write({'tag_ids': [(4, tag_id)]})  # Append tags
                    self._cr.commit()

    @api.model
    def _register_comment(self, payload):
        """Method called when notes being noted to the call."""
        comments = []
        data = payload.get('data')
        for comment in data.get('comments'):
            comments.append('\n{}'.format(comment.get('content')))
        call_comment = "\n".join(comments)
        aircall_detail_rec = self.env['aircall.details'].sudo().search([
            ('aircall_call_id', '=', data.get('id'))], order='id desc', limit=1)
        if aircall_detail_rec:
            if call_comment and not aircall_detail_rec.notes:
                _logger.info('\n\nAircallDetailRec-Comment %s', aircall_detail_rec,
                             aircall_detail_rec.notes)
                aircall_detail_rec.sudo().write({'notes': call_comment})

    def _process_comments_tags(self, data):
        """This method gives Comments and Tags which is added During the call"""
        comments = [f"\n{comment['content']}" for comment in data['comments']]
        tags = [f"\n{tag['name']}" for tag in data['tags']]
        return comments, tags

    def _process_call_with_conf_num(self, payload, comments, tags):
        """This method allows user to add the logout which is configured in setting."""
        data = payload['data']
        partner_obj = self.env['res.partner'].sudo()
        external_entity_id = self._find_partner(partner_obj, data['raw_digits'])

        # Check if message is already logged for this call ID
        check_msg = self.env['mail.message'].sudo().search_read(
            [('aircall_call_id', '=', data['id'])], limit=1
        )

        manual_call_loging = self.env['ir.config_parameter'].sudo().get_param(
            'cit_aircall_api_integration.manual_call_loging'
        )

        if not check_msg and payload.get('event') == 'call.ended' and external_entity_id:
            talk_time, waiting_time = self._calculate_times(data)

            # Generate message **ONCE** before looping over contacts
            message = self._generate_message(data, talk_time, waiting_time, tags, comments)

            partner = external_entity_id[0] if external_entity_id else None
            if partner:
                if not manual_call_loging or partner.x_add_log_note:
                    self._post_message_and_create_call(partner, message, data, talk_time,
                                                       waiting_time, tags, comments)
                    partner.update({'x_add_log_note': False})  # Reset flag after processing

    def _process_call_without_conf_num(self, data):
        """This method calls when call is disconnected."""
        partner_obj = self.env['res.partner']
        external_entity_ids = self._find_partner(partner_obj, data['raw_digits']).filtered(
            lambda a: a.x_add_log_note)
        if external_entity_ids:
            [external_entity_id.update({'x_add_log_note': False}) for external_entity_id in
             external_entity_ids]

    @api.model
    def _register_call(self, payload):
        """ Method called when a call event is performed, handling general call processing, CRM leads, and Helpdesk tickets. """
        _logger.info(payload)
        assert payload['resource'] == 'call'

        data = payload['data']
        company = request.env.company
        number = data['number']

        # Common data processing
        conf_num = self._get_conf_num(company, number)
        comments, tags = self._process_comments_tags(data)

        if conf_num:
            self._process_call_with_conf_num(payload, comments, tags)
        else:
            self._process_call_without_conf_num(data)

        # Check if CRM module is installed
        crm_installed = self.env['ir.module.module'].sudo().search_count([
            ('name', '=', 'crm'), ('state', '=', 'installed')
        ]) > 0

        enable_helpdesk_module = self.env['ir.config_parameter'].sudo().get_param(
            'cit_aircall_api_integration.enable_helpdesk_module'
        )

        if crm_installed:
            # Handle CRM leads
            crm_lead = self.env['crm.lead'].sudo().search(
                ['|',
                 ('phone', 'ilike', data['raw_digits']),
                 '|',
                 ('phone', 'ilike', data['raw_digits'].replace(" ", "")),
                 '|',
                 ('mobile', 'ilike', data['raw_digits']),
                 ('mobile', 'ilike', data['raw_digits'].replace(" ", ""))]
            )

            # if not data.get('answered_at'):
            #     data['answered_at'] = data['ended_at']

            self._process_leads(crm_lead, data, tags, comments)
        else:
            _logger.warning("CRM module is not installed, skipping CRM lead processing.")

        # Check if Helpdesk module is installed
        helpdesk_installed = self.env['ir.module.module'].sudo().search_count([
            ('name', '=', 'helpdesk'), ('state', '=', 'installed')
        ]) > 0

        if helpdesk_installed and enable_helpdesk_module:
            # Handle Helpdesk tickets
            helpdesk = self.env['helpdesk.ticket'].sudo().search(
                [
                    '|', ('partner_phone', 'ilike', data['raw_digits']), '|',
                    ('partner_phone', 'ilike', data['raw_digits'].replace(" ", "")), '|',
                    ('x_partner_mobile', 'ilike', data['raw_digits']),
                    ('x_partner_mobile', 'ilike', data['raw_digits'].replace(" ", "")),
                    ('x_add_log_note', '=', True)
                ]
            )

            self._process_helpdesk(helpdesk, data, tags, comments)
        else:
            _logger.warning(
                "Helpdesk module is not installed, skipping Helpdesk ticket processing.")

        return True

    def _get_conf_num(self, company, number):
        """Fetches configuration numbers based on the company's number config."""
        if not company.number_config_ids:
            return []
        num_search = self.env['number.number'].sudo().search(
            [('id', 'in', company.number_config_ids.ids)]
        )
        conf_num = [num for num in num_search if
                    str(num.number_id) == str(number['id']) and str(num.digits) == str(
                        number['digits'])]
        return conf_num

    def _process_helpdesk(self, helpdesk, data, tags, comments):
        """This method calls for adding a log note in ticket for configured aircall user"""
        for rec in helpdesk:
            talk_time, waiting_time = self._calculate_times(data)
            if self._is_helpdesk_number_configured(data['number']['digits']):
                message = self._generate_message(data, talk_time, waiting_time, tags, comments)
                author_ref = self.env.ref(
                    'cit_aircall_api_integration.aircall_res_partner_1',
                    raise_if_not_found=False)
                author_id = author_ref.id if author_ref else None
                mail_data = rec.sudo().message_post(body=message,
                                                    author_id=author_id if author_id else None)
                if mail_data:
                    mail_data.aircall_call_id = data['id']
                    self.create_call_detail(
                        data['id'], data['asset'], waiting_time, rec, mail_data, data,
                        talk_time,
                        tags, comments)
        helpdesk.sudo().write({'x_add_log_note': False})

    def _is_helpdesk_number_configured(self, digits):
        """Find the configure aircall number in setting"""
        return self.env.company.number_helpdesk_config_ids.filtered(
            lambda num: num.digits == digits)

    def _find_partner(self, partner_obj, raw_digits):
        """Finds the external entity based on the phone or mobile number."""
        return partner_obj.sudo().search(
            [
                '|', ('phone', 'ilike', raw_digits), '|',
                ('phone', 'ilike', raw_digits.replace(" ", "")), '|',
                ('mobile', 'ilike', raw_digits),
                ('mobile', 'ilike', raw_digits.replace(" ", ""))], order='id desc'
        )

    def _handle_unknown_contact_creation(self, external_entity_id, partner_obj, data):
        """Handles the creation of unknown contacts if allowed."""
        create_aircall_contact = self.env['ir.config_parameter'].sudo().get_param(
            'cit_aircall_api_integration.allow_create_unknown_contacts'
        )

        if create_aircall_contact and not external_entity_id:
            aircall_contact_find = self._find_partner(partner_obj, data['raw_digits'])
            if not aircall_contact_find:
                external_entity_id = partner_obj.sudo().create({
                    'name': "NEW : " + data['raw_digits'],
                    'phone': data['raw_digits'],
                    'email': '',
                })

        for partner in external_entity_id:
            if len(external_entity_id) == 1 and not partner.x_add_log_note:
                partner.x_add_log_note = True

        return external_entity_id

    def _calculate_times(self, data):
        """Calculates the talk time and waiting time based on call data."""
        talk_time = waiting_time = 0
        if data['answered_at']:
            talk_time = time.strftime('%H:%M:%S',
                                      time.gmtime(data['ended_at'] - data['answered_at']))
            waiting_time = time.strftime('%H:%M:%S',
                                         time.gmtime(data['answered_at'] - data['started_at']))

        return talk_time, waiting_time

    def _generate_message(self, data, talk_time, waiting_time, tags, comments):
        """Generates the message to be logged or sent."""
        started_at = datetime.fromtimestamp(int(data['started_at'])).strftime(
            '%A %b %d %Y (%I:%M:%S %p)')
        ended_at = datetime.fromtimestamp(int(data['ended_at'])).strftime(
            '%A %b %d %Y (%I:%M:%S %p)')

        missed_call_status = 'No' if data['answered_at'] else 'Yes'
        return Markup(
            """
                                    <strong>Call ID:</strong> %(Call ID)s<br/>
                                    <strong>Started At:</strong> %(Start At)s<br/>
                                    <strong>Ended At:</strong> %(End At)s<br/>
                                    <strong>Contact Number:</strong> %(Contact Number)s<br/>
                                    <strong>Call direction:</strong> %(Call direction)s<br/>
                                    <strong>Aircall User:</strong> %(Aircall User)s<br/>
                                    <strong>Aircall Number:</strong> %(Aircall Number)s<br/>
                                    <strong>Call Duration:</strong> %(Call Duration)s<br/>
                                     <strong>Missed Call:</strong> %(Missed Call)s<br/>
                                    <strong>Tags:</strong> %(Tags)s<br/>
                                    <strong>Comments:</strong> %(Comments)s<br/>
                                    """

        ) % {
            'Call ID': '{}'.format(data["id"]),
            'Start At': '{}'.format(started_at),
            'End At': '{}'.format(ended_at),
            'Contact Number': '{}'.format(data["raw_digits"]),
            'Call direction': data["direction"],
            'Call Duration': '{} Sec'.format(data['duration']),
            'Missed Call': '{}'.format(missed_call_status),
            'Tags': '{}'.format(", ".join(tags)),
            'Comments': '{}'.format(" ".join(comments)),
            'Aircall User': '{}'.format(data.get("user", {}).get("name", "")),
            'Aircall Number': '{}'.format(data.get("number", {}).get("digits", "")),

        }

    def _post_message_and_create_call(self, partner, message, data, talk_time, waiting_time,
                                      tags, comments):
        """Posts a message and creates the call detail entry."""
        author_ref = self.env.ref('cit_aircall_api_integration.aircall_res_partner_1',
                                  raise_if_not_found=False)
        author_id = author_ref.id if author_ref else None
        manual_call_loging = self.env['ir.config_parameter'].sudo().get_param(
            'cit_aircall_api_integration.manual_call_loging')
        partner_matches = self.env['res.partner'].sudo().search([
            '|', ('phone', 'ilike', data['raw_digits']),
            '|', ('phone', 'ilike', data['raw_digits'].replace(" ", "")),
            '|', ('mobile', 'ilike', data['raw_digits']),
            ('mobile', 'ilike', data['raw_digits'].replace(" ", ""))
        ])
        mail_data = None  # Initialize mail_data to avoid UnboundLocalError
        if not manual_call_loging and len(partner_matches) > 1:
            # Multiple partners found, log message for the last parent's contact if any
            parents = partner_matches.mapped('parent_id').filtered(lambda p: p)
            if parents:
                last_parent = parents[0]  # Get the last parent
                mail_data = last_parent.sudo().message_post(
                    body=message,
                    author_id=author_id
                )
            else:
                mail_data = partner_matches[0].sudo().message_post(
                    body=message,
                    author_id=author_id
                )
        else:
            # Post message to the given partner
            mail_data = partner.sudo().message_post(
                body=message,
                author_id=author_id
            )
        # Process mail_data and create call detail
        if mail_data:
            mail_data.aircall_call_id = data['id']
            partner.sudo().write({'x_add_log_note': False})  # Reset add_log_note
            self.with_context(from_res_partner=True).create_call_detail(
                data['id'], data['asset'], waiting_time, partner, mail_data, data, talk_time,
                tags, comments
            )

    @api.model
    def _send_insight_card(self, payload):
        """ Method for sending the insight card """
        api_id, api_token = self.get_aircall_api_config()
        if False in [api_id, api_token]:
            _logger.warning(
                "Aircall api credentials are not set. Some features won't work")
            return
        json_field = self._populate_insight_card(payload)
        if json_field is False:
            # Callee was not found on the system on the system
            return
        aircall_url = AIRCALL_API_URL + "/calls/" + \
                      str(payload['data']['id']) + "/insight_cards"
        requests.post(aircall_url, auth=(
            api_id, api_token), json=json_field)

    def _get_helpdesk_ticket(self, raw_digits):
        """ Fetch Helpdesk ticket by partner's phone or mobile number only if Helpdesk is installed. """
        helpdesk_installed = self.env['ir.module.module'].sudo().search_count([
            ('name', '=', 'helpdesk'), ('state', '=', 'installed')
        ]) > 0
        enable_helpdesk_module = self.env['ir.config_parameter'].sudo().get_param(
            'cit_aircall_api_integration.enable_helpdesk_module'
        )

        if not helpdesk_installed:
            return self.env['ir.model.data'].browse()  # Returns an empty recordset safely

        if helpdesk_installed and enable_helpdesk_module:
            return self.env['helpdesk.ticket'].sudo().search([
                '|', ('partner_phone', 'ilike', raw_digits),
                '|', ('partner_phone', 'ilike', raw_digits.replace(" ", "")),
                '|', ('x_partner_mobile', 'ilike', raw_digits),
                ('x_partner_mobile', 'ilike', raw_digits.replace(" ", ""))
            ])

    @api.model
    def _populate_insight_card(self, payload):
        """ Method for populating the insight card to the current call, handling CRM, interactions, and Helpdesk. """
        data = payload['data']

        # Ensure Helpdesk module is installed before proceeding
        helpdesk_installed = self.env['ir.module.module'].sudo().search_count([
            ('name', '=', 'helpdesk'), ('state', '=', 'installed')
        ]) > 0

        enable_helpdesk_module = self.env['ir.config_parameter'].sudo().get_param(
            'cit_aircall_api_integration.enable_helpdesk_module'
        )

        # Search for partner based on phone number
        partner = self.env['res.partner'].sudo().search(
            [
                '|', ('phone', 'ilike', data['raw_digits']), '|',
                ('phone', 'ilike', data['raw_digits'].replace(" ", "")), '|',
                ('mobile', 'ilike', data['raw_digits']),
                ('mobile', 'ilike', data['raw_digits'].replace(" ", ""))
            ]
        )

        manual_call_loging = self.env['ir.config_parameter'].sudo().get_param(
            'cit_aircall_api_integration.manual_call_loging'
        )

        enable_crm_module = self.env['ir.config_parameter'].sudo().get_param(
            'cit_aircall_api_integration.enable_crm_module'
        )

        # Default partner name string
        if manual_call_loging:
            partner_name_string = 'Click to log call'
        elif manual_call_loging is False:
            last_partner = partner.sorted(key=lambda p: p.create_date, reverse=True)[0] if partner else False
            partner_name_string = last_partner.name if last_partner else 'No partners found'
            parents = last_partner.mapped('parent_id')
            if parents:
                last_partner = parents[-1]
                partner_name_string = last_partner.name
        else:
            partner_name_string = 'Select Contact'

        if len(partner) == 1:
            partner_name_string = partner.name
            partner.write({'x_add_log_note': True})

        if data.get('direction') == 'inbound':
            partner = self._handle_unknown_contact_creation(partner, self.env['res.partner'], data)

        # Handle CRM leads only if CRM module is enabled
        leads_text = 'Create new opportunity'
        lead = False  # Initialize lead here
        if enable_crm_module == 'True':
            lead = self._get_crm_lead(data['raw_digits'])
            if lead:
                if manual_call_loging:
                    leads_text = 'Click to log call'
                elif manual_call_loging is False:
                    parent_opportunity = self.env['crm.lead'].sudo().search(
                        [('partner_id', 'in', partner.mapped('parent_id').ids)],
                        order="id desc",
                        limit=1)
                    if parent_opportunity:
                        leads_text = parent_opportunity.name
                    else:
                        child_opportunity = self.env['crm.lead'].sudo().search(
                            [('partner_id', 'in', partner.ids)], order="id desc", limit=1)
                        leads_text = child_opportunity.name if child_opportunity else 'No lead found'
                else:
                    leads_text = 'Select Opportunity'

                if len(lead) == 1 and partner:
                    leads_text = f"{lead[0].name}"

        # Generate initial JSON response
        json_field = self._generate_insight_card_json(partner, partner_name_string, data)
        if not json_field:
            return False

        # Extend with lead information only if CRM module is enabled
        if enable_crm_module == 'True':
            last_partner = partner.sorted(key=lambda p: p.create_date, reverse=True)[0] if partner else None
            result = self._extend_card_with_lead_info(json_field, lead, leads_text, last_partner)
        else:
            result = json_field

        # Custom logic for Helpdesk tickets only if module is installed and enabled
        if helpdesk_installed and enable_helpdesk_module == 'True':
            helpdesk = self._get_helpdesk_ticket(data['raw_digits']) or self.env['helpdesk.ticket']
            helpdesk_text = 'Select Ticket'
            partner = self._find_partner(self.env['res.partner'], data['raw_digits']) or self.env['res.partner']

            if len(helpdesk) == 1 and partner:
                helpdesk_text = helpdesk.name

            result = self._extend_card_with_helpdesk_info(result, helpdesk, helpdesk_text,
                                                          partner[0] if partner else None)

        return result

    def _extend_card_with_helpdesk_info(self, result, helpdesk, helpdesk_text, partner):
        """Extend insight card with helpdesk ticket information using Odoo internal URLs."""
        enable_helpdesk_module = self.env['ir.config_parameter'].sudo().get_param(
            'cit_aircall_api_integration.enable_helpdesk_module'
        )
        if enable_helpdesk_module != 'True':
            _logger.warning("Helpdesk module is disabled in settings. Skipping helpdesk integration.")
            return result

        helpdesk_installed = self.env['ir.module.module'].sudo().search_count([
            ('name', '=', 'helpdesk'), ('state', '=', 'installed')
        ]) > 0

        if not helpdesk_installed:
            _logger.warning("Helpdesk module is not installed. Skipping helpdesk integration.")
            return result

        action = self.env.ref('helpdesk.helpdesk_ticket_action_main_tree', raise_if_not_found=False)

        helpdesk_ticket_setting = self.env['ir.config_parameter'].sudo().get_param(
            'cit_aircall_api_integration.helpdesk_log_note_setting'
        )
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        partner = partner[0] if isinstance(partner, list) else partner
        url = False
        context = {
            'default_partner_id': partner.id,
            'default_name': 'Ticket of ' + (partner.name or 'Unknown')
        }
        context_str = urllib.parse.quote(json.dumps(context))
        if helpdesk_ticket_setting == 'open_new_ticket':
            helpdesk_id = self.env['helpdesk.ticket'].sudo().create({
                'partner_id': partner.id,
                'name': f"Ticket of {partner.name or 'Unknown'}",
                'x_add_log_note': True
            })
            url = f"{base_url}/web#action={action.id}&id={helpdesk_id.id}&context={context_str}&model=helpdesk.ticket&view_type=form"

        elif helpdesk_ticket_setting == 'add_log_note_exciting':
            ticket_ids = helpdesk.ids

            if ticket_ids and len(ticket_ids) == 1:
                url = f"{base_url}/web#action={action.id}&id={ticket_ids[0]}&context={context_str}&model=helpdesk.ticket&view_type=form"
            elif ticket_ids and len(ticket_ids) > 1:
                domain = [('id', 'in', ticket_ids)]
                domain_str = urllib.parse.quote(json.dumps(domain))
                url = f"{base_url}/web#action={action.id}&context={context_str}&model=helpdesk.ticket&view_type=list&aircall_domain={domain_str}"
            else:
                domain = [('id', '=', False)]
                domain_str = urllib.parse.quote(json.dumps(domain))
                url = f"{base_url}/web#action={action.id}&context={context_str}&model=helpdesk.ticket&view_type=list&aircall_domain={domain_str}"

        if url:
            result['contents'].append({
                'type': 'shortText',
                'label': 'Ticket',
                'text': helpdesk_text,
                'link': url
            })

        _logger.info(result)
        return result

    def _generate_insight_card_json(self, partner, partner_name_string, data):
        """Generate JSON field for insight card with dynamic form/list view logic."""
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        action = self.env.ref('cit_aircall_api_integration.action_contacts_extended',
                              raise_if_not_found=False)
        if len(partner.ids) == 1:
            # Single partner: go to form view
            partner_url = f"{base_url}/web#action={action.id}&id={partner.ids[0]}&model=res.partner&view_type=form"
        else:
            # Multiple partners: go to list view with domain filter
            domain = [('id', 'in', partner.ids)]
            domain_str = urllib.parse.quote(json.dumps(domain))
            partner_url = (
                f"{base_url}/web#action={action.id}&model=res.partner"
                f"&view_type=list&cids=1&aircall_domain={domain_str}"
            )

        return {
            'contents': [
                {
                    'type': 'title',
                    'text': 'Odoo information',
                    'link': partner_url,
                },
                {
                    'type': 'shortText',
                    'label': 'Contact',
                    'text': partner_name_string,
                    'link': partner_url
                }
            ]
        }

    @api.model
    def _register_contact(self, payload):
        """ Method called when contact is created in aircall. """
        _logger.info(payload)
        phone_format = ''
        res_partner = self.env['res.partner']
        phone_details = self.env['phone.details']
        email_details = self.env['email.details']
        contact = payload['data']
        company = False

        if contact['phone_numbers']:
            phone = phonenumbers.parse(contact['phone_numbers'][0]['value'])
            phone_format = phonenumbers.format_number(
                phone, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            phone_format_clean = phone_format.replace(" ", "")

        partner = res_partner.sudo().search([
            ('name', '=', contact['first_name']),
            '|', '|', '|',
            ('phone', 'ilike', phone_format),
            ('phone', 'ilike', phone_format_clean),
            ('mobile', 'ilike', phone_format),
            ('mobile', 'ilike', phone_format_clean)
        ])

        if not partner:
            if contact['company_name']:
                company = res_partner.sudo().search(
                    [('name', '=', contact['company_name'])], limit=1)
                if not company:
                    company = res_partner.sudo().create({
                        'name': contact['company_name'],
                        'company_type': 'company',
                        'is_company': True,
                        'aircall_id': contact['id']
                    })
            partner = res_partner.sudo().create({
                'name': contact['first_name'],
                'last_name': contact['last_name'] or '',
                'comment': contact['information'],
                'phone': phone_format if contact['phone_numbers'] else '',
                'email': contact['emails'][0]['value'] if contact['emails'] else '',
                'parent_id': company and company.id or False,
                'aircall_id': contact['id'],
                'direct_link': contact['direct_link'],
                'is_shared': contact['is_shared'],
            })
            for phone in contact['phone_numbers']:
                phone_details.sudo().create({
                    'phone_id': phone['id'],
                    'label': phone['label'],
                    'value': phone['value'],
                    'partner_id': partner.id,
                })
            for email in contact['emails']:
                email_details.sudo().create({
                    'email_id': email['id'],
                    'label': email['label'],
                    'value': email['value'],
                    'partner_id': partner.id,
                })

    def _get_crm_lead(self, raw_digits):
        """ Fetch CRM lead by phone or mobile number only if CRM is installed. """
        crm_installed = self.env['ir.module.module'].sudo().search_count([
            ('name', '=', 'crm'), ('state', '=', 'installed')
        ]) > 0

        if not crm_installed:
            return self.env['ir.model.data'].browse()  # Returns an empty recordset safely

        return self.env['crm.lead'].sudo().search([
            '|', ('phone', 'ilike', raw_digits),
            '|', ('phone', 'ilike', raw_digits.replace(" ", "")),
            '|', ('mobile', 'ilike', raw_digits),
            ('mobile', 'ilike', raw_digits.replace(" ", "")),
        ])

    def _extend_card_with_lead_info(self, result, lead, leads_text, partner):
        """Extend insight card with lead information using Odoo internal URLs."""
        _logger.info("Processing lead information for partner: %s", partner)

        crm_installed = self.env['ir.module.module'].sudo().search_count(
            [('name', '=', 'crm'), ('state', '=', 'installed')]
        )


        if not crm_installed:
            _logger.warning("CRM module is not installed.")
            return result

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        action = self.sudo().env.ref('crm.crm_lead_opportunities')
        context = {
            'default_partner_id': partner.id,
            'default_name': f'Opportunity of {partner.name}'
        }
        context_str = urllib.parse.quote(json.dumps(context))
        if lead and len(lead) == 1:
            url = f"{base_url}/web#action={action.id}&id={lead.ids[0]}&context={context_str}&model=crm.lead&view_type=form"
        elif lead and len(lead) > 1:
            domain = [('id', 'in', lead.ids)]
            domain_str = urllib.parse.quote(json.dumps(domain))
            url = f"{base_url}/web#action={action.id}&context={context_str}&model=crm.lead&view_type=list&aircall_domain={domain_str}"
        else:
            domain = [('id', '=', False)]
            domain_str = urllib.parse.quote(json.dumps(domain))
            url = f"{base_url}/web#action={action.id}&context={context_str}&model=crm.lead&view_type=list&aircall_domain={domain_str}"

        result['contents'].append({
            'type': 'shortText',
            'label': 'Opportunity',
            'text': leads_text,
            'link': url
        })

        _logger.info("Updated result: %s", result)
        return result

    def _is_number_configured(self, digits):
        """Find the configure aircall number in setting"""
        return self.env.company.number_crm_config_ids.sudo().filtered(
            lambda num: num.digits == digits)

    def _process_leads(self, crm_lead, data, tags, comments):
        """This method calls for adding a log note in lead for configured Aircall user"""

        enable_crm_module = self.env['ir.config_parameter'].sudo().get_param(
            'cit_aircall_api_integration.enable_crm_module'
        )

        if enable_crm_module != 'True':  # Ensure CRM module is explicitly enabled
            _logger.warning("CRM module is disabled in settings. Skipping call logging in opportunities.")
            return

        manual_call_loging = self.env['ir.config_parameter'].sudo().get_param(
            'cit_aircall_api_integration.manual_call_loging'
        )
        partner = self._find_partner(self.env['res.partner'], data['raw_digits'])

        lead_to_log = None

        if len(crm_lead) == 1:
            lead_to_log = crm_lead[0]  # Log in the single opportunity

        elif len(crm_lead) > 1:
            if not manual_call_loging:  # manual_call_loging is a string, so check for 'True'
                parent_opportunity = self.env['crm.lead'].sudo().search(
                    [('partner_id', 'in', partner.mapped('parent_id').ids)], order="id desc",
                    limit=1)
                if parent_opportunity:
                    lead_to_log = parent_opportunity[0]
                else:
                    lead_to_log = crm_lead[0]  # Log in the first opportunity
            else:
                # If more than one lead and manual_call_loging is False, log in the one with x_add_log_note=True
                lead_with_log_note = crm_lead.filtered(lambda lead: lead.x_add_log_note)
                if lead_with_log_note:
                    lead_to_log = lead_with_log_note[0]  # Log in the opportunity with x_add_log_note=True

        if lead_to_log:  # Proceed only if there is a valid lead to log
            talk_time, waiting_time = self._calculate_times(data)

            if self._is_number_configured(data['number']['digits']):
                message = self._generate_message(data, talk_time, waiting_time, tags, comments)
                author_ref = self.env.ref(
                    'cit_aircall_api_integration.aircall_res_partner_1',
                    raise_if_not_found=False)
                author_id = author_ref.id if author_ref else None
                mail_data = lead_to_log.sudo().message_post(body=message,
                                                            author_id=author_id if author_id else None)
                if mail_data:
                    mail_data.aircall_call_id = data['id']
                    self.create_call_detail(
                        data['id'], data['asset'], waiting_time, lead_to_log, mail_data, data,
                        talk_time,
                        tags, comments
                    )

        # Reset 'x_add_log_note' field to False after processing
        crm_lead.filtered(lambda a: a.x_add_log_note).sudo().write({'x_add_log_note': False})
