"""
Proof-of-Concept: Aider + AWS Bedrock Integration for CDE-Orchestrator-MCP

This module demonstrates the integration pattern for invoking Aider with AWS Bedrock
in the context of the CDE-Orchestrator-MCP project.
"""

import subprocess
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AiderBedrockAgent:
    """
    High-level agent for invoking Aider with AWS Bedrock backend.

    This agent abstracts the Bedrock + Aider integration for use with
    CDE-Orchestrator-MCP workflows.
    """

    # Configuration
    MODEL_ID = "anthropic.claude-sonnet-4-5-20250929-v1:0"
    BEDROCK_REGION = "us-east-1"
    BEDROCK_PROFILE = "bedrock"

    def __init__(self, project_path: str = "."):
        """
        Initialize Aider agent for a specific project.

        Args:
            project_path: Path to the project repository
        """
        self.project_path = Path(project_path).resolve()
        self.env = self._setup_environment()

        logger.info(f"Initialized AiderBedrockAgent for: {self.project_path}")

    def _setup_environment(self) -> Dict[str, str]:
        """Setup environment variables for Bedrock access."""
        env = os.environ.copy()
        env['AWS_REGION'] = self.BEDROCK_REGION
        env['AWS_PROFILE'] = self.BEDROCK_PROFILE
        return env

    def validate_setup(self) -> bool:
        """
        Validate that Aider and AWS credentials are properly configured.

        Returns:
            True if setup is valid, False otherwise
        """
        # Check Aider installation
        try:
            result = subprocess.run(
                ['aider', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                logger.error("Aider not found or not working")
                return False
            logger.info(f"Aider version: {result.stdout.strip()}")
        except FileNotFoundError:
            logger.error("Aider command not found. Install with: pip install aider-chat")
            return False

        # Check AWS credentials
        try:
            result = subprocess.run(
                ['aws', 'sts', 'get-caller-identity', '--profile', self.BEDROCK_PROFILE],
                capture_output=True,
                text=True,
                env=self.env,
                timeout=5
            )
            if result.returncode != 0:
                logger.error(f"AWS credentials invalid: {result.stderr}")
                return False

            identity = json.loads(result.stdout)
            logger.info(f"AWS Identity: {identity.get('Arn', 'Unknown')}")
        except Exception as e:
            logger.error(f"AWS credential check failed: {e}")
            return False

        # Check project is a git repository
        git_dir = self.project_path / '.git'
        if not git_dir.exists():
            logger.warning(f"Project is not a git repository: {self.project_path}")
            logger.info("Aider requires a git repository. Initialize with: git init")
            return False

        logger.info("Setup validation passed!")
        return True

    def start_interactive_session(self) -> int:
        """
        Start an interactive Aider session.

        Returns:
            Process exit code
        """
        logger.info(f"Starting interactive Aider session in {self.project_path}")

        cmd = [
            'aider',
            '--model', f'bedrock/{self.MODEL_ID}',
            str(self.project_path)
        ]

        logger.info(f"Command: {' '.join(cmd)}")

        process = subprocess.run(
            cmd,
            env=self.env,
            cwd=str(self.project_path)
        )

        return process.returncode

    def execute_task_non_interactive(self, prompt: str, auto_yes: bool = False) -> Dict[str, Any]:
        """
        Execute a development task in non-interactive mode.

        Args:
            prompt: User's development request
            auto_yes: Skip confirmation prompts

        Returns:
            Dictionary with status, output, and any errors
        """
        logger.info(f"Executing task (auto_yes={auto_yes}): {prompt}")

        cmd = [
            'aider',
            '--model', f'bedrock/{self.MODEL_ID}',
        ]

        if auto_yes:
            cmd.append('--yes')

        cmd.append(str(self.project_path))

        logger.info(f"Command: {' '.join(cmd)}")
        logger.info(f"Input prompt: {prompt}")

        try:
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=self.env,
                cwd=str(self.project_path)
            )

            # Send the prompt as input
            stdout, stderr = process.communicate(input=prompt, timeout=300)

            result = {
                'status': 'completed' if process.returncode == 0 else 'failed',
                'exit_code': process.returncode,
                'stdout': stdout,
                'stderr': stderr,
                'prompt': prompt
            }

            logger.info(f"Task completed with exit code: {process.returncode}")

            return result

        except subprocess.TimeoutExpired:
            logger.error("Task execution timed out (5 minutes)")
            process.kill()
            return {
                'status': 'timeout',
                'exit_code': -1,
                'error': 'Execution timed out after 5 minutes'
            }
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            return {
                'status': 'error',
                'exit_code': -1,
                'error': str(e)
            }

    def get_bedrock_models(self) -> Optional[list]:
        """
        List available Bedrock models.

        Returns:
            List of model summaries or None if failed
        """
        logger.info("Fetching available Bedrock models")

        try:
            result = subprocess.run(
                [
                    'aws', 'bedrock', 'list-foundation-models',
                    '--region', self.BEDROCK_REGION,
                    '--profile', self.BEDROCK_PROFILE
                ],
                capture_output=True,
                text=True,
                env=self.env,
                timeout=10
            )

            if result.returncode == 0:
                data = json.loads(result.stdout)
                models = data.get('modelSummaries', [])
                logger.info(f"Found {len(models)} models")
                return models
            else:
                logger.error(f"Failed to list models: {result.stderr}")
                return None

        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return None


# ============================================================================
# MCP INTEGRATION EXAMPLE
# ============================================================================

def create_mcp_tool_start_coding_session() -> Dict[str, Any]:
    """
    MCP tool definition for starting a coding session with Aider.

    This would be registered in the CDE-Orchestrator-MCP server.
    """
    return {
        "name": "cde_startCodingSession",
        "description": "Start an Aider coding session with AWS Bedrock backend",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to the project repository"
                },
                "prompt": {
                    "type": "string",
                    "description": "Initial development request/prompt"
                },
                "auto_yes": {
                    "type": "boolean",
                    "description": "Skip confirmation prompts (default: false)",
                    "default": False
                },
                "interactive": {
                    "type": "boolean",
                    "description": "Start interactive session vs non-interactive (default: false)",
                    "default": False
                }
            },
            "required": ["project_path", "prompt"]
        }
    }


