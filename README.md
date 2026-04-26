# Ansible MCP Demo

Demonstrates integrating MCP (Model Context Protocol) servers into Ansible playbooks using the `ansible.mcp` and `ansible.mcp_builder` collections.

## Overview

This demo includes two MCP servers:
- **GitHub MCP Server** - Interact with GitHub repositories, issues, and pull requests
- **Fetch MCP Server** - Retrieve web content via HTTP/HTTPS

## Prerequisites

- Podman or Docker
- ansible-builder
- ansible-navigator
- GitHub Personal Access Token (for GitHub MCP server)

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

## Important Notes

- **Never embed credentials** into the execution environment image
- GitHub MCP server requires `GITHUB_PERSONAL_ACCESS_TOKEN` environment variable
