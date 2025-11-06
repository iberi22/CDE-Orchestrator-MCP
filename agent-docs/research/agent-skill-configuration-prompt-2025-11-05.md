---
title: "Agent Skill Configuration Prompt for Other Projects"
description: "Prompt template for configuring AI agent skills in other projects based on CDE Orchestrator learnings"
type: research
status: active
created: "2025-11-05"
updated: "2025-11-05"
author: "GitHub Copilot"
tags:
  - prompt
  - skills
  - configuration
  - agents
  - templates
llm_summary: |
  Reusable prompt for configuring AI agent skills in other projects.
  Based on CDE Orchestrator execution patterns and learnings.
  Includes CLI vs SDK decision framework and skill documentation templates.
---

# 🤖 Agent Skill Configuration Prompt

**For Other Projects: Configure AI Agent Skills Based on CDE Orchestrator Patterns**

## 🎯 Purpose

Use this prompt to configure AI agent skills in your project based on the successful patterns learned from the CDE Orchestrator MCP execution. This will help you:

- Choose between CLI tools and SDK/MCP approaches
- Document skills for reuse across your team
- Set up proper monitoring and orchestration
- Follow proven patterns for AI-assisted development

## 📋 Configuration Steps

### Step 1: Analyze Your Project Context

First, understand your project's AI tooling landscape:

```bash
# Check what AI tools are available in your environment
# List CLI tools
which claude-code || echo "Claude Code not found"
which gemini || echo "Gemini CLI not found"
which gh || echo "GitHub CLI not found"
which jules || echo "Jules not found"

# Check SDK availability
python -c "import boto3; print('AWS SDK available')" 2>/dev/null || echo "AWS SDK not available"
python -c "import google.generativeai; print('Google AI SDK available')" 2>/dev/null || echo "Google AI SDK not available"

# Check MCP server capability
# (Check if your project has MCP server setup)
```

### Step 2: Document Your Current Skills

Create a skill inventory based on your project's patterns:

```markdown
# Project Skills Inventory

## Current AI Tooling

### CLI Tools Available:
- [ ] Claude Code (Anthropic)
- [ ] Aider (OpenAI)
- [ ] Gemini CLI (Google)
- [ ] GitHub Copilot CLI
- [ ] Jules (Google)
- [ ] Other: __________

### SDK/MCP Integration:
- [ ] AWS Bedrock SDK
- [ ] Google AI SDK
- [ ] OpenAI SDK
- [ ] Custom MCP server
- [ ] Other: __________

### Current Usage Patterns:
- [ ] Interactive coding sessions
- [ ] Background research tasks
- [ ] Parallel development
- [ ] Batch processing
- [ ] Code suggestions
- [ ] Complex workflow orchestration
```

### Step 3: Apply Decision Framework

Use the CLI vs SDK decision rules learned from CDE execution:

#### For Each Task Type, Choose Primary Tool

| Task Type | Your Choice | Reasoning |
|-----------|-------------|-----------|
| Interactive Coding | [CLI/SDK] | _______________ |
| Parallel Development | [CLI/SDK] | _______________ |
| Background Research | [CLI/SDK] | _______________ |
| Batch Processing | [CLI/SDK] | _______________ |
| Code Suggestions | [CLI/SDK] | _______________ |
| Complex Workflows | [CLI/SDK] | _______________ |

#### Complexity-Based Selection

```python
def choose_tool_approach(task_description, estimated_hours):
    """
    Apply CDE-learned decision framework
    """
    if estimated_hours < 0.5:  # < 30 minutes
        return "CLI_TOOLS"
    elif estimated_hours <= 4:  # 30 min - 4 hours
        return "CLI_PLUS_MCP_ORCHESTRATION"
    elif estimated_hours <= 8:  # 4-8 hours
        return "JULES_PARALLEL_MCP"
    else:  # 8+ hours
        return "SDK_INTEGRATION"
```

### Step 4: Create Skill Documentation

For each skill you identify, create documentation following this template:

```markdown
# Skill: [Skill Name]

> **Capability**: [What this skill enables]
> **Use Case**: [When to apply this skill]
> **Status**: ✅ ACTIVE
> **Last Updated**: 2025-11-05

---

## Overview

[Brief description of the skill and its value]

## Prerequisites

- **[Tool Name]**: [Installation/setup requirements]
- **[Environment]**: [Required environment setup]
- **[Credentials]**: [Authentication requirements]

## Usage Patterns

### 1. [Primary Use Case]

```bash
# Example command or code
[your command here]
```

### 2. [Secondary Use Case]

```python
# Example integration
[your code here]
```

## Integration with Other Tools

- **Complements**: [Tools this works well with]
- **Conflicts**: [Tools to avoid combining]
- **Dependencies**: [Required companion tools]

## Success Metrics

- **Effectiveness**: [How to measure if this skill is working]
- **Efficiency**: [Time/complexity improvements]
- **Quality**: [Code/documentation improvements]

## Lessons Learned

[Key insights from applying this skill in your project]
```

### Step 5: Set Up Monitoring and Orchestration

Implement monitoring patterns from CDE execution:

```python
# Basic monitoring script template
def monitor_ai_usage():
    """
    Track AI tool usage and effectiveness
    Based on CDE Orchestrator monitoring patterns
    """
    # Track active sessions
    # Monitor completion rates
    # Measure time savings
    # Log integration points

# Background job management
def manage_background_jobs():
    """
    Handle long-running AI tasks
    Based on Gemini CLI background patterns
    """
    # Start background research
    # Monitor job status
    # Collect and integrate results
```

### Step 6: Configure Project-Specific Skills Directory

Set up your skill storage following CDE patterns:

```bash
# Create skills directory structure
mkdir -p .ai/skills/base
mkdir -p .ai/skills/ephemeral
mkdir -p .ai/monitoring
mkdir -p .ai/orchestration

# Create initial skill files
touch .ai/skills/base/project-specific-skill.md
touch .ai/monitoring/usage-tracker.py
touch .ai/orchestration/workflow-router.py
```

## 🛠️ Tool-Specific Configuration Examples

### Claude Code Configuration

```bash
# Install Claude Code
npm install -g @anthropic/claude-code

# Configure for your project
claude-code --init

# Create skill documentation
cat > .ai/skills/base/claude-interactive-coding.md << 'EOF'
# Skill: Claude Interactive Coding

> **Capability**: Real-time collaborative coding with Claude
> **Use Case**: Interactive development sessions
> **Status**: ✅ ACTIVE

## Usage
```bash
claude-code --model sonnet-3.5
```
EOF
```

### Jules Parallel Development

```bash
# If Jules is available in your environment
jules --help

# Create parallel development skill
cat > .ai/skills/base/jules-parallel-development.md << 'EOF'
# Skill: Jules Parallel Development

> **Capability**: Distribute complex tasks across multiple AI agents
> **Use Case**: Large refactoring, feature development
> **Status**: ✅ ACTIVE

## Usage
```bash
jules remote create --session "Feature implementation"
jules remote list --session
```
EOF
```

### AWS Bedrock SDK Integration

```python
# Create SDK skill for batch processing
bedrock_skill = """
# Skill: AWS Bedrock Batch Processing

> **Capability**: Large-scale content processing via AWS Bedrock
> **Use Case**: Batch analysis, content generation
> **Status**: ✅ ACTIVE

## Usage
```python
import boto3

bedrock = boto3.client('bedrock-runtime')
# Batch processing logic here
```
"""

with open('.ai/skills/base/aws-bedrock-batch.md', 'w') as f:
    f.write(bedrock_skill)
```

## 📊 Success Metrics to Track

### Quantitative Metrics
- **Time Savings**: Hours saved vs manual development
- **Completion Rate**: Tasks completed successfully with AI assistance
- **Error Reduction**: Fewer bugs introduced with AI assistance
- **Code Quality**: Improved metrics (complexity, coverage, etc.)

