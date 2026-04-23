"""Custom filter to parse JSON from MCP tool responses."""

import re
import json


def parse_mcp_json(content):
    """
    Extract and parse JSON from MCP tool response content.

    MCP tools return content as a list of objects with 'text' fields.
    This filter extracts the JSON object from the text and parses it.

    Args:
        content: MCP response content (list of dicts with 'text' keys)

    Returns:
        Parsed JSON object as a dict, or empty dict if parsing fails
    """
    if not content or not isinstance(content, list) or len(content) == 0:
        return {}

    try:
        text = content[0].get('text', '')
        # Extract JSON object from text (handles text before/after JSON)
        match = re.search(r'\{.*\}', text, re.MULTILINE | re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except (AttributeError, ValueError, json.JSONDecodeError):
        pass

    return {}


class FilterModule(object):
    """Ansible filter plugin for MCP response parsing."""

    def filters(self):
        return {
            'parse_mcp_json': parse_mcp_json
        }
