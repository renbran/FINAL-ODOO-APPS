# Odoo 17 Dockerfile with Python packages
FROM odoo:17.0

# Switch to root user
USER root

# Install additional Python packages required by custom modules
RUN pip3 install --no-cache-dir \
    pandas>=2.3.1 \
    openpyxl>=3.1.5 \
    moment>=0.12.1 \
    xlsxwriter>=3.0.2 \
    python-dateutil>=2.9.0 \
    numpy>=2.2.6 \
    dateparser>=1.2.2 \
    arrow>=1.3.0 \
    regex>=2024.11.6

# Copy custom addons
COPY . /mnt/extra-addons

# Copy requirements file for future reference
COPY requirements.txt /mnt/requirements.txt

# Set proper permissions
RUN chown -R odoo:odoo /mnt/extra-addons

# Switch back to odoo user
USER odoo

# Set the default command
CMD ["odoo"]
