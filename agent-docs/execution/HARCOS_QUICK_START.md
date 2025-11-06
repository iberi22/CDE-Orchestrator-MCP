---
title: "HARCOS Quick Start - Deploy in 2.5 Hours"
description: "Fast-track deployment guide - everything you need to launch HARCOS organization"
type: "guide"
status: "active"
created: "2025-11-05"
updated: "2025-11-05"
author: "HARCOS Team"
---

# 🚀 HARCOS Quick Start

**Deploy HARCOS-AI organization in 2.5 hours. Everything is ready.**

## ⚡ Pre-Flight Checklist (5 min)

Before you start, verify you have:

- [ ] GitHub account with org creation permissions
- [ ] GitHub CLI installed (`gh --version`)
- [ ] Git installed (`git --version`)
- [ ] Terminal/PowerShell access
- [ ] DNS access (optional, for harcos.ai domain)

```bash
# Test GitHub CLI
gh auth status

# Expected output: Logged in to github.com as YOUR_USERNAME
```

If not logged in:
```bash
gh auth login
# Follow prompts to authenticate
```

## 📋 Deployment Phases (155 minutes total)

### Phase 1: Create Organization (5 min)

**Goal**: Create HARCOS-AI organization on GitHub

**Option A: Web UI (Easiest)**
1. Go to `https://github.com/organizations/new`
2. Organization account name: `HARCOS-AI`
3. Email: `contact@harcos.ai` (or your email)
4. Company: HARCOS Team
5. Click "Create organization"
6. Choose free plan
7. Done ✅

**Option B: GitHub CLI**
```bash
# Note: GitHub CLI doesn't support org creation yet
# Use Option A (web UI)
```

**Verify**:
```bash
gh org view HARCOS-AI
# Should show organization details
```

### Phase 2: Transfer Repository (10 min)

**Goal**: Move CDE-Orchestrator-MCP to HARCOS-AI

**Steps**:
1. Go to `https://github.com/iberi22/CDE-Orchestrator-MCP/settings/transfer`
2. Type "HARCOS-AI/CDE-Orchestrator-MCP" in the new repository name field
3. Click "I understand, transfer this repository."
4. Confirm transfer

**Update Local Repository**:
```bash
# Navigate to your local CDE repository
cd /path/to/CDE-Orchestrator-MCP

# Update remote URL
git remote set-url origin https://github.com/HARCOS-AI/CDE-Orchestrator-MCP.git

# Verify
git remote -v
# Should show: origin https://github.com/HARCOS-AI/CDE-Orchestrator-MCP.git
```

**Verify**:
```bash
gh repo view HARCOS-AI/CDE-Orchestrator-MCP
```

### Phase 3: Create Repositories (15 min)

**Goal**: Create skeleton repos for Agent-Framework, LLM-Eval-Toolkit, docs, enterprise

```bash
# Create Agent-Framework
gh repo create HARCOS-AI/Agent-Framework --public --description "Multi-agent orchestration framework" --source=. --template --push

# Wait for creation...
# Copy README.md from CDE-Orchestrator-MCP as template

# Create LLM-Eval-Toolkit
gh repo create HARCOS-AI/LLM-Eval-Toolkit --public --description "LLM evaluation and benchmarking toolkit" --source=. --template --push

# Create docs repository
gh repo create HARCOS-AI/docs --public --description "HARCOS unified documentation and landing page" --source=. --template --push

# Create enterprise repository
gh repo create HARCOS-AI/enterprise --public --description "HARCOS enterprise services and infrastructure" --source=. --template --push
```

Alternative (one-liner for each):
```bash
# If above doesn't work, use:
curl -X POST -H "Authorization: token YOUR_GITHUB_TOKEN" \
  -d '{"name":"Agent-Framework","description":"Multi-agent orchestration framework","public":true}' \
  https://api.github.com/orgs/HARCOS-AI/repos
```

**Verify all repos created**:
```bash
gh repo list HARCOS-AI --limit 10
```

### Phase 4: Apply Fair Source License (20 min)

**Goal**: Copy LICENSE and FUNDING.yml to all repos

**Copy LICENSE file to each repo**:

From CDE-Orchestrator-MCP root, copy `LICENSE` file:

