# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID

def migrate(cr, version):
    # Update foreign key constraints for ON DELETE SET NULL
    cr.execute('''
        ALTER TABLE account_move DROP CONSTRAINT IF EXISTS account_move_project_id_fkey;
        ALTER TABLE account_move
          ADD CONSTRAINT account_move_project_id_fkey
          FOREIGN KEY (project_id)
          REFERENCES sale_order_project (id)
          ON DELETE SET NULL;

        ALTER TABLE account_move DROP CONSTRAINT IF EXISTS account_move_unit_id_fkey;
        ALTER TABLE account_move
          ADD CONSTRAINT account_move_unit_id_fkey
          FOREIGN KEY (unit_id)
          REFERENCES sale_order_unit (id)
          ON DELETE SET NULL;

        ALTER TABLE sale_order DROP CONSTRAINT IF EXISTS sale_order_project_id_fkey;
        ALTER TABLE sale_order
          ADD CONSTRAINT sale_order_project_id_fkey
          FOREIGN KEY (project_id)
          REFERENCES sale_order_project (id)
          ON DELETE SET NULL;

        ALTER TABLE sale_order DROP CONSTRAINT IF EXISTS sale_order_unit_id_fkey;
        ALTER TABLE sale_order
          ADD CONSTRAINT sale_order_unit_id_fkey
          FOREIGN KEY (unit_id)
          REFERENCES sale_order_unit (id)
          ON DELETE SET NULL;
    ''')
