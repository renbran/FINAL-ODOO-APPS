# -*- coding: utf-8 -*-
import base64
import io
import logging
import os
import tempfile
from contextlib import closing

# Import PDF libraries with compatibility
try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    try:
        from PyPDF2 import PdfReader, PdfWriter
    except ImportError:
        from PyPDF2 import PdfFileReader as PdfReader, PdfFileWriter as PdfWriter

from odoo import api, models, fields
from odoo.tools import pdf

_logger = logging.getLogger(__name__)


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    apply_osus_template = fields.Boolean(
        string='Apply OSUS Template',
        default=True,
        help='Apply the global OSUS Properties template to this report'
    )

    def _get_osus_template_path(self):
        """Get the path to the OSUS template PDF"""
        module_path = os.path.dirname(os.path.dirname(__file__))
        template_path = os.path.join(module_path, 'static', 'template', 'osus_template.pdf')
        
        if os.path.exists(template_path):
            return template_path
        
        _logger.warning(f"OSUS template not found at: {template_path}")
        return None

    def _get_pdf_page_count(self, pdf_reader):
        """Universal method to get page count"""
        try:
            return len(pdf_reader.pages)
        except AttributeError:
            try:
                return pdf_reader.getNumPages()
            except AttributeError:
                return 0

    def _get_pdf_page(self, pdf_reader, page_num):
        """Universal method to get PDF page"""
        try:
            return pdf_reader.pages[page_num]
        except (AttributeError, TypeError):
            try:
                return pdf_reader.getPage(page_num)
            except AttributeError:
                return None

    def _add_page_to_writer(self, writer, page):
        """Universal method to add page to writer"""
        try:
            writer.add_page(page)
        except AttributeError:
            writer.addPage(page)

    def _merge_pages(self, template_page, content_page):
        """Universal method to merge pages"""
        try:
            template_page.merge_page(content_page)
        except AttributeError:
            template_page.mergePage(content_page)
        return template_page

    def _apply_osus_template_to_pdf(self, pdf_content):
        """
        Apply OSUS template to the generated PDF content
        
        Args:
            pdf_content: bytes - The original PDF content
            
        Returns:
            bytes - The PDF content with OSUS template applied
        """
        # Check if template should be applied
        if not self.apply_osus_template:
            return pdf_content
        
        template_path = self._get_osus_template_path()
        if not template_path:
            _logger.warning("OSUS template not available, returning original PDF")
            return pdf_content
        
        try:
            # Read template PDF into memory first
            with open(template_path, "rb") as template_file:
                template_content = template_file.read()
            
            # Create input PDF reader from bytes
            input_stream = io.BytesIO(pdf_content)
            input_reader = PdfReader(input_stream)
            page_count = self._get_pdf_page_count(input_reader)
            
            if page_count == 0:
                _logger.warning("Input PDF has no pages")
                return pdf_content
            
            # Create output writer
            output_writer = PdfWriter()
            
            # Apply template to each page
            for i in range(page_count):
                content_page = self._get_pdf_page(input_reader, i)
                
                if content_page:
                    # Create fresh template reader for this page
                    template_stream = io.BytesIO(template_content)
                    template_reader = PdfReader(template_stream)
                    template_page = self._get_pdf_page(template_reader, 0)
                    
                    if not template_page:
                        _logger.error(f"Could not read OSUS template page for page {i}")
                        # Add content page without template
                        self._add_page_to_writer(output_writer, content_page)
                        continue
                    
                    # Merge content onto template
                    try:
                        merged_page = self._merge_pages(template_page, content_page)
                        self._add_page_to_writer(output_writer, merged_page)
                    except Exception as merge_error:
                        _logger.warning(f"Could not merge template for page {i}: {merge_error}")
                        # Fall back to content page without template
                        self._add_page_to_writer(output_writer, content_page)
            
            # Write output PDF to bytes
            output_stream = io.BytesIO()
            output_writer.write(output_stream)
            output_stream.seek(0)
            final_content = output_stream.read()
            
            _logger.info(f"✅ Applied OSUS template to {page_count} pages")
            return final_content

                        
        except Exception as e:
            _logger.error(f"Error applying OSUS template: {str(e)}", exc_info=True)
            # Return original PDF on error
            return pdf_content

    def _render_qweb_pdf_prepare_streams(self, report_ref, data, res_ids=None):
        """
        Override to apply OSUS template after PDF generation
        This is called for each report and has access to self as the report
        """
        _logger.info(f"🔍 _render_qweb_pdf_prepare_streams called for report_ref: {report_ref}")
        
        # Generate the base PDF streams using parent method
        collected_streams = super()._render_qweb_pdf_prepare_streams(report_ref, data, res_ids)
        
        _logger.info(f"📊 Generated {len(collected_streams)} streams")
        
        # Get report object to check if template should be applied
        report_sudo = self._get_report(report_ref)
        
        # Apply template to each stream if enabled
        if hasattr(report_sudo, 'apply_osus_template') and report_sudo.apply_osus_template:
            _logger.info(f"🎨 Applying OSUS template to report: {report_sudo.name}")
            
            for res_id, stream_data in collected_streams.items():
                if stream_data and stream_data.get('stream'):
                    original_stream = stream_data['stream']
                    if original_stream:
                        try:
                            # Get PDF content from stream
                            original_stream.seek(0)
                            pdf_content = original_stream.read()
                            _logger.info(f"   Original PDF size: {len(pdf_content)} bytes for res_id={res_id}")
                            
                            # Apply template
                            modified_content = report_sudo._apply_osus_template_to_pdf(pdf_content)
                            _logger.info(f"   Modified PDF size: {len(modified_content)} bytes")
                            
                            # Create new stream with modified content
                            new_stream = io.BytesIO(modified_content)
                            stream_data['stream'] = new_stream
                            
                        except Exception as e:
                            _logger.error(f"❌ Error applying template to res_id={res_id}: {e}", exc_info=True)
                            # Keep original stream on error
        else:
            if hasattr(report_sudo, 'apply_osus_template'):
                _logger.info(f"ℹ️ Template application disabled for report: {report_sudo.name}")
            else:
                _logger.info(f"⚠️ Report has no apply_osus_template field: {report_sudo.name}")
        
        return collected_streams
