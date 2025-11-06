#!/usr/bin/env python3
"""
Jules Session Monitor - Track progress of parallel Jules sessions
"""

import subprocess
import json
import time
from datetime import datetime
from pathlib import Path

def run_command(cmd):
    """Run shell command and return output"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def get_sessions_status():
    """Get status of all Jules sessions"""
    output = run_command('jules remote list --session')
    if not output:
        return []

    lines = output.split('\n')
    if len(lines) < 2:
        return []

    sessions = []
    # Skip header line
    for line in lines[1:]:
        if line.strip() and not line.startswith(' '):
            # Find the last occurrence of status patterns
            line_clean = line.replace('\u00e2\u20ac\u00a6', '...')  # Replace ellipsis

            # Status is typically at the end: Planning, In Progress, Complete
            status = "Unknown"
            if "Planning" in line:
                status = "Planning"
            elif "In Progress" in line:
                status = "In Progress"
            elif "Complete" in line:
                status = "Complete"
            elif "Failed" in line:
                status = "Failed"

            # Extract ID (first field)
            parts = line_clean.split()
            if parts:
                session_id = parts[0]

                # Description is everything until we hit the repo pattern
                desc_parts = []
                repo_start = -1
                for i, part in enumerate(parts[1:], 1):
                    if part.startswith('iberi22/'):
                        repo_start = i
                        break
                    desc_parts.append(part)

                description = ' '.join(desc_parts)

                # If we found repo, extract remaining fields
                if repo_start >= 0:
                    remaining = parts[repo_start:]
                    if len(remaining) >= 3:
                        repo = remaining[0]
                        last_active = remaining[-2]
                        # status already extracted above
                    else:
                        repo = 'Unknown'
                        last_active = 'Unknown'
                else:
                    repo = 'Unknown'
                    last_active = 'Unknown'

                sessions.append({
                    'id': session_id,
                    'description': description,
                    'repo': repo,
                    'last_active': last_active,
                    'status': status
                })

    return sessions

def monitor_sessions():
    """Monitor Jules sessions and report progress"""
    print("🚀 Jules Session Monitor - CDE Orchestrator MCP")
    print("=" * 60)

    sessions = get_sessions_status()

    if not sessions:
        print("❌ No active sessions found")
        return

    # Group sessions by phase
    phases = {
        'PHASE 2': [],
        'PHASE 3': [],
        'PHASE 4': [],
        'PHASE 5': []
    }

    completed = 0
    in_progress = 0
    planning = 0

    for session in sessions:
        desc = session.get('description', '')
        status = session.get('status', 'Unknown')

        # Count status
        if status == 'Complete':
            completed += 1
        elif status == 'In Progress':
            in_progress += 1
        elif status == 'Planning':
            planning += 1

        # Group by phase
        for phase in phases:
            if phase in desc:
                phases[phase].append(session)
                break

    # Report summary
    print(f"📊 Session Summary:")
    print(f"   Planning: {planning}")
    print(f"   In Progress: {in_progress}")
    print(f"   Completed: {completed}")
    print(f"   Total: {len(sessions)}")
    print()

    # Report by phase
    for phase, phase_sessions in phases.items():
        if phase_sessions:
            print(f"🎯 {phase}: {len(phase_sessions)} sessions")
            for session in phase_sessions:
                status = session.get('status', 'Unknown')
                status_icon = {
                    'Planning': '📝',
                    'In Progress': '🔄',
                    'Complete': '✅',
                    'Failed': '❌'
                }.get(status, '❓')

                desc_short = session.get('description', '')[:60] + '...' if len(session.get('description', '')) > 60 else session.get('description', '')
                print(f"   {status_icon} {desc_short}")
            print()

    # Save to file
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_file = Path(".cde") / f"jules_monitor_{timestamp}.json"

    report = {
        'timestamp': timestamp,
        'summary': {
            'total_sessions': len(sessions),
            'planning': planning,
            'in_progress': in_progress,
            'completed': completed
        },
        'phases': phases,
        'sessions': sessions
    }

    report_file.parent.mkdir(exist_ok=True)
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"💾 Report saved to: {report_file}")

if __name__ == "__main__":
    monitor_sessions()