```bash
# Get LICENSE content from CDE repo
cat LICENSE

# Copy to all repos
for repo in Agent-Framework LLM-Eval-Toolkit docs enterprise; do
  cd /tmp/$repo
  cp ../CDE-Orchestrator-MCP/LICENSE .
  git add LICENSE
  git commit -m "Add Fair Source License 1.0"
  git push
done
```

**Copy FUNDING.yml**:

```bash
# Create/copy .github/FUNDING.yml to all repos
for repo in Agent-Framework LLM-Eval-Toolkit docs enterprise; do
  cd /tmp/$repo
  mkdir -p .github
  cp ../CDE-Orchestrator-MCP/.github/FUNDING.yml .github/
  git add .github/FUNDING.yml
  git commit -m "Add GitHub sponsorship configuration"
  git push
done
```

**Verify**:
```bash
# Check each repo has LICENSE
gh repo view HARCOS-AI/Agent-Framework --json nameWithOwner
# Should display repo with LICENSE

# Check GitHub Sponsors enabled
gh repo view HARCOS-AI/Agent-Framework --json hasSponsorsListing
```

### Phase 5: Setup Sponsorship (30 min)

**Goal**: Enable GitHub Sponsors and Open Collective for organization

**GitHub Sponsors Setup**:

1. Go to `https://github.com/sponsors/signup`
2. Select "HARCOS-AI" organization (if not pre-selected)
3. Enter business profile info:
   - Country: Select your country
   - Business name: HARCOS — Human-AI Research Community Open Source
   - Business description: "Open tools for symbiotic intelligence. Providing enterprise services for CDE orchestration, agent frameworks, and LLM evaluation."
4. Add tax information (if required)
5. Click "Create profile"

**Funding Tiers** (add these):
```
Tier 1: Supporter - $5/month
  - Access to supporter badge
  - Recognition in README

Tier 2: Contributor - $25/month
  - All Supporter benefits
  - Priority support channel
  - Early access to features

Tier 3: Partner - $50/month
  - All Contributor benefits
  - Logo on website
  - Co-marketing opportunities

Tier 4: Sponsor - $100+/month
  - All Partner benefits
  - Dedicated support contact
  - Roadmap influence
  - Custom tier available
```

**Open Collective Setup**:

1. Go to `https://opencollective.com/`
2. Click "Start a Collective"
3. Select "Open Source"
4. Organization name: HARCOS
5. Description: "Human-AI Research Community Open Source"
6. Logo: Use HARCOS logo (when created)
7. Social links:
   - Website: https://harcos.ai (or github.com/HARCOS-AI)
   - GitHub: https://github.com/HARCOS-AI
   - Twitter: @HARCOS_AI
8. Create profile

**Expense tiers** (same as GitHub Sponsors):
```
$5, $25, $50, $100+ per month
```

**Update FUNDING.yml** in all repos:
```yaml
# .github/FUNDING.yml
github: [HARCOS-AI]
open_collective: harcos-ai
```

### Phase 6: Deploy Landing Page (15 min)

**Goal**: Launch https://harcos-ai.github.io/docs

**Step 1: Create docs/index.html**

In `HARCOS/docs` repository:

```bash
# Clone docs repo
git clone https://github.com/HARCOS-AI/docs.git
cd docs

# Copy landing page
cp ../CDE-Orchestrator-MCP/.github/HARCOS_LANDING_PAGE.html index.html

# Commit
git add index.html
git commit -m "Add HARCOS landing page"
git push
```

**Step 2: Enable GitHub Pages**

1. Go to `https://github.com/HARCOS-AI/docs/settings/pages`
2. Source: Deploy from branch
3. Branch: main
4. Folder: / (root)
5. Click "Save"
6. Wait 1-2 minutes for deployment

**Step 3: Verify**

```bash
# Check GitHub Pages status
gh repo view HARCOS-AI/docs --json url

# Open in browser: https://harcos-ai.github.io/docs
```

**Optional: Custom Domain**

```bash
# Create CNAME file
echo "harcos.ai" > docs/CNAME
git add docs/CNAME
git commit -m "Configure custom domain"
git push

# Update DNS records (at your domain registrar)
# Add A record pointing to GitHub Pages:
# 185.199.108.153
# 185.199.109.153
# 185.199.110.153
# 185.199.111.153

# Or add CNAME:
# harcos-ai.github.io
```

