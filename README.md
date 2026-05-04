# Ansible MCP Demo

Demonstrates integrating MCP (Model Context Protocol) servers into Ansible playbooks using the `ansible.mcp` and `ansible.mcp_builder` collections.

## Overview

This demo includes two MCP servers:
- **GitHub MCP Server** - Interact with GitHub repositories, issues, and pull requests
- **Fetch MCP Server** - Retrieve web content via HTTP/HTTPS

## Prerequisites

- Podman
- ansible-builder
- ansible-navigator
- GitHub Personal Access Token (for GitHub MCP server)

## Important Notes

- **Never embed credentials** into the execution environment image
- GitHub MCP server requires `GITHUB_PERSONAL_ACCESS_TOKEN` environment variable

## Setup

### 1. Obtain the Fetch MCP Collection

The `hdefazio.mcp_fetch` collection provides the Fetch MCP server integration. See the [collection README](https://github.com/hdefazio/hdefazio.mcp_fetch/blob/main/README.md) for more details.

Build the collection tarball from source:

```bash
git clone https://github.com/hdefazio/hdefazio.mcp_fetch
cd hdefazio.mcp_fetch
ansible-galaxy collection build --output-path /path/to/ansible_mcp_demo/ee_build/
```


### 2. Build the Execution Environment

The execution environment includes both MCP servers and required Ansible collections.

First, authenticate with the Red Hat registry:

```bash
podman login registry.redhat.io
```

Then build the execution environment:

```bash
cd ee_build
ansible-builder build -t my-mcp-ee:latest -f execution-environment.yml -v 3
```

**Note:** The `my-mcp-ee:latest` image is automatically used by ansible-navigator through the configuration in `ansible-navigator.yml`. This config file specifies the execution environment image, so you don't need to pass it explicitly with each command.

### 3. Configure Environment

Set your GitHub Personal Access Token:

```bash
export GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token_here
```

**Required token scopes:**
- `repo` - Full control of repositories (for private repos and PR comments)
- `public_repo` - Access to public repositories (minimum for public repos)

## Verification

### Verify Execution Environment Setup

Confirms MCP servers are installed and registered:

```bash
ansible-navigator run playbooks/verify-ee-setup.yml
```

### Explore MCP Server Functionality

#### GitHub MCP Server

Lists server info and 38 available tools:

```bash
ansible-navigator run playbooks/explore-github-mcp.yml
```

#### Fetch MCP Server

Lists server info and available fetch tool:

```bash
ansible-navigator run playbooks/explore-fetch-mcp.yml
```

## Demo: Whale Shark PR Migration Tracker

The `whale_shark_demo/whale-shark-pr-migration.yml` playbook showcases both MCP servers working together in a practical workflow. It tracks stale pull requests, monitors their health, and posts ocean-themed status comments directly on PRs.

### What It Does

Like a whale shark filtering through the ocean, this playbook:
- **Finds All Open PRs**: Uses GitHub search to get all open, non-draft PRs
- **Tracks Real Activity**: Distinguishes between whale shark comments and actual work (commits or human comments)
- **Smart Filtering**: Single-pass filtering by both real activity and whale shark comment recency
- **Analyzes PR Health**: Identifies PRs with failing CI or merge conflicts
- **Checks Ocean Conditions**: Monitors GitHub platform status using Fetch MCP
- **Provides Wisdom**: Posts GitHub Zen wisdom and navigation tips as PR comments
- **Comment Throttling**: Only re-comments after a configurable period to avoid spam
- **Safety Limited**: Refuses to comment on more than `max_prs_per_run` PRs to prevent accidental spam

### Configuration

Edit `playbooks/whale_shark_demo/vars/config.yml` to target your repository:

```yaml
# Repository to monitor
repo_owner: "your-org"
repo_name: "your-repo"

# Activity thresholds
days_last_activity_threshold: 5   # Comment on PRs with no activity for N+ days
comment_freshness_days: 7         # Wait N days before re-commenting
max_prs_per_run: 10              # Safety limit to prevent spam
```

**How it works:**
1. **GitHub search** finds all open, non-draft PRs
2. **Fetch details** gets PR metadata, comments, and commit history for each PR
3. **Real activity filter** includes PRs with no real activity (commits OR human comments) in N+ days
4. **Comment freshness** prevents re-commenting too frequently (whale shark comments don't count as activity)

**Real activity** = latest of:
- Last commit pushed to the PR branch
- Last non-whale-shark comment (reviews, questions, etc.)
- PR creation date (if no commits or comments)

### Usage

```bash
ansible-navigator run playbooks/whale_shark_demo/whale-shark-pr-migration.yml -i inventory.yml
```

### Output: Example PR Comment

```
🦈 Whale Shark PR Migration Status 🦈

Your PR is migrating through the review ocean!

Ocean Conditions: 🌊 Calm seas - All GitHub systems operational
Current Location: 🦑 tangled in kelp (blocked)
Days adrift: 📅 21 days
Last spotted: 🔭 7 days ago

🦈 Whale Shark Wisdom:
  > "Half measures are as bad as nothing at all."

🧭 Navigation Tips:
1. Check your compass - Review the CI status and any feedback
2. Test the waters - Run tests locally before pushing
3. Ask the school - Request review from your team

---
Whale sharks are the largest fish in the ocean and can migrate over 7,000 miles.
Your PR can make it through code review! Keep swimming! 🦈🌊
```

### Custom Filter Plugin

This playbook uses a custom `parse_mcp_json` filter to cleanly extract JSON from MCP tool responses:

```yaml
# Instead of verbose inline parsing
platform_status: "{{ response.content[0].text | regex_search('\\{.*\\}') | from_json }}"

# Use the custom filter
platform_status: "{{ response.content | parse_mcp_json }}"
```

The filter is located in `plugins/filter/parse_mcp_response.py` and automatically loaded via `ansible.cfg`.
