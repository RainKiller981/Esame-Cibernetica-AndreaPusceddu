# Google Antigravity SDK & Agents Architecture

This document outlines the architecture of the Google Antigravity (AGY) SDK, custom agent configurations, and how specialized subagents interact with local tools and workspaces.

## Architecture Overview
The Google Antigravity platform enables developers to orchestrate autonomous AI agents. The framework is designed around:
- **Agent**: The core unit of execution, defined by system prompt sections, equipped tools, and settings.
- **Conversation**: The context window and messaging channel of the active session.
- **Connection**: Interface to external services, local commands, and MCP (Model Context Protocol) servers.

---

## Agent Configuration (agent.json)
Agents are defined declaratively in JSON files. The standard format is:

```json
{
  "name": "agent_name",
  "description": "Agent description",
  "hidden": true,
  "config": {
    "customAgent": {
      "systemPromptSections": [
        {
          "title": "Agent System Instructions",
          "content": "Core instructions..."
        }
      ],
      "toolNames": [
        "send_message",
        "run_command",
        "manage_task"
      ],
      "systemPromptConfig": {
        "includeSections": [
          "user_information",
          "skills",
          "artifacts"
        ]
      }
    }
  }
}
```

---

## Generated Subagents
During our work, we created two custom agents to automate Blender tasks:

### 1. Blender Creator (`blender_creator`)
- **Role**: Designs, models, and styles 3D scenes in Blender.
- **Integration**: Connects to the local Blender session over TCP port `9876` using a custom socket protocol, allowing commands like `execute_code`, `get_scene_info`, and `get_viewport_screenshot`.
- **Location**: `.agents/agents/blender_creator/agent.json`

### 2. Blender Script Writer (`blender_script_writer`)
- **Role**: Writes wrapper scripts to launch Blender in headless background mode and export results to standard JSON.
- **Location**: `.agents/agents/blender_script_writer/agent.json`