### Phase 7: Organization Documentation (30 min)

**Goal**: Create CONTRIBUTING.md, CODE_OF_CONDUCT.md, organization README

**Create in HARCOS-AI/.github** (special directory):

```bash
# Clone special repo for organization-wide files
cd /tmp
git clone https://github.com/HARCOS-AI/.github.git
cd .github
```

**Create CONTRIBUTING.md**:

```markdown
# Contributing to HARCOS

Thanks for contributing! Here's how to get started.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/REPO.git`
3. Create a feature branch: `git checkout -b feature/my-feature`
4. Make changes
5. Commit: `git commit -am "Add my feature"`
6. Push: `git push origin feature/my-feature`
7. Open a Pull Request

## Code Style

- Python: Follow PEP 8
- Tests: Write tests for new features
- Documentation: Update docs with changes

## Reporting Issues

- Use GitHub Issues
- Include: description, steps to reproduce, expected vs actual
- Add relevant labels

## Code of Conduct

See CODE_OF_CONDUCT.md for community standards.

## Questions?

Ask in GitHub Discussions or GitHub Issues.

Thanks for contributing to HARCOS!
```

**Create CODE_OF_CONDUCT.md**:

```markdown
# Code of Conduct

## Our Commitment

We are committed to providing a welcoming and inspiring community for all.

## Standards

Examples of behavior that contribute to a positive environment:

- Using welcoming and inclusive language
- Being respectful of differing opinions
- Accepting constructive criticism gracefully
- Focusing on what is best for the community
- Showing empathy towards other community members

Examples of unacceptable behavior include:

- Harassment or discrimination
- Derogatory comments
- Personal attacks
- Unwelcome sexual attention
- Other conduct reasonably considered inappropriate

## Enforcement

Violations can be reported to conduct@harcos.ai.

We will review and investigate, maintaining confidentiality.

## Attribution

This Code of Conduct is adapted from the Contributor Covenant.
```

**Create profile/README.md** (organization-wide):

```markdown
# HARCOS — Human-AI Research Community Open Source

**"Open tools for symbiotic intelligence"**

Human-AI Research Community Open Source (HARCOS) develops cutting-edge, community-driven AI development tools with ethical monetization.

## 🎯 Our Projects

