#!/bin/sh
set -e

# Set SSHD configuration
echo "🤖 Setting SSHD configuration..."
{
    echo "Port 2222"
    echo "PermitRootLogin yes"
    echo "DebianBanner no"
    echo "PermitEmptyPasswords no"
    echo "MaxAuthTries 5"
    echo "LoginGraceTime 20"
    echo "ChallengeResponseAuthentication no"
    echo "KerberosAuthentication no"
    echo "GSSAPIAuthentication no"
    echo "X11Forwarding no"
    echo "AllowAgentForwarding yes"
    echo "AllowTcpForwarding yes"
    echo "PermitTunnel yes"

    echo "SyslogFacility AUTH"
    echo "LogLevel VERBOSE"
    # Enable MOTD display
    echo "PrintMotd yes"
    echo "PrintLastLog yes"
    # Strict authentication
    echo "PasswordAuthentication no"
    echo "UsePAM no"
    echo "AuthenticationMethods publickey"
    # Brute force protection
    echo "MaxSessions 10"
    echo "MaxAuthTries 3"
    echo "LoginGraceTime 15"
    echo "MaxStartups 10:30:100"
    echo "ClientAliveInterval 300"
    echo "ClientAliveCountMax 2"
} > /etc/ssh/sshd_config.d/custom.conf

chmod 700 \
    "/root/.ssh" \
    "/root/.ssh/authorized_keys"

# Ensure strict permissions on SSH configuration
chmod 600 /etc/ssh/sshd_config.d/*.conf
chmod 755 /etc/ssh/sshd_config.d

# Execute the CMD
exec "$@"
