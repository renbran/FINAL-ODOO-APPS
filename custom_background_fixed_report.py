# See LICENSE file for full copyright and licensing details.
import base64
import logging
import os
import tempfile
from contextlib import closing
from itertools import islice

from lxml import etree

# FIX: Import correct PyPDF2/pypdf classes
try:
    from pypdf import PdfReader, PdfWriter
    _logger = logging.getLogger(__name__)
    _logger.info("Using pypdf (modern)")
except ImportError:
    try:
        from PyPDF2 import PdfReader, PdfWriter
        _logger = logging.getLogger(__name__)
        _logger.info("Using PyPDF2 (v3+)")
    except ImportError:
        # Fallback to old PyPDF2
        from PyPDF2 import PdfFileReader as PdfReader, PdfFileWriter as PdfWriter
        _logger = logging.getLogger(__name__)
        _logger.warning("Using legacy PyPDF2 - upgrade recommended")

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools import pdf, split_every
from odoo.tools.safe_eval import safe_eval
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


def _split_table(tree, max_rows):
    """
    Walks through the etree and splits tables with more than max_rows rows into
    multiple tables with max_rows rows.

    This function is needed because wkhtmltopdf has a exponential processing
    time growth when processing tables with many rows. This function is a
    workaround for this problem.

    :param tree: The etree to process
    :param max_rows: The maximum number of rows per table
    """
    for table in list(tree.iter("table")):
        prev = table
        for rows in islice(split_every(max_rows, table), 1, None):
            sibling = etree.Element("table", attrib=table.attrib)
            sibling.extend(rows)
            prev.addnext(sibling)
            prev = sibling


