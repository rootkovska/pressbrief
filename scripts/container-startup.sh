#!/bin/sh

# Set up variables
scriptPath=$(dirname $(readlink -f "${0}"))

# Save environment variables to file
printenv | sed 's/^\(.*\)$/export \1/g' > "${scriptPath}/.env.sh"
chmod +x "${scriptPath}/.env.sh"

# Create crontab file in cron directory
echo "0 0 * * * ${scriptPath}/pressbrief-execution.sh >> /var/log/cron.log 2>&1
# This extra line made it a valid crone" > /etc/cron.d/pressbrief

# Give execution rights on cron job
chmod 0644 /etc/cron.d/pressbrief

# Apply cron job
crontab /etc/cron.d/pressbrief

# Create log file
touch /var/log/cron.log

# Run command on container startup
cron && tail -f /var/log/cron.log