### Qualitative Metrics
- **Developer Satisfaction**: Team feedback on AI tooling
- **Learning Curve**: Time to become proficient with tools
- **Integration Friction**: Difficulties in combining tools
- **Maintenance Overhead**: Effort required to maintain AI configurations

## 🔄 Continuous Improvement

### Monthly Review Process
1. **Analyze Usage**: Review AI tool usage logs
2. **Assess Effectiveness**: Measure against success metrics
3. **Update Skills**: Add new patterns, retire obsolete ones
4. **Optimize Configuration**: Fine-tune tool parameters
5. **Document Learnings**: Update skill documentation

### Feedback Integration
```python
def collect_feedback():
    """
    Gather team feedback on AI tooling effectiveness
    """
    # Survey developers
    # Analyze usage patterns
    # Identify improvement opportunities
    # Update configurations
```

## 🚀 Quick Start Template

For immediate configuration in your project:

```bash
# 1. Set up directory structure
mkdir -p .ai/{skills/base,skills/ephemeral,monitoring,orchestration}

# 2. Create initial decision framework
cat > .ai/orchestration/tool-selector.py << 'EOF'
#!/usr/bin/env python3
"""
AI Tool Selection Framework
Based on CDE Orchestrator patterns
"""

def select_tool(task_description, complexity):
    """
    Choose appropriate AI tool based on task characteristics
    """
    tools = {
        'cli': ['claude-code', 'aider', 'gemini', 'gh-copilot'],
        'sdk': ['bedrock', 'openai', 'google-ai'],
        'mcp': ['custom-orchestrator']
    }

    if complexity == 'low':
        return tools['cli'][0]  # Default to first CLI tool
    elif complexity == 'high':
        return 'jules'  # Parallel execution
    else:
        return 'mcp-orchestration'  # Intelligent routing
EOF

# 3. Make executable
chmod +x .ai/orchestration/tool-selector.py

# 4. Create first skill
cat > .ai/skills/base/interactive-coding.md << 'EOF'
# Skill: Interactive Coding

> **Capability**: Real-time AI-assisted coding
> **Use Case**: Feature development, bug fixes
> **Status**: ✅ ACTIVE

## Primary Tools
1. Claude Code (if available)
2. Aider (fallback)
3. GitHub Copilot (IDE integration)

## Usage Pattern
```bash
# Try Claude Code first
claude-code --model sonnet-3.5

# Or use Aider
aider --model gpt-4

# Or IDE integration
# Use GitHub Copilot in your editor
```
EOF
```

## 📚 Reference Links

- **CDE Orchestrator Skills**: `.copilot/skills/` (if you have access)
- **CDE Decision Framework**: `agent-docs/research/model-usage-rules-cli-vs-sdk-2025-11-05.md`
- **MCP Tools Documentation**: `AGENTS.md`, `GEMINI.md`
- **Setup Guides**: `BEDROCK_SETUP.md`, `CONTRIBUTING.md`

## 🎯 Expected Outcomes

After following this configuration:

1. **Clear Tool Selection**: Team knows when to use CLI vs SDK
2. **Documented Skills**: Reusable knowledge across projects
3. **Monitoring**: Track AI tool effectiveness
4. **Continuous Improvement**: Regular optimization based on usage
5. **Knowledge Sharing**: Skills that transfer between team members

## 🔧 Troubleshooting

### Common Issues

**"No AI tools available"**
- Check installations: `which claude-code`, `python -c "import boto3"`
- Verify credentials and API keys
- Consider cloud-based alternatives

**"Tools not integrating well"**
- Use MCP orchestration layer
- Implement monitoring to identify conflicts
- Start with simpler combinations

**"Skills not being reused"**
- Ensure consistent documentation format
- Create centralized skill repository
- Regular team knowledge sharing sessions

---

**Remember**: Start simple, measure effectiveness, and iterate. The goal is to enhance development productivity while maintaining code quality and team knowledge.
