#!/bin/bash
set -e

# Check if we need to start Xvfb for headed browser support
if [ "$TIKTOK_HEADLESS" = "false" ] && [ -z "$DISPLAY" ]; then
    echo "🖥️  Starting Xvfb virtual display for headed browser support..."
    
    # Clean up any existing Xvfb processes
    rm -f /tmp/.X99-lock
    
    # Start Xvfb on display :99 with 1920x1080 resolution and 24-bit color
    Xvfb :99 -screen 0 1920x1080x24 -nolisten tcp -nolisten unix &
    XVFB_PID=$!
    
    # Wait for Xvfb to start
    sleep 2
    
    # Export display for all processes
    export DISPLAY=:99
    
    echo "✅ Virtual display started on DISPLAY=:99"
    
    # Trap to cleanup Xvfb on exit
    trap "echo 'Cleaning up Xvfb...'; kill $XVFB_PID 2>/dev/null || true" EXIT INT TERM
else
    if [ "$TIKTOK_HEADLESS" = "false" ]; then
        echo "🖥️  DISPLAY already set to: $DISPLAY"
    else
        echo "🔲 Running in headless mode (TIKTOK_HEADLESS=$TIKTOK_HEADLESS)"
    fi
fi

# Execute the main command
exec "$@"