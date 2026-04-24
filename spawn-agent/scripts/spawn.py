#!/usr/bin/env python3
"""
Spawn Agent - Auto-delegate tasks to subagents
Usage: /spawn <task description>

This script is called by the agent when /spawn is detected in user input.
It extracts the task and spawns a subagent automatically.
"""

import sys
import json

def main():
    # Get the full task description from arguments
    task = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    
    if not task:
        print("Usage: /spawn <task description>")
        print("Example: /spawn search for recent AI news and summarize")
        sys.exit(1)
    
    # Return JSON for the parent agent to process
    result = {
        "action": "spawn_subagent",
        "task": task,
        "timeout": 300,  # 5 minutes default
        "message": f"🚀 Spawning subagent to handle: {task[:80]}{'...' if len(task) > 80 else ''}"
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
