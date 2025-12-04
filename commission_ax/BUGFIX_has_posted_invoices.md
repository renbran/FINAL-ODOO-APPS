# 🔧 BUGFIX: Missing Field `has_posted_invoices`

## Issue #4

**Error Type:** OwlError - Uncaught Promise  
**Location:** Sale Order View  
**Date Fixed:** December 4, 2025, 19:29 UTC

### Error Message
```
Error: "sale.order"."has_posted_invoices" field is undefined.
    at Field.parseFieldNode (web.assets_web.min.js:7795:231)
```

---

## Solution

### Field Definition Added

**File:** `models/sale_order.py`

```python
# Posted invoices check for compatibility
has_posted_invoices = fields.Boolean(
    string="Has Posted Invoices",
    compute="_compute_has_posted_invoices",
    help="True if this order has at least one posted invoice"
)
```

### Compute Method Added

```python
@api.depends('invoice_ids', 'invoice_ids.state')
def _compute_has_posted_invoices(self):
    """Check if this order has at least one posted invoice."""
    for order in self:
        posted_invoices = order.invoice_ids.filtered(lambda inv: inv.state == 'posted')
        order.has_posted_invoices = len(posted_invoices) > 0
```

---

## Deployment

### Database Updates

**osusproperties:**
```sql
-- Added automatically during module upgrade
ALTER TABLE sale_order ADD COLUMN has_posted_invoices BOOLEAN;
```

**erposus:**
```sql
-- Added manually
ALTER TABLE sale_order ADD COLUMN has_posted_invoices BOOLEAN DEFAULT FALSE;
```

### Module Upgrade
```bash
cd /var/odoo/osusproperties
python3 src/odoo-bin -c odoo.conf -d osusproperties -u commission_ax --stop-after-init --no-http
```

### Service Restart
```bash
systemctl restart odona-osusproperties.service
```

---

## Verification

✅ Field exists in osusproperties  
✅ Field exists in erposus  
✅ Service running without errors  
✅ No "field is undefined" errors in logs  

---

## Status

**DEPLOYED:** December 4, 2025, 19:29 UTC  
**Module:** commission_ax v17.0.2.0.0  
**Result:** ✅ SUCCESS

---

*This is the 4th missing field fixed in commission_ax module today.*