class ReportBackgroundLine(models.Model):
    _name = "report.background.line"
    _description = "Report Background Line"

    page_number = fields.Integer()
    # TODO after 17 release need to change field name to ttype.
    type = fields.Selection(  # pylint: disable=W8113
        [
            ("fixed", "Fixed Page"),
            ("expression", "Expression"),
            ("first_page", "First Page"),
            ("last_page", "Last Page"),
            ("remaining", "Remaining pages"),
            ("append", "Append"),
            ("prepend", "Prepend"),
        ],
        string="Type",
    )
    background_pdf = fields.Binary(string="Background PDF")
    # New field. #22260
    file_name = fields.Char()
    report_id = fields.Many2one(
        comodel_name="ir.actions.report", string="Report", ondelete="cascade"
    )
    page_expression = fields.Char()
    fall_back_to_company = fields.Boolean()
    # New fields. #22260
    lang_id = fields.Many2one(
        comodel_name="res.lang", string="Language", ondelete="cascade"
    )


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    custom_report_background = fields.Boolean()
    custom_report_background_image = fields.Binary(string="Background Image")
    custom_report_type = fields.Selection(
        [
            ("company", "From Company"),
            ("report", "From Report Fixed"),
            ("dynamic", "From Report Dynamic"),
            # Added new custom report type #T5886
            (
                "dynamic_per_report_company_lang",
                "Background Per Report - Company - Lang",
            ),
        ]
    )

    background_ids = fields.One2many(
        "report.background.line", "report_id", "Background Configuration"
    )
    # New fields. #22260
    bg_per_lang_ids = fields.One2many(
        "report.background.lang",
        "report_id",
        string="Background Per Language",
    )
    # New field #T5886
    is_bg_per_lang = fields.Boolean(string="Is Background Per Language?")
    # New field #T5886
    per_report_com_lang_bg_ids = fields.One2many(
        comodel_name="report.company.background.lang",
        inverse_name="report_id",
        string="Background Per Report - Company - Lang",
    )

    def add_pdf_watermarks(self, background_pdf, page):
        """
        FIX: Modernized PDF watermark merging with proper error handling
        """
        try:
            # Decode the background PDF
            back_data = base64.b64decode(background_pdf)
            
            # Create temporary file for background
            temp_back_fd, temp_back_path = tempfile.mkstemp(
                suffix=".pdf", prefix="watermark.tmp."
            )
            
            try:
                # Write background data
                with closing(os.fdopen(temp_back_fd, "wb")) as back_file:
                    back_file.write(back_data)
                
                # Read watermark PDF
                with open(temp_back_path, "rb") as watermark_file:
                    watermark_reader = PdfReader(watermark_file)
                    
                    # Get first page of watermark
                    if len(watermark_reader.pages) > 0:
                        watermark_page = watermark_reader.pages[0]
                        
                        # FIX: Use modern merge_page method (works with both old and new PyPDF2)
                        try:
                            # New API (PyPDF2 3.0+, pypdf)
                            watermark_page.merge_page(page)
                        except AttributeError:
                            # Legacy API (PyPDF2 < 3.0)
                            watermark_page.mergePage(page)
                        
                        return watermark_page
                    else:
                        _logger.warning("Watermark PDF has no pages, returning original page")
                        return page
                        
            finally:
                # Cleanup temp file
                try:
                    os.unlink(temp_back_path)
                except (OSError, IOError):
                    _logger.warning(f"Could not delete temp file: {temp_back_path}")
                    
        except Exception as e:
            _logger.error(f"Error adding PDF watermark: {str(e)}", exc_info=True)
            # Return original page on error
            return page

    def get_lang(self):
        """
        Get current language code from context
        """
        lang_code = self._context.get("lang", False)
        if not lang_code:
            lang_code = self.env.user.lang or "en_US"
        return lang_code

    def _get_background_per_report_company_language(self):
        """
        Get custom background based on report, company and language
        """
        company = self._context.get("background_company")
        if not company:
            return False
            
        lang_code = self.get_lang()
        
        # Filter backgrounds by report, company and language
        custom_bg = self.per_report_com_lang_bg_ids.filtered(
            lambda bg: bg.company_id.id == company.id
            and bg.lang_id.code == lang_code
            and bg.type_attachment == "default"
        )
        
        return custom_bg[:1].background_pdf if custom_bg else False

    def get_bg_per_lang(self):
        """
        Get custom background per language with proper fallback
        FIX: Added better error handling and fallback logic
        """
        try:
            lang_code = self.get_lang()
            company_background = self._context.get("background_company")
            
            # Initialize domain for language filtering
            lang_domain = []
            
            # If background per language is enabled
            if self.is_bg_per_lang and lang_code:
                lang_id = self.env["res.lang"].search([("code", "=", lang_code)], limit=1)
                if lang_id:
                    lang_domain = [("lang_id", "=", lang_id.id)]
                else:
                    # Fallback to default if language not found
                    _logger.warning(f"Language {lang_code} not found, using default")
                    lang_domain = [("lang_id", "=", False)]
            else:
                # If not per language, use default background
                lang_domain = [("lang_id", "=", False)]
                
            # Handle dynamic per report/company/language type
            if self.custom_report_type == "dynamic_per_report_company_lang":
                custom_background = self._get_background_per_report_company_language()
                return custom_background
                
            # Determine source of background (report or company)
            if self.custom_report_type == "report":
                custom_bg_from = self
            elif self.custom_report_type == "company" or not self.custom_report_type:
                custom_bg_from = company_background
            else:
                return False
                
            if not custom_bg_from:
                return False
                
            # Filter backgrounds by language
            custom_bg_lang = custom_bg_from.bg_per_lang_ids.filtered(
                lambda lang: lang.lang_id.code == lang_code
            )
            
            # Return first matching background
            return custom_bg_lang[:1].background_pdf if custom_bg_lang else False
            
        except Exception as e:
            _logger.error(f"Error in get_bg_per_lang: {str(e)}", exc_info=True)
            return False

    def _get_pdf_page_count(self, pdf_reader):
        """
        FIX: Universal method to get page count (works with old and new PyPDF2)
        """
        try:
            # Try new API first (PyPDF2 3.0+, pypdf)
            return len(pdf_reader.pages)
        except AttributeError:
            # Fall back to old API (PyPDF2 < 3.0)
            try:
                return pdf_reader.getNumPages()
            except AttributeError:
                _logger.error("Could not determine PDF page count")
                return 0

    def _get_pdf_page(self, pdf_reader, page_num):
        """
        FIX: Universal method to get PDF page (works with old and new PyPDF2)
        """
        try:
            # Try new API first (PyPDF2 3.0+, pypdf)
            return pdf_reader.pages[page_num]
        except (AttributeError, TypeError):
            # Fall back to old API (PyPDF2 < 3.0)
            try:
                return pdf_reader.getPage(page_num)
            except AttributeError:
                _logger.error(f"Could not get page {page_num} from PDF")
                return None

    def _dynamic_background_per_report(self, report, pdf_report_path):  # noqa: C901
        """
        FIX: Modernized dynamic background merging with proper error handling
        """
        lang_domain = []
        temporary_files = []
        
        if not report or not report.custom_report_background:
            return lang_domain, pdf_report_path
            
        try:
            if report.custom_report_type in ["dynamic", "dynamic_per_report_company_lang"]:
                # Create temp file for output
                temp_report_fd, temp_report_path = tempfile.mkstemp(
                    suffix=".pdf", prefix="with_back_report.tmp."
                )
                
                # FIX: Use modern PdfWriter
                output = PdfWriter()
                
                # FIX: Read source PDF with proper API
                with open(pdf_report_path, "rb") as pdf_file:
                    pdf_reader_content = PdfReader(pdf_file)
                    page_count = self._get_pdf_page_count(pdf_reader_content)
                    
                    # Get language domain for filtering backgrounds
                    lang_domain = report.with_context(**self.env.context).get_bg_per_lang()
                    
                    # Initialize background types
                    first_page = last_page = fixed_pages = remaining_pages = expression = False
                    
                    if report.custom_report_type == "dynamic":
                        # Search for different background types
                        first_page = report.background_ids.search(
                            (lang_domain if isinstance(lang_domain, list) else [])
                            + [("type", "=", "first_page"), ("report_id", "=", report.id)],
                            limit=1,
                        )
                        last_page = report.background_ids.search(
                            (lang_domain if isinstance(lang_domain, list) else [])
                            + [("type", "=", "last_page"), ("report_id", "=", report.id)],
                            limit=1,
                        )
                        fixed_pages = report.background_ids.search(
                            (lang_domain if isinstance(lang_domain, list) else [])
                            + [("type", "=", "fixed"), ("report_id", "=", report.id)]
                        )
                        remaining_pages = report.background_ids.search(
                            (lang_domain if isinstance(lang_domain, list) else [])
                            + [("type", "=", "remaining"), ("report_id", "=", report.id)],
                            limit=1,
                        )
                        expression = report.background_ids.search(
                            (lang_domain if isinstance(lang_domain, list) else [])
                            + [("type", "=", "expression"), ("report_id", "=", report.id)],
                            limit=1,
                        )
                    
                    # Get company background
                    company_background = self._context.get("background_company")
                    company_background_img = (
                        company_background.custom_report_background_image
                        if company_background
                        else False
                    )
                    
                    # Get language-specific company background
                    custom_bg_lang = False
                    if report.is_bg_per_lang and company_background:
                        lang_code = report.get_lang()
                        custom_bg_lang = company_background.bg_per_lang_ids.filtered(
                            lambda lang: lang.lang_id.code == lang_code
                        )
                    
                    # Process each page
                    for i in range(page_count):
                        watermark = False
                        
                        # Determine which background to use for this page
                        if report.custom_report_type == "dynamic_per_report_company_lang":
                            watermark = lang_domain if not isinstance(lang_domain, list) else False
                        elif first_page and i == 0:
                            if first_page.fall_back_to_company and company_background:
                                watermark = (
                                    custom_bg_lang[:1].background_pdf
                                    if report.is_bg_per_lang and custom_bg_lang
                                    else company_background_img
                                )
                            elif first_page.background_pdf:
                                watermark = first_page.background_pdf
                        elif last_page and i == page_count - 1:
                            if last_page.fall_back_to_company and company_background:
                                watermark = (
                                    custom_bg_lang[:1].background_pdf
                                    if report.is_bg_per_lang and custom_bg_lang
                                    else company_background_img
                                )
                            elif last_page.background_pdf:
                                watermark = last_page.background_pdf
                        elif fixed_pages and (i + 1) in fixed_pages.mapped("page_number"):
                            fixed_page = fixed_pages.filtered(lambda p: p.page_number == i + 1)[:1]
                            if fixed_page.fall_back_to_company and company_background:
                                watermark = (
                                    custom_bg_lang[:1].background_pdf
                                    if report.is_bg_per_lang and custom_bg_lang
                                    else company_background_img
                                )
                            elif fixed_page.background_pdf:
                                watermark = fixed_page.background_pdf
                        elif expression and expression.page_expression:
                            eval_dict = {"page": i + 1, "result": False}
                            try:
                                safe_eval(
                                    expression.page_expression,
                                    eval_dict,
                                    mode="exec",
                                    nocopy=True,
                                )
                            except Exception as e:
                                _logger.error(f"Error evaluating page expression: {str(e)}")
                            
                            if eval_dict.get("result", False):
                                if expression.fall_back_to_company and company_background:
                                    watermark = (
                                        custom_bg_lang[:1].background_pdf
                                        if report.is_bg_per_lang and custom_bg_lang
                                        else company_background_img
                                    )
                                elif expression.background_pdf:
                                    watermark = expression.background_pdf
                            elif remaining_pages:
                                if remaining_pages.fall_back_to_company and company_background:
                                    watermark = (
                                        custom_bg_lang[:1].background_pdf
                                        if report.is_bg_per_lang and custom_bg_lang
                                        else company_background_img
                                    )
                                elif remaining_pages.background_pdf:
                                    watermark = remaining_pages.background_pdf
                        else:
                            if remaining_pages:
                                if remaining_pages.fall_back_to_company and company_background:
                                    watermark = (
                                        custom_bg_lang[:1].background_pdf
                                        if report.is_bg_per_lang and custom_bg_lang
                                        else company_background_img
                                    )
                                elif remaining_pages.background_pdf:
                                    watermark = remaining_pages.background_pdf
                        
                        # Apply watermark or add original page
                        page = self._get_pdf_page(pdf_reader_content, i)
                        if page:
                            if watermark:
                                page = report.add_pdf_watermarks(watermark, page)
                            
                            # FIX: Use modern add_page method
                            try:
                                output.add_page(page)
                            except AttributeError:
                                output.addPage(page)
                
                # Write output
                with open(temp_report_path, "wb") as output_file:
                    output.write(output_file)
                
                pdf_report_path = temp_report_path
                os.close(temp_report_fd)
                
            elif report.custom_report_background:
                # Static background (company or report)
                temp_back_fd, temp_back_path = tempfile.mkstemp(
                    suffix=".pdf", prefix="back_report.tmp."
                )
                
                custom_background = False
                
                # Get background based on type
                if report.custom_report_type == "report":
                    if report.is_bg_per_lang:
                        custom_background = report.with_context(**self.env.context).get_bg_per_lang()
                    else:
                        custom_background = report.custom_report_background_image
                elif (
                    report.custom_report_type == "company" or not report.custom_report_type
                ) and self._context.get("background_company"):
                    company_id = self._context.get("background_company")
                    if report.is_bg_per_lang:
                        custom_background = report.with_context(**self.env.context).get_bg_per_lang()
                    else:
                        custom_background = company_id.custom_report_background_image
                
                # Apply background if found
                if custom_background:
                    back_data = base64.b64decode(custom_background)
                    with closing(os.fdopen(temp_back_fd, "wb")) as back_file:
                        back_file.write(back_data)
                    
                    temp_report_fd, temp_report_path = tempfile.mkstemp(
                        suffix=".pdf", prefix="with_back_report.tmp."
                    )
                    
                    output = PdfWriter()
                    
                    with open(pdf_report_path, "rb") as pdf_file:
                        pdf_reader_content = PdfReader(pdf_file)
                        page_count = self._get_pdf_page_count(pdf_reader_content)
                        
                        for i in range(page_count):
                            page = self._get_pdf_page(pdf_reader_content, i)
                            if page:
                                # Apply watermark
                                with open(temp_back_path, "rb") as watermark_file:
                                    pdf_reader_watermark = PdfReader(watermark_file)
                                    watermark = self._get_pdf_page(pdf_reader_watermark, 0)
                                    
                                    if watermark:
                                        # FIX: Use modern merge_page method
                                        try:
                                            watermark.merge_page(page)
                                        except AttributeError:
                                            watermark.mergePage(page)
                                        
                                        # FIX: Use modern add_page method
                                        try:
                                            output.add_page(watermark)
                                        except AttributeError:
                                            output.addPage(watermark)
                    
                    with open(temp_report_path, "wb") as output_file:
                        output.write(output_file)
                    
                    pdf_report_path = temp_report_path
                    os.close(temp_report_fd)
                    
                    # Cleanup temp background file
                    try:
                        os.unlink(temp_back_path)
                    except (OSError, IOError):
                        pass
                        
        except Exception as e:
            _logger.error(f"Error in _dynamic_background_per_report: {str(e)}", exc_info=True)
            # Return original path on error
            pass
            
        return lang_domain, pdf_report_path

    def _build_wkhtmltopdf_args(
        self,
        paperformat_id,
        landscape,
        specific_paperformat_args=None,
        set_viewport_size=False,
    ):
        """FIX: Ensure print media type is used for proper background rendering"""
        command_args = super()._build_wkhtmltopdf_args(
            paperformat_id,
            landscape,
            specific_paperformat_args=specific_paperformat_args,
            set_viewport_size=set_viewport_size,
        )
        # Add print media type for proper CSS rendering
        if "--print-media-type" not in command_args:
            command_args.extend(["--print-media-type"])
        return command_args

    @api.model
    def _run_wkhtmltopdf(  # noqa: C901
        self,
        bodies,
        report_ref=False,
        header=None,
        footer=None,
        landscape=False,
        specific_paperformat_args=None,
        set_viewport_size=False,
    ):
        """
        FIX: Modernized wkhtmltopdf execution with proper error handling
        """
        report = self._get_report(report_ref)
        
        # Generate base PDF
        pdf_content = super()._run_wkhtmltopdf(
            bodies,
            report_ref=report_ref,
            header=header,
            footer=footer,
            landscape=landscape,
            specific_paperformat_args=specific_paperformat_args,
            set_viewport_size=set_viewport_size,
        )
        
        # Save to temporary file
        temporary_files = []
        report_file_fd, pdf_report_path = tempfile.mkstemp(
            suffix=".pdf", prefix="report.inherited.tmp."
        )
        
        try:
            with closing(os.fdopen(report_file_fd, "wb")) as report_file:
                report_file.write(pdf_content)
            temporary_files.append(pdf_report_path)
            
            # Apply custom backgrounds
            lang_domain, pdf_report_path = self._dynamic_background_per_report(
                report=report, pdf_report_path=pdf_report_path
            )
            
            # Read final PDF
            with open(pdf_report_path, "rb") as pdf_document:
                pdf_content = pdf_document.read()
            
            # Handle append/prepend attachments
            if (
                report
                and report.custom_report_background
                and report.custom_report_type in ["dynamic", "dynamic_per_report_company_lang"]
            ):
                append_attachment = prepend_attachment = False
                
                if report.custom_report_type == "dynamic":
                    domain = lang_domain if isinstance(lang_domain, list) else []
                    prepend_attachment = report.background_ids.search(
                        domain + [("type", "=", "prepend"), ("report_id", "=", report.id)]
                    )
                    append_attachment = report.background_ids.search(
                        domain + [("type", "=", "append"), ("report_id", "=", report.id)]
                    )
                elif report.custom_report_type == "dynamic_per_report_company_lang":
                    company = self._context.get("background_company")
                    if company:
                        prepend_attachment = report.per_report_com_lang_bg_ids.filtered(
                            lambda bg: bg.type_attachment == "prepend"
                            and bg.background_pdf
                            and bg.company_id.id == company.id
                            and bg.report_id.id == report.id
                        )
                        append_attachment = report.per_report_com_lang_bg_ids.filtered(
                            lambda bg: bg.type_attachment == "append"
                            and bg.background_pdf
                            and bg.company_id.id == company.id
                            and bg.report_id.id == report.id
                        )
                
                # Merge attachments if found
                if prepend_attachment or append_attachment:
                    data = []
                    
                    # Add prepend attachments
                    for prepend_data in (prepend_attachment or []):
                        if prepend_data and prepend_data.background_pdf:
                            data.append(base64.b64decode(prepend_data.background_pdf))
                    
                    # Add main PDF
                    data.append(pdf_content)
                    
                    # Add append attachments
                    for append_data in (append_attachment or []):
                        if append_data and append_data.background_pdf:
                            data.append(base64.b64decode(append_data.background_pdf))
                    
                    # Merge all PDFs
                    if len(data) > 1:
                        pdf_content = pdf.merge_pdf(data)
                        
        except Exception as e:
            _logger.error(f"Error in _run_wkhtmltopdf: {str(e)}", exc_info=True)
            # Continue with original PDF content on error
            
        finally:
            # Cleanup temporary files
            for temporary_file in temporary_files:
                try:
                    os.unlink(temporary_file)
                except (OSError, IOError):
                    _logger.debug(f"Could not remove temporary file: {temporary_file}")
        
        return pdf_content
