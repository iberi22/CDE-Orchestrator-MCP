---
title: "HARCOS Organization Setup Guide"
description: "Complete setup guide for migrating CDE Orchestrator to HARCOS-AI GitHub organization with unified branding, Fair Source licensing, and enterprise services"
type: "guide"
status: "active"
created: "2025-11-05"
updated: "2025-11-05"
author: "GitHub Copilot Agent"
llm_summary: |
  Step-by-step guide for creating HARCOS-AI organization, registering GitHub org, transferring repositories,
  applying Fair Source License, and setting up unified sponsorship and enterprise services infrastructure.
  Includes CLI commands, documentation templates, and branding guidelines.
---

# HARCOS Organization Setup Guide

> **HARCOS — Human-AI Research Community Open Source**
> "Open tools for symbiotic intelligence"

---

## 🎯 Setup Overview

This guide walks through creating the HARCOS-AI GitHub organization and migrating CDE Orchestrator MCP as the first project.

**Setup Time Estimate**: 1-2 hours (mostly waiting for GitHub to process organization creation)

**Prerequisites**:
- GitHub account with organization creation permission
- GitHub CLI installed (`gh --version` to verify)
- Git installed
- Admin access to current iberi22/CDE-Orchestrator-MCP repository

---

## 📋 Phase 1: GitHub Organization Creation (15 minutes)

### Step 1.1: Create GitHub Organization

**Option A: Via Web UI (Recommended for first-time)**

1. Navigate to: https://github.com/organizations/new
2. Fill in:
   - **Organization name**: `HARCOS-AI` (or `HARCOS` if preferred)
   - **Billing email**: Your email
   - **Organization website**: `https://harcos.ai` (placeholder for now)
   - **Organization description**: "Human-AI Research Community Open Source"
   - **Location**: Your location
3. Click "Create organization"
4. Choose free plan (can upgrade later)
5. Add members (if applicable)

**Option B: Via GitHub CLI**

```bash
# Not yet available via CLI, use web UI
# But verify organization was created:
gh org view HARCOS-AI
```

### Step 1.2: Verify Organization

```bash
# List organizations you own
gh org list --owner

# View organization details
gh org view HARCOS-AI --json name,description,websiteUrl
```

### Step 1.3: Configure Organization Settings

Navigate to: https://github.com/organizations/HARCOS-AI/settings

**Configure**:
- [ ] General → Base permissions: "Read"
- [ ] Member privileges → Allow forking: Enabled
- [ ] Member privileges → Allow repo creation: Enabled
- [ ] Billing → Free plan (upgrade later if needed)
- [ ] Security → Require 2FA for members: Optional now, enable later

---

## 📋 Phase 2: Repository Transfer (20 minutes)

### Step 2.1: Transfer CDE Orchestrator to Organization

**Via Web UI (Recommended)**:

1. Navigate to: https://github.com/iberi22/CDE-Orchestrator-MCP/settings
2. Scroll to **"Transfer ownership"** section
3. Enter: `HARCOS-AI` as new owner
4. Click "Transfer"
5. Confirm ownership transfer

**Via GitHub CLI**:

```bash
# Not directly available, use web UI
# After transfer, verify:
gh repo view HARCOS-AI/CDE-Orchestrator-MCP
```

### Step 2.2: Verify Transfer

```bash
# List repositories in HARCOS-AI organization
gh repo list HARCOS-AI

# View specific repo
gh repo view HARCOS-AI/CDE-Orchestrator-MCP --json name,description,owner
```

### Step 2.3: Update Local Repository Remote

After transfer, update your local clone:

```bash
# Check current remote
git remote -v

# Update remote URL
git remote set-url origin https://github.com/HARCOS-AI/CDE-Orchestrator-MCP.git

# Verify
git remote -v
# Should show: https://github.com/HARCOS-AI/CDE-Orchestrator-MCP.git
```

---

## 📋 Phase 3: Create Additional Repositories (20 minutes)

