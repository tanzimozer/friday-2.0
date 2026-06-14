#!/bin/bash
# Friday 2.0 Upgrades Setup Script

echo "=== Friday 2.0 Cost Optimization Upgrades Setup ==="
echo ""

HERMES_DIR="$HOME/.hermes"
EDITH_DIR="$HERMES_DIR/edith"

# Create EDITH directory
mkdir -p "$EDITH_DIR"
chmod 700 "$EDITH_DIR"
echo "✓ EDITH directory created: $EDITH_DIR"

# Copy EDITH vault
cp friday_upgrades/v2.0/edith_vault.json "$EDITH_DIR/edith_vault.json"
chmod 600 "$EDITH_DIR/edith_vault.json"
echo "✓ EDITH vault installed"

# Copy persistent memory config
cp friday_upgrades/v2.0/friday_persistent_memory_v2.json "$HERMES_DIR/friday_persistent_memory_v2.json"
chmod 600 "$HERMES_DIR/friday_persistent_memory_v2.json"
echo "✓ Persistent memory config installed"

# Verify EDITH access
echo ""
echo "=== EDITH Verification ==="
if [ -f "$EDITH_DIR/edith_vault.json" ]; then
    echo "✓ EDITH vault exists and is accessible"
    echo "  Location: $EDITH_DIR/edith_vault.json"
    echo "  Permissions: $(ls -la $EDITH_DIR/edith_vault.json | awk '{print $1}')"
else
    echo "✗ EDITH vault not found. Setup failed."
    exit 1
fi

echo ""
echo "=== Setup Complete ==="
echo "Friday 2.0 upgrades are ready for use."
echo ""
echo "Next steps:"
echo "1. Verify EDITH access with 3-factor authentication"
echo "2. Test skill auto-binding with sample tasks"
echo "3. Confirm 5 AM PDT daily refresh cron job"
