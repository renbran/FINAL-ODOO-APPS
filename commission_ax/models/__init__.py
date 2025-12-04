# -*- coding: utf-8 -*-
"""
Commission Models Initialization
=================================
Load models in correct dependency order
"""

import logging
_logger = logging.getLogger(__name__)

# Core commission model (must load first)
try:
    from . import commission_ax
    _logger.info("✅ commission_ax model loaded")
except Exception as e:
    _logger.error(f"❌ Failed to load commission_ax: {str(e)}")
    raise

# Related models (load after commission_ax)
try:
    from . import sale_order
    _logger.info("✅ sale_order model loaded")
except Exception as e:
    _logger.error(f"❌ Failed to load sale_order: {str(e)}")

try:
    from . import purchase_order
    _logger.info("✅ purchase_order model loaded")
except Exception as e:
    _logger.error(f"❌ Failed to load purchase_order: {str(e)}")

try:
    from . import cloudpepper_compatibility
    _logger.info("✅ cloudpepper_compatibility model loaded")
except Exception as e:
    _logger.warning(f"⚠️  cloudpepper_compatibility not loaded: {str(e)}")

try:
    from . import commission_report
    _logger.info("✅ commission_report model loaded")
except Exception as e:
    _logger.warning(f"⚠️  commission_report not loaded: {str(e)}")

_logger.info("🎯 Commission models initialization completed")