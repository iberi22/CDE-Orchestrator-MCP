"""
Test MCP tool for status bar progress demonstration.

This tool simulates meaningful work with progress reporting
to demonstrate the MCP Status Bar extension.

Uses HTTP POST to send progress events to proxy endpoint.
"""

import asyncio
import json
import time
import urllib.request

from fastmcp import Context


async def cde_testProgressReporting(
    ctx: Context, duration: int = 10, steps: int = 10
) -> str:
    """
    Test tool that demonstrates progress reporting for the status bar.

    This tool performs simulated work and reports progress at each step,
    allowing the MCP Status Bar extension to display real-time progress
    in VS Code.

    Args:
        ctx: FastMCP context (automatically injected)
        duration: Total duration of work in seconds (default: 10)
        steps: Number of progress steps to report (default: 10)

    Returns:
        JSON with completion summary

    Example:
        >>> await cde_testProgressReporting(duration=15, steps=5)
        {"status": "success", "steps_completed": 5, "total_duration": 15}
    """
    await ctx.info(f"🧪 Starting progress test: {duration}s, {steps} steps")

    step_duration = duration / steps
    start_time = time.time()

    for step in range(steps + 1):
        percentage = step / steps
        message = f"Step {step}/{steps}"
        elapsed = time.time() - start_time

        # Send progress via HTTP POST directly to VS Code extension (port 8768)
        try:
            event = {
                "server": "CDE",
                "tool": "testProgressReporting",
                "percentage": percentage,
                "elapsed": elapsed,
                "message": message,
            }

            data = json.dumps(event).encode("utf-8")
            req = urllib.request.Request(
                "http://localhost:8768/progress",  # Changed from 8767 to 8768
                data=data,
                headers={"Content-Type": "application/json"},
            )

            try:
                response = urllib.request.urlopen(
                    req, timeout=5
                )  # Increased timeout to 5s
                response.read()
                response.close()
            except Exception as e:
                await ctx.info(f"⚠️ Failed to send progress to VS Code: {e}")
        except Exception:
            pass  # Silently continue if request fails

        # Simulate work (skip sleep on last step)
        if step < steps:
            await asyncio.sleep(step_duration)

    await ctx.info("✅ Progress test completed")

    # Return result
    return json.dumps(
        {
            "status": "success",
            "steps_completed": steps,
            "total_duration": f"{duration}s",
            "message": "Progress test completed successfully",
        },
        indent=2,
    )
