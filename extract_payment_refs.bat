@echo off
echo Starting payment reference extraction from journal entries...
echo ==================================================

REM Run the extraction script in Odoo shell
docker-compose exec odoo odoo shell -d odoo --shell-interface ipython -c "exec(open('/mnt/extra-addons/extract_payment_refs.py').read())"

echo ==================================================
echo Payment reference extraction completed!
echo Check the output above for results.
pause
