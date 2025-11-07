"""
MCP tool for testing status bar progress reporting.

This tool simulates work with progress updates to demonstrate
the MCP Status Bar extension in VS Code.
"""

import json
import time

from fastmcp import FastMCP

# Create a simple test MCP app
app = FastMCP("Test Progress MCP")


@app.tool()
def simulate_work(duration_seconds: int = 10, steps: int = 10) -> str:
    """
    Simulate long-running work with progress updates.

    This tool performs simulated work in steps, reporting progress
    at each step so the VS Code extension can display a progress bar.

    Args:
        duration_seconds: Total duration of simulated work in seconds
        steps: Number of progress steps to report

    Returns:
        JSON with completion status and summary
    """
    step_duration = duration_seconds / steps

    for step in range(1, steps + 1):
        # Simulate work
        time.sleep(step_duration)

        # Report progress (this gets captured by the proxy)
        # Note: In real FastMCP, you'd use ctx.report_progress()
        # For now we just log progress
        percentage = (step / steps) * 100
        print(f"Progress: {percentage:.0f}%", flush=True)

    return json.dumps(
        {"status": "complete", "steps_completed": steps, "duration": duration_seconds}
    )


if __name__ == "__main__":
    app.run()
