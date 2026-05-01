#!/usr/bin/bash

# Start Xvfb in the background on display 99
# -screen 0 1280x1024x24 defines resolution and color depth
Xvfb :99 -screen 0 1280x1024x24 -nolisten tcp &

# Give Xvfb a moment to start up
sleep 2

# Execute the main container command (CMD from Dockerfile or docker run)
exec "$@"