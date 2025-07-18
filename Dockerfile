# Use official Odoo 17 image as base
FROM odoo:17

# Switch to root user to install dependencies
USER root

# Install additional system dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    git \
    curl \
    nano \
    && rm -rf /var/lib/apt/lists/*

# Install additional Python packages
RUN pip3 install \
    xlsxwriter \
    qrcode[pil] \
    Pillow \
    requests \
    python-dateutil \
    reportlab

# Create custom addons directory
RUN mkdir -p /mnt/extra-addons

# Copy custom modules to the container
COPY . /mnt/extra-addons/

# Set ownership for Odoo user
RUN chown -R odoo:odoo /mnt/extra-addons

# Switch back to odoo user
USER odoo

# Expose the default Odoo port
EXPOSE 8069

# Set the default command
CMD ["odoo", "--addons-path=/mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons"]

# Temporary directory fix
RUN mkdir -p /var/odoo/osuspro/temp && \
    chmod 755 /var/odoo/osuspro/temp && \
    chown odoo:odoo /var/odoo/osuspro/temp

# Set environment variables for temp directory
ENV TMPDIR=/var/odoo/osuspro/temp
ENV TMP=/var/odoo/osuspro/temp
ENV TEMP=/var/odoo/osuspro/temp
