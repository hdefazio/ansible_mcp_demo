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

### Test MCP Server Functionality

#### GitHub MCP Server

Lists server info and 38 available tools:

```bash
ansible-navigator run playbooks/test-github-mcp.yml
```

#### Fetch MCP Server

Lists server info and available fetch tool:

```bash
ansible-navigator run playbooks/test-fetch-mcp.yml
```

## Demo: Whale Shark PR Migration Tracker

The `whale-shark-pr-migration.yml` playbook showcases both MCP servers working together in a practical workflow. It tracks stale pull requests, monitors their health, and provides ocean-themed status reports.

### What It Does

Like a whale shark filtering through the ocean, this playbook:
- **Checks Ocean Conditions**: Monitors GitHub platform status using Fetch MCP
- **Finds PRs Adrift**: Searches for pull requests that haven't been updated in N days
- **Analyzes PR Health**: Identifies PRs with failing CI or merge conflicts
- **Provides Wisdom**: Displays GitHub Zen wisdom and navigation tips

### Configuration

Edit the playbook variables to target your repository:

```yaml
vars:
  repo_owner: "your-org"               # Repository owner
  repo_name: "your-repo"               # Repository name
  days_adrift_threshold: 3             # Days without updates
```

### Usage

```bash
ansible-navigator run playbooks/whale-shark-pr-migration.yml -i inventory.yml
```

### Output Example

```
🦈 Whale Shark PR Migration Status 🦈

Your PR is migrating through the review ocean!

Ocean Conditions: 🌊 Calm seas - All GitHub systems operational
Current Location: 🦑 tangled in kelp (blocked)
Days adrift: 📅 21 days

🦈 Whale Shark Wisdom:
  > "Half measures are as bad as nothing at all."

🧭 Navigation Tips:
1. Check your compass - Read the CI failure logs
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