### Step 3.1: Create Repository Structure

Create these repositories in HARCOS-AI organization:

```bash
# Create each repository
gh repo create HARCOS-AI/Agent-Framework \
  --private \
  --description "Multi-agent orchestration framework for AI systems" \
  --template iberi22/CDE-Orchestrator-MCP \
  --org HARCOS-AI

gh repo create HARCOS-AI/LLM-Eval-Toolkit \
  --private \
  --description "Comprehensive toolkit for evaluating LLM agent capabilities" \
  --org HARCOS-AI

gh repo create HARCOS-AI/docs \
  --public \
  --description "Unified documentation for HARCOS projects" \
  --org HARCOS-AI

gh repo create HARCOS-AI/enterprise \
  --private \
  --description "Enterprise services and managed deployment configuration" \
  --org HARCOS-AI
```

### Step 3.2: Verify Repository Creation

```bash
# List all repos in organization
gh repo list HARCOS-AI --limit 10
```

---

## 📋 Phase 4: Apply Fair Source License to All Repos (30 minutes)

### Step 4.1: Copy License Files to All Repos

For each repository (CDE-Orchestrator-MCP, Agent-Framework, LLM-Eval-Toolkit):

```bash
# Clone each repo
gh repo clone HARCOS-AI/CDE-Orchestrator-MCP
cd CDE-Orchestrator-MCP

# Copy LICENSE and FUNDING.yml from CDE-Orchestrator-MCP
# (They should already exist in CDE repo)

# Commit and push
git add LICENSE .github/FUNDING.yml
git commit -m "chore: apply Fair Source License and unified funding"
git push origin main

# Repeat for other repos...
```

### Step 4.2: Verify License in All Repos

```bash
# Check each repo has LICENSE file
for repo in CDE-Orchestrator-MCP Agent-Framework LLM-Eval-Toolkit; do
  echo "=== $repo ==="
  gh repo view HARCOS-AI/$repo --json licenseInfo
done
```

---

## 📋 Phase 5: Set Up Unified Sponsorship (20 minutes)

### Step 5.1: Create Organization Sponsorship Profile

1. Navigate to: https://github.com/sponsors/HARCOS-AI (if organization has GitHub Sponsors)
2. Set up organization sponsorship (may require business account)

### Step 5.2: Copy SPONSORS.md to All Repos

```bash
# In each repo, create or update .github/SPONSORS.md
# Content should reference the unified organization sponsorship

cat > .github/SPONSORS.md << 'EOF'
# Support HARCOS Projects

HARCOS is a Human-AI Research Community dedicated to open-source AI orchestration tools.

## Sponsorship Tiers

All contributions support the entire HARCOS ecosystem:

| Tier | Amount | Benefits |
|------|--------|----------|
| Supporter | $5+/mo | ❤️ Badge on all READMEs |
| Contributor | $25+/mo | 🌟 Priority support + early access |
| Partner | $50+/mo | 🚀 Logo on website + co-marketing |
| Sponsor | $100+/mo | 💎 Dedicated support + roadmap influence |
| Enterprise | Custom | 🏢 SLA, custom features, consulting |

**Support us on:**
- [GitHub Sponsors](https://github.com/sponsors/HARCOS-AI)
- [Open Collective](https://opencollective.com/harcos-ai)

**100% voluntary. No feature gating. All funds support AI research, accessibility, and open-source sustainability.**

For enterprise services, contact: [enterprise@harcos.ai](mailto:enterprise@harcos.ai)
EOF

git add .github/SPONSORS.md
git commit -m "docs: add unified HARCOS sponsorship tiers"
git push origin main
```

---

## 📋 Phase 6: Create Organization README (25 minutes)

### Step 6.1: Create Main Organization README

