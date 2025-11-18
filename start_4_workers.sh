#!/bin/bash
# Quick start script to launch 4 parallel workers in tmux
# Run this on your EC2 instance

SESSION_NAME="video_conversion"

# Check if session already exists
tmux has-session -t $SESSION_NAME 2>/dev/null

if [ $? == 0 ]; then
    echo "⚠️  Session '$SESSION_NAME' already exists!"
    echo "Options:"
    echo "  1. Attach to existing session: tmux attach -t $SESSION_NAME"
    echo "  2. Kill and restart: tmux kill-session -t $SESSION_NAME && $0"
    exit 1
fi

# Your conversion parameters
INPUT_FOLDER="AI CERTs/Synthesia V3 Videos/AI+ Writer/"
INPUT_BUCKET="cdn.netcomplus.com"
OUTPUT_BUCKET="cdn.netcomplus.com"
OUTPUT_PREFIX="streams/AI CERTs/Synthesia V3 Videos/AI+ Writer/"

# Build the command
CMD="python3 convert_ffmpeg.py \"$INPUT_FOLDER\" $INPUT_BUCKET $OUTPUT_BUCKET \"$OUTPUT_PREFIX\""

echo "🚀 Starting 4 parallel workers in tmux..."
echo "Session name: $SESSION_NAME"
echo "Command: $CMD"
echo ""

# Create new session and run command in first pane
tmux new-session -d -s $SESSION_NAME "$CMD"

# Split horizontally (top/bottom)
tmux split-window -v -t $SESSION_NAME "$CMD"

# Select top pane and split vertically (left/right)
tmux select-pane -t $SESSION_NAME:0.0
tmux split-window -h -t $SESSION_NAME "$CMD"

# Select bottom pane and split vertically (left/right)
tmux select-pane -t $SESSION_NAME:0.2
tmux split-window -h -t $SESSION_NAME "$CMD"

# Adjust pane sizes to be equal
tmux select-layout -t $SESSION_NAME tiled

echo "✅ 4 workers started successfully!"
echo ""
echo "To attach to the session:"
echo "  tmux attach -t $SESSION_NAME"
echo ""
echo "To detach (keep running):"
echo "  Press: Ctrl+B then d"
echo ""
echo "To view this session's status:"
echo "  tmux ls"
echo ""
echo "To kill all workers:"
echo "  tmux kill-session -t $SESSION_NAME"
echo ""
echo "📊 Workers are now processing videos in parallel!"

