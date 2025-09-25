from odoo import models, fields, api
from odoo.exceptions import UserError
import base64
from io import BytesIO

# Only import reportlab if available
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, mm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class CommissionReportGenerator(models.Model):
    _name = 'commission.report.generator'
    _description = 'Commission Report Generator'

    def generate_commission_report(self, sale_order_id):
        """Generate enhanced commission report with complete structure and details"""
        import logging
        logger = logging.getLogger(__name__)
        
        if not REPORTLAB_AVAILABLE:
            raise UserError("ReportLab library is not installed. Please install it with: pip install reportlab")
            
        sale_order = self.env['sale.order'].browse(sale_order_id)
        if not sale_order.exists():
            raise UserError("Sale order not found")
        
        logger.info(f"Generating enhanced commission report for order: {sale_order.name}")
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=15*mm,
            bottomMargin=15*mm,
            leftMargin=15*mm,
            rightMargin=15*mm
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # Define colors matching template
        burgundy_color = colors.HexColor("#800020")
        light_gray = colors.HexColor("#f8f9fa")
        medium_gray = colors.HexColor("#6c757d")
        border_color = colors.HexColor("#e9ecef")
        green_color = colors.HexColor("#28a745")
        
        # Page width calculation
        page_width = A4[0] - 30*mm
        
        # Enhanced styles matching template - use Helvetica for better compatibility
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=burgundy_color,
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'SubtitleStyle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=medium_gray,
            alignment=TA_CENTER,
            spaceAfter=16
        )
        
        section_header_style = ParagraphStyle(
            'SectionHeaderStyle',
            parent=styles['Normal'],
            fontSize=15,
            textColor=burgundy_color,
            fontName='Helvetica-Bold',
            spaceBefore=18,
            spaceAfter=10,
            borderWidth=0,
            borderColor=burgundy_color,
            borderPadding=0
        )
        
        # Report Header
        story.append(Paragraph("Commission Report", title_style))
        story.append(Paragraph(
            f"Order: <b>{sale_order.name}</b> | Date: <b>{sale_order.date_order.strftime('%m/%d/%Y') if sale_order.date_order else 'N/A'}</b>", 
            subtitle_style
        ))
        
        # Add border under header
        header_line = Table([[""]], colWidths=[page_width])
        header_line.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, -1), 2, burgundy_color),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(header_line)
        
        # Order Information Grid (Enhanced with more details)
        info_data = [
            ["Customer:", sale_order.partner_id.name or "N/A", "Project:", getattr(sale_order, 'project_id', False) and sale_order.project_id.name or "N/A"],
            ["Unit:", getattr(sale_order, 'unit_id', False) and sale_order.unit_id.name or "N/A", "Sales Value:", f"AED {sale_order.amount_total or 0:,.2f}"],
            ["Salesperson:", sale_order.user_id.name or "N/A", "Commission Status:", self._get_status_display(getattr(sale_order, 'commission_status', 'draft'))]
        ]
        
        # Calculate column widths for info grid
        col_width = page_width / 4
        info_table = Table(info_data, colWidths=[col_width * 0.7, col_width * 1.3, col_width * 0.7, col_width * 1.3])
        
        info_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 13),
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 13),  # Left labels
            ('FONT', (2, 0), (2, -1), 'Helvetica-Bold', 13),  # Right labels
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor("#333")),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor("#495057")),  # Left labels
            ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor("#495057")),  # Right labels
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (3, 0), (3, -1), 'LEFT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, -1), light_gray),
            ('GRID', (0, 0), (-1, -1), 1, border_color),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 16))
        
        # Calculate commission totals
        total_external = self._calculate_external_commission(sale_order)
        total_internal = self._calculate_internal_commission(sale_order)
        total_legacy = self._calculate_legacy_commission(sale_order)
        
        # Commission Details Section
        story.append(Paragraph("COMMISSION DETAILS", section_header_style))
        
        # Commission table with status per recipient
        commission_data = [
            ['Recipient', 'Type', 'Base Amount (AED)', 'Rate (%)', 'Commission (AED)', 'Status']
        ]
        
        # Add commission rows with status
        commission_rows = self._build_commission_rows(sale_order)
        commission_data.extend(commission_rows)
        
        # Add subtotal rows
        commission_data.extend([
            ["", "", "", "Total External Commissions:", f"{total_external:,.2f}", ""],
            ["", "", "", "Total Internal Commissions:", f"{total_internal:,.2f}", ""],
            ["", "", "", "Total Legacy Commissions:", f"{total_legacy:,.2f}", ""],
            ["", "", "", "TOTAL COMMISSION:", f"{total_external + total_internal + total_legacy:,.2f}", ""]
        ])
        
        # Create commission table
        commission_table = Table(commission_data, colWidths=[
            page_width * 0.25,   # Recipient
            page_width * 0.15,   # Type
            page_width * 0.18,   # Base Amount
            page_width * 0.12,   # Rate
            page_width * 0.20,   # Commission
            page_width * 0.10    # Status
        ])
        
        num_data_rows = len(commission_rows)
        commission_table.setStyle(self._get_commission_table_style(burgundy_color, light_gray, border_color, green_color, num_data_rows))
        
        story.append(commission_table)
        story.append(Spacer(1, 20))
        
        # Build PDF
        doc.build(story)
        pdf_data = buffer.getvalue()
        buffer.close()
        
        logger.info(f"Commission report generated successfully for order: {sale_order.name}")
        return pdf_data

    def _calculate_external_commission(self, sale_order):
        """Calculate total external commissions"""
        broker_amount = getattr(sale_order, 'broker_amount', 0) or 0
        referrer_amount = getattr(sale_order, 'referrer_amount', 0) or 0
        cashback_amount = getattr(sale_order, 'cashback_amount', 0) or 0
        other_external_amount = getattr(sale_order, 'other_external_amount', 0) or 0
        return broker_amount + referrer_amount + cashback_amount + other_external_amount

    def _calculate_internal_commission(self, sale_order):
        """Calculate total internal commissions"""
        agent1_amount = getattr(sale_order, 'agent1_amount', 0) or 0
        agent2_amount = getattr(sale_order, 'agent2_amount', 0) or 0
        manager_amount = getattr(sale_order, 'manager_amount', 0) or 0
        director_amount = getattr(sale_order, 'director_amount', 0) or 0
        return agent1_amount + agent2_amount + manager_amount + director_amount

    def _calculate_legacy_commission(self, sale_order):
        """Calculate total legacy commissions"""
        consultant_amount = getattr(sale_order, 'salesperson_commission', 0) or 0
        manager_legacy_amount = getattr(sale_order, 'manager_commission', 0) or 0
        second_agent_amount = getattr(sale_order, 'second_agent_commission', 0) or 0
        director_legacy_amount = getattr(sale_order, 'director_commission', 0) or 0
        return consultant_amount + manager_legacy_amount + second_agent_amount + director_legacy_amount

    def _build_commission_rows(self, sale_order):
        """Build commission rows with recipient status"""
        commission_rows = []
        base_amount = sale_order.amount_total or 0
        
        # EXTERNAL COMMISSIONS
        if hasattr(sale_order, 'broker_partner_id') and sale_order.broker_partner_id:
            broker_amount = getattr(sale_order, 'broker_amount', 0) or 0
            if broker_amount > 0:
                rate = getattr(sale_order, 'broker_rate', 0) or 0
                status = self._get_recipient_status(sale_order, 'broker')
                commission_rows.append([
                    self._truncate_name(sale_order.broker_partner_id.name or "N/A"),
                    "Broker",
                    f"{base_amount:,.2f}",
                    f"{rate:.2f}",
                    f"{broker_amount:,.2f}",
                    status
                ])
        
        if hasattr(sale_order, 'referrer_partner_id') and sale_order.referrer_partner_id:
            referrer_amount = getattr(sale_order, 'referrer_amount', 0) or 0
            if referrer_amount > 0:
                rate = getattr(sale_order, 'referrer_rate', 0) or 0
                status = self._get_recipient_status(sale_order, 'referrer')
                commission_rows.append([
                    self._truncate_name(sale_order.referrer_partner_id.name or "N/A"),
                    "Referrer",
                    f"{base_amount:,.2f}",
                    f"{rate:.2f}",
                    f"{referrer_amount:,.2f}",
                    status
                ])
        
        # INTERNAL COMMISSIONS
        if hasattr(sale_order, 'agent1_partner_id') and sale_order.agent1_partner_id:
            agent1_amount = getattr(sale_order, 'agent1_amount', 0) or 0
            if agent1_amount > 0:
                rate = getattr(sale_order, 'agent1_rate', 0) or 0
                status = self._get_recipient_status(sale_order, 'agent1')
                commission_rows.append([
                    self._truncate_name(sale_order.agent1_partner_id.name or "N/A"),
                    "Agent 1",
                    f"{base_amount:,.2f}",
                    f"{rate:.2f}",
                    f"{agent1_amount:,.2f}",
                    status
                ])
        
        # LEGACY COMMISSIONS
        if hasattr(sale_order, 'consultant_id') and sale_order.consultant_id:
            consultant_amount = getattr(sale_order, 'salesperson_commission', 0) or 0
            if consultant_amount > 0:
                rate = getattr(sale_order, 'consultant_comm_percentage', 0) or 0
                status = self._get_recipient_status(sale_order, 'consultant')
                commission_rows.append([
                    self._truncate_name(sale_order.consultant_id.name or "N/A"),
                    "Consultant (Legacy)",
                    f"{base_amount:,.2f}",
                    f"{rate:.2f}",
                    f"{consultant_amount:,.2f}",
                    status
                ])
        
        return commission_rows

    def _get_recipient_status(self, sale_order, recipient_type):
        """Get status for a specific commission recipient"""
        commission_status = getattr(sale_order, 'commission_status', 'draft')
        
        # Check if there's specific status for this recipient
        recipient_status_field = f"{recipient_type}_status"
        if hasattr(sale_order, recipient_status_field):
            status = getattr(sale_order, recipient_status_field, '')
            if status:
                return self._get_status_display(status)
        
        # Default status logic based on commission type and overall status
        if recipient_type in ['broker', 'cashback']:
            return "PAID" if commission_status == 'approved' else "PENDING"
        elif recipient_type in ['referrer', 'other_external']:
            return "DRAFT" if commission_status == 'draft' else "PENDING"
        elif recipient_type in ['agent1', 'agent2', 'manager', 'director']:
            return "APPROVED" if commission_status in ['approved', 'paid'] else "PENDING"
        else:  # Legacy
            return "LEGACY"

    def _truncate_name(self, name, max_length=25):
        """Truncate long names for better table formatting"""
        if not name:
            return "N/A"
        return name[:max_length] + "..." if len(name) > max_length else name

    def _get_status_display(self, status):
        """Get formatted status display"""
        if not status:
            return "N/A"
        status_map = {
            'draft': 'Draft',
            'pending': 'Pending Approval',
            'approved': 'Approved',
            'paid': 'Paid',
            'legacy': 'Legacy System'
        }
        return status_map.get(status, status.replace('_', ' ').title())

    def _get_commission_table_style(self, burgundy_color, light_gray, border_color, green_color, num_data_rows):
        """Get table style for commission table"""
        return TableStyle([
            # Header row styling
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 12),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (0, 0), (-1, 0), burgundy_color),
            ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
            ('ALIGN', (2, 0), (-1, 0), 'CENTER'),
            
            # Data rows styling
            ('FONT', (0, 1), (-1, num_data_rows), 'Helvetica', 11),
            ('TEXTCOLOR', (0, 1), (-1, num_data_rows), colors.black),
            ('ALIGN', (0, 1), (1, num_data_rows), 'LEFT'),
            ('ALIGN', (2, 1), (4, num_data_rows), 'RIGHT'),
            ('ALIGN', (3, 1), (3, num_data_rows), 'CENTER'),
            ('ALIGN', (5, 1), (5, num_data_rows), 'CENTER'),
            
            # Commission amounts in green
            ('TEXTCOLOR', (4, 1), (4, num_data_rows), green_color),
            ('FONT', (4, 1), (4, num_data_rows), 'Helvetica-Bold', 11),
            
            # Alternating row backgrounds
            ('BACKGROUND', (0, 1), (-1, num_data_rows), light_gray),
            
            # Subtotal rows styling
            ('FONT', (0, num_data_rows+1), (-1, -2), 'Helvetica-Bold', 11),
            ('TEXTCOLOR', (0, num_data_rows+1), (-1, -2), colors.black),
            ('BACKGROUND', (0, num_data_rows+1), (-1, -2), colors.HexColor("#f1f3f4")),
            ('ALIGN', (0, num_data_rows+1), (-1, -2), 'RIGHT'),
            
            # Grand total row styling
            ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold', 12),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
            ('BACKGROUND', (0, -1), (-1, -1), burgundy_color),
            ('ALIGN', (0, -1), (-1, -1), 'RIGHT'),
            
            # Spans for subtotal labels
            ('SPAN', (0, num_data_rows+1), (3, num_data_rows+1)),  # External
            ('SPAN', (0, num_data_rows+2), (3, num_data_rows+2)),  # Internal
            ('SPAN', (0, num_data_rows+3), (3, num_data_rows+3)),  # Legacy
            ('SPAN', (0, -1), (3, -1)),  # Grand total
            ('SPAN', (5, num_data_rows+1), (5, -1)),  # Status column
            
            # General formatting
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 1.5, border_color),
        ])