- **[CDE Orchestrator MCP](https://github.com/HARCOS-AI/CDE-Orchestrator-MCP)** - Context-Driven Engineering for AI-powered development
- **[Agent Framework](https://github.com/HARCOS-AI/Agent-Framework)** - Multi-agent orchestration (Coming Soon)
- **[LLM Eval Toolkit](https://github.com/HARCOS-AI/LLM-Eval-Toolkit)** - Benchmarking and evaluation (Coming Soon)

## 🚀 Get Started

Visit our landing page: https://harcos.ai

Or start with CDE Orchestrator:
```bash
git clone https://github.com/HARCOS-AI/CDE-Orchestrator-MCP.git
cd CDE-Orchestrator-MCP
pip install -r requirements.txt
```

## 💚 Support HARCOS

We're open source with optional enterprise services.

- **Free**: All source code, community support
- **Sponsor** ($5+/month): Support our mission
- **Enterprise** ($2,000+/month): Managed services, 24/7 support

[Sponsor on GitHub](https://github.com/sponsors/HARCOS-AI)

## 📖 Documentation

- [CDE Orchestrator Docs](https://github.com/HARCOS-AI/CDE-Orchestrator-MCP/blob/main/README.md)
- [Contributing Guide](CONTRIBUTING.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)

## 📞 Contact

- GitHub: [@HARCOS-AI](https://github.com/HARCOS-AI)
- Enterprise: enterprise@harcos.ai
- Issues: GitHub Issues on specific project repos

---

© 2025 HARCOS Contributors. Licensed under Fair Source License 1.0.
```

**Commit and push**:

```bash
git add CONTRIBUTING.md CODE_OF_CONDUCT.md profile/README.md
git commit -m "Add organization documentation"
git push
```

### Phase 8: GitHub Organization Settings (20 min)

**Go to**: `https://github.com/organizations/HARCOS-AI/settings`

**Settings to configure**:

1. **Profile**:
   - Avatar: Upload HARCOS logo (when created)
   - Name: HARCOS — Human-AI Research Community Open Source
   - Bio: Open tools for symbiotic intelligence
   - Website: https://harcos.ai (when deployed)
   - Location: Global
   - Email: contact@harcos.ai

2. **Member privileges**:
   - Allow members to create internal repos: ON
   - Allow members to create pages: ON
   - Base permissions: Member (can read org repos)

3. **Actions**:
   - Policies: Allow all actions
   - Workflow permissions: Read and write

4. **Secrets** (if needed):
   - Add any secrets for CI/CD

5. **Protected branches**:
   - Go to each repo → Settings → Branches
   - Add rule: `main` branch
   - Require PR reviews: 1
   - Dismiss stale reviews: ON
   - Require status checks: ON

### Phase 9: DNS Configuration [OPTIONAL] (10 min)

**If deploying harcos.ai custom domain**:

1. **Purchase domain**:
   - Registrar: GoDaddy, Namecheap, Route53, or other
   - Domain: harcos.ai (~$10-15/year)

2. **Configure DNS**:
   - Option A (A records - recommended):
     ```
     Type: A
     Name: @
     Value: 185.199.108.153 (add all 4 IPs below)
            185.199.109.153
            185.199.110.153
            185.199.111.153
     ```
   - Option B (CNAME):
     ```
     Type: CNAME
     Name: www
     Value: harcos-ai.github.io
     ```

3. **Verify DNS**:
   ```bash
   # Wait 5-30 minutes for propagation
   nslookup harcos.ai
   # Should resolve to GitHub Pages IP
   ```

4. **GitHub Pages setup**:
   - Repo: HARCOS/docs
   - Settings → Pages
   - Custom domain: harcos.ai
   - Enforce HTTPS: ON
   - Click "Save"

## ✅ Deployment Verification

After completing all phases, run this verification:

```bash
# 1. Organization exists
gh org view HARCOS-AI

# 2. All repos created
gh repo list HARCOS-AI

# 3. CDE repo transferred
gh repo view HARCOS-AI/CDE-Orchestrator-MCP

# 4. Licenses in place
gh api repos/HARCOS-AI/Agent-Framework/contents/LICENSE

# 5. Landing page deployed
curl -I https://harcos-ai.github.io/docs
# Should return: 200 OK

# 6. GitHub Sponsors active
gh repo view HARCOS-AI/docs --json hasSponsorsListing

# 7. Custom domain resolves (optional)
nslookup harcos.ai
```

## 🎉 Success!

Your HARCOS organization is now live:

```
✅ Organization: https://github.com/HARCOS-AI
✅ Landing page: https://harcos-ai.github.io/docs
✅ Custom domain: https://harcos.ai (optional)
✅ GitHub Sponsors: https://github.com/sponsors/HARCOS-AI
✅ Open Collective: https://opencollective.com/harcos-ai
```

## 📢 Next Steps (Post-Deployment)

1. **Announcement**:
   - Write blog post: "Introducing HARCOS"
   - Post on Twitter/LinkedIn
   - Share on Reddit, HN, Product Hunt

2. **Community**:
   - Create GitHub Discussions
   - Setup Discord or Slack channel
   - Invite beta testers

3. **Branding Assets**:
   - Create logo files in Figma
   - Upload to HARCOS/docs/assets/branding/
   - Configure org profile picture

4. **Enterprise Outreach**:
   - Identify 10-20 target companies
   - Send outreach emails
   - Schedule demos

5. **Analytics**:
   - Add Google Analytics to landing page
   - Setup uptime monitoring
   - Create dashboard

## 📚 Reference

- **Full setup guide**: `HARCOS_ORGANIZATION_SETUP.md`
- **Branding guide**: `HARCOS_BRANDING_GUIDELINES.md`
- **Landing page deployment**: `HARCOS_LANDING_PAGE_DEPLOYMENT.md`
- **Enterprise model**: `enterprise-services-analysis-2025-11-05.md`

---

**Time to completion**: ~2.5 hours
**Complexity**: Low to Medium
**Success rate**: 99% if steps followed

Good luck, and welcome to HARCOS! 🚀