```bash
# Clone the organization docs repository
gh repo clone HARCOS-AI/docs
cd docs

# Create main README
cat > README.md << 'EOF'
---
title: "HARCOS — Human-AI Research Community Open Source"
description: "Open tools for symbiotic intelligence"
type: "guide"
status: "active"
created: "2025-11-05"
updated: "2025-11-05"
author: "HARCOS Team"
---

# 🤖 HARCOS — Human-AI Research Community Open Source

> **Tagline:** "Open tools for symbiotic intelligence"

HARCOS is a GitHub organization dedicated to building **open-source, community-driven tools** for human-AI collaboration and research.

## 🎯 Mission

Develop **transparent, accessible, and powerful AI orchestration tools** that empower researchers, developers, and organizations to build better AI systems through open-source collaboration.

## 🔍 Core Values

1. **Openness**: 100% source code accessible, AI-friendly
2. **Accessibility**: Free for all (personal, educational, commercial)
3. **Community**: Built with and for the community
4. **Ethics**: Transparent monetization, voluntary support
5. **Research**: Advancing AI through collaborative innovation

## 📦 Projects

### 🎼 [CDE Orchestrator MCP](https://github.com/HARCOS-AI/CDE-Orchestrator-MCP)
**Context-Driven Engineering for AI-powered development**

The reference implementation of CDE methodology for structured, phase-based software development with built-in research and continuous improvement.

- Python 3.14+ FastMCP server
- 309/312 tests passing (97% coverage)
- Fair Source License 1.0
- Enterprise services available

### 🤖 [Agent Framework](https://github.com/HARCOS-AI/Agent-Framework) (Coming Soon)
**Multi-agent orchestration for AI systems**

Unified framework for managing multiple AI agents (Claude, GPT, Gemini) with shared context and coordinated workflows.

### 📊 [LLM Eval Toolkit](https://github.com/HARCOS-AI/LLM-Eval-Toolkit) (Coming Soon)
**Comprehensive LLM evaluation and benchmarking**

Toolkit for evaluating LLM agent capabilities, benchmarking against baselines, and continuous improvement tracking.

## 🚀 Getting Started

### Use CDE Orchestrator

```bash
git clone https://github.com/HARCOS-AI/CDE-Orchestrator-MCP.git
cd CDE-Orchestrator-MCP
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .[dev]
python src/server.py
```

See [CDE Quick Start](https://github.com/HARCOS-AI/CDE-Orchestrator-MCP#quick-start) for details.

### Contribute

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 💰 Support This Mission

HARCOS is funded by the community. If our tools help your organization:

| Tier | Contribution | Benefits |
|------|--------------|----------|
| **Supporter** | $5+/mo | Badge on all READMEs |
| **Contributor** | $25+/mo | Priority support |
| **Partner** | $50+/mo | Logo + co-marketing |
| **Sponsor** | $100+/mo | Dedicated support |
| **Enterprise** | Custom | SLA, features, consulting |

**100% voluntary. All funds support research, accessibility, and open-source sustainability.**

- [GitHub Sponsors](https://github.com/sponsors/HARCOS-AI)
- [Open Collective](https://opencollective.com/harcos-ai)

## 🏢 Enterprise Services

Need managed cloud hosting, 24×7 support, or dedicated infrastructure?

**HARCOS Enterprise offers:**
- ✅ Managed cloud deployment (AWS/GCP/Azure)
- ✅ 24×7 premium support with SLA
- ✅ Dedicated infrastructure & RAG/embeddings services
- ✅ Custom integrations & consulting
- ✅ Team training & onboarding

📧 **Contact:** [enterprise@harcos.ai](mailto:enterprise@harcos.ai)

## 📚 Documentation

- [CDE Orchestrator Docs](https://github.com/HARCOS-AI/CDE-Orchestrator-MCP/docs)
- [Architecture Guide](https://github.com/HARCOS-AI/CDE-Orchestrator-MCP/specs/design/ARCHITECTURE.md)
- [Contributing Guide](CONTRIBUTING.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)

## 📊 Project Status

| Project | Status | Stars | Tests | License |
|---------|--------|-------|-------|---------|
| CDE Orchestrator MCP | ✅ Active | TBD | 309/312 | Fair Source 1.0 |
| Agent Framework | 🔜 Coming | — | — | Fair Source 1.0 |
| LLM Eval Toolkit | 🔜 Coming | — | — | Fair Source 1.0 |

## 🤝 Community

- **GitHub Issues**: Ask questions, report bugs, suggest features
- **GitHub Discussions**: Join conversations and share ideas
- **Discord** (coming soon): Real-time community chat
- **Twitter/X**: [@HARCOS_AI](https://twitter.com/harcos_ai) (coming soon)

## 📜 License

All HARCOS projects are licensed under **Fair Source License 1.0**:
- ✅ 100% free for all (personal, educational, commercial)
- 💚 Voluntary contributions encouraged
- 🌍 All derivatives must remain open source
- 🤖 Must remain accessible to LLM models

See [LICENSE](LICENSE) for complete terms.

## 🎓 Acknowledgments

HARCOS is built on the shoulders of giants in open-source and AI research. We thank:
- OpenAI, Anthropic, Google for advancing AI
- GitHub for providing infrastructure
- All open-source contributors worldwide

## 📝 Citation

If you use HARCOS projects in your research, please cite:

```bibtex
@software{harcos2025,
  author = {HARCOS Contributors},
  title = {HARCOS: Human-AI Research Community Open Source},
  url = {https://github.com/HARCOS-AI},
  year = {2025}
}
```

---

**Built with ❤️ by the HARCOS Community**

© 2025 HARCOS Contributors. Licensed under Fair Source License 1.0.
EOF

git add README.md
git commit -m "docs: create HARCOS organization README"
git push origin main
```

---

## 📋 Phase 7: Create Contributing and CoC Files (20 minutes)

### Step 7.1: Create CONTRIBUTING.md

```bash
cat > CONTRIBUTING.md << 'EOF'
# Contributing to HARCOS

Thank you for your interest in contributing to HARCOS! We welcome contributions from everyone.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/PROJECT.git`
3. Create a feature branch: `git checkout -b feature/your-feature`
4. Make your changes
5. Write or update tests
6. Submit a pull request

## Code Standards

- Python: Follow PEP 8 (enforced by `black`, `ruff`)
- Git commits: Use [Conventional Commits](https://www.conventionalcommits.org/)
- Documentation: Keep docstrings and README up to date
- Tests: Aim for >80% coverage

## Pull Request Process

1. Update tests and documentation
2. Ensure all tests pass: `pytest tests/ -v`
3. Check code style: `black src/ --check`, `ruff check src/`
4. Keep PR focused on one feature/fix
5. Write clear PR description explaining the change

## Reporting Issues

- Use GitHub Issues for bug reports
- Provide minimal reproduction case
- Include Python version, OS, and dependency versions

## Code of Conduct

By participating, you agree to uphold our [Code of Conduct](CODE_OF_CONDUCT.md).

---

Questions? Open an issue or join our community discussions!
EOF

git add CONTRIBUTING.md
git commit -m "docs: add CONTRIBUTING guidelines"
git push origin main
```

### Step 7.2: Create CODE_OF_CONDUCT.md

```bash
cat > CODE_OF_CONDUCT.md << 'EOF'
# Contributor Code of Conduct

## Our Pledge

We are committed to providing a welcoming and inspiring community for all. We pledge that everyone participating in the HARCOS community will treat each other with respect and dignity.

## Standards

Examples of behavior that contributes to a positive environment include:
- Being respectful of differing opinions, viewpoints, and experiences
- Giving and gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

Examples of unacceptable behavior include:
- Harassment or discrimination
- Personal attacks or trolling
- Public or private harassment
- Publishing others' private information without permission

## Enforcement

Instances of unacceptable behavior can be reported to the community leaders. All complaints will be reviewed and investigated.

---

This Code of Conduct is adapted from the [Contributor Covenant](https://www.contributor-covenant.org/).
EOF

git add CODE_OF_CONDUCT.md
git commit -m "docs: add Code of Conduct"
git push origin main
```

---

## 📋 Phase 8: Create Organization Settings (15 minutes)

### Step 8.1: Configure GitHub Organization Settings

Navigate to: https://github.com/organizations/HARCOS-AI/settings

**Configure**:

1. **Profile**
   - [ ] Organization name: HARCOS-AI
   - [ ] Display name: HARCOS
   - [ ] Description: "Human-AI Research Community Open Source"
   - [ ] Website: https://harcos.ai (placeholder)
   - [ ] Location: Your location
   - [ ] Email: contact@harcos.ai (if available)

2. **Member Privileges**
   - [ ] Base permissions: "Read"
   - [ ] Allow forking: Enabled
   - [ ] Allow repo creation: Enabled
   - [ ] Allow outside collaborators: Enabled

3. **Security**
   - [ ] 2FA requirement: Optional for now
   - [ ] Personal access tokens: Review settings later

4. **Billing** (if upgrading)
   - [ ] Choose plan based on team size

### Step 8.2: Create Teams (Optional, but Recommended)

```bash
# Create teams for organization
gh api --method POST /orgs/HARCOS-AI/teams \
  -f name='Maintainers' \
  -f description='CDE Orchestrator maintainers' \
  -f privacy='closed'

gh api --method POST /orgs/HARCOS-AI/teams \
  -f name='Contributors' \
  -f description='Active contributors' \
  -f privacy='closed'

gh api --method POST /orgs/HARCOS-AI/teams \
  -f name='Enterprise' \
  -f description='Enterprise services team' \
  -f privacy='closed'
```

---

## 📋 Phase 9: Update CDE Repository (10 minutes)

### Step 9.1: Update README URLs

In `HARCOS-AI/CDE-Orchestrator-MCP/README.md`:

```bash
# Replace old URLs with new organization URLs
sed -i 's|iberi22/CDE-Orchestrator-MCP|HARCOS-AI/CDE-Orchestrator-MCP|g' README.md

# Example replacements:
# https://github.com/iberi22/CDE-Orchestrator-MCP → https://github.com/HARCOS-AI/CDE-Orchestrator-MCP
# https://codecov.io/gh/iberi22/CDE-Orchestrator-MCP → https://codecov.io/gh/HARCOS-AI/CDE-Orchestrator-MCP
```

### Step 9.2: Add Organization Header to README

Add to the top of README (after frontmatter):

```markdown
## 🏢 Part of HARCOS

This project is part of the **[HARCOS](https://github.com/HARCOS-AI)** (Human-AI Research Community Open Source) initiative.

See [HARCOS Organization](https://github.com/HARCOS-AI) for other projects and organization-wide information.
```

---

## 🚀 Post-Setup Tasks (Optional, For Later)

- [ ] Set up continuous integration badges in README
- [ ] Create organization website/landing page (harcos.ai domain)
- [ ] Set up GitHub Sponsors organization profile
- [ ] Create Open Collective page for HARCOS
- [ ] Configure CNAME for GitHub Pages
- [ ] Add organization to GitHub topics and trending lists
- [ ] Announce organization on Twitter, Reddit, HN
- [ ] Create Discord server for community

---

## 📞 Support

If you run into issues during setup:

1. Check [GitHub Organization Documentation](https://docs.github.com/en/organizations)
2. Review GitHub CLI help: `gh repo create --help`
3. Open a GitHub issue in the CDE repository

---

**Setup completed! Welcome to HARCOS! 🚀**

Next steps:
1. Configure CI/CD pipelines (GitHub Actions)
2. Set up org website with landing page
3. Start promoting HARCOS to the community
4. Begin work on Agent Framework and LLM Eval Toolkit

---

© 2025 HARCOS Contributors. Licensed under Fair Source License 1.0.