def mcp_tool_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    MCP tool handler for starting coding sessions.

    This would be called by the CDE-Orchestrator-MCP server.
    """
    project_path = arguments.get("project_path", ".")
    prompt = arguments.get("prompt")
    auto_yes = arguments.get("auto_yes", False)
    interactive = arguments.get("interactive", False)

    if not prompt:
        return {
            "status": "error",
            "error": "prompt is required"
        }

    # Initialize agent
    agent = AiderBedrockAgent(project_path)

    # Validate setup
    if not agent.validate_setup():
        return {
            "status": "error",
            "error": "Setup validation failed. Check logs for details."
        }

    # Execute based on mode
    if interactive:
        logger.info("Starting interactive session...")
        exit_code = agent.start_interactive_session()
        return {
            "status": "completed",
            "mode": "interactive",
            "exit_code": exit_code
        }
    else:
        logger.info("Starting non-interactive task...")
        result = agent.execute_task_non_interactive(prompt, auto_yes=auto_yes)
        return result


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    import sys

    # Example 1: Validate setup
    print("=" * 60)
    print("Example 1: Validating Setup")
    print("=" * 60)
    agent = AiderBedrockAgent(".")
    is_valid = agent.validate_setup()
    print(f"Setup valid: {is_valid}\n")

    # Example 2: List available models
    print("=" * 60)
    print("Example 2: List Available Models")
    print("=" * 60)
    models = agent.get_bedrock_models()
    if models:
        print(f"Found {len(models)} models:")
        for model in models[:5]:  # Show first 5
            print(f"  - {model.get('modelId', 'Unknown')}")
        print()

    # Example 3: Non-interactive task
    print("=" * 60)
    print("Example 3: Execute Non-Interactive Task")
    print("=" * 60)
    result = agent.execute_task_non_interactive(
        "Create a simple Python function that adds two numbers",
        auto_yes=True
    )
    print(f"Status: {result['status']}")
    print(f"Exit Code: {result['exit_code']}")
    if result.get('stdout'):
        print(f"Output preview: {result['stdout'][:200]}...")
    print()

    # Example 4: MCP Tool Integration
    print("=" * 60)
    print("Example 4: MCP Tool Definition")
    print("=" * 60)
    tool_def = create_mcp_tool_start_coding_session()
    print(json.dumps(tool_def, indent=2))
