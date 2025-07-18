#!/bin/bash
# Temporary directory environment fix
export TMPDIR=/var/odoo/osuspro/temp
export TMP=/var/odoo/osuspro/temp  
export TEMP=/var/odoo/osuspro/temp
mkdir -p /var/odoo/osuspro/temp
chmod 755 /var/odoo/osuspro/temp
