# Gemini Integration & Prompting Guide

This document describes the integration of the Gemini model family within the Antigravity platform and provides guidelines for optimal prompting and configuration.

## Overview
Gemini is Google's family of highly capable multimodal AI models. In this environment, Gemini models power the agent's core reasoning, tool calling, and codebase analysis.

### Supported Models
- **Gemini 3.5 Flash (High)**: Optimized for fast, high-quality, and cost-efficient agentic tasks.
- **Gemini 3.5 Pro**: Best for complex reasoning, multi-turn code synthesis, and deep architectural analysis.
- **Gemma Local Models**: Lightweight models (like `gemma3-1b-gpu-custom`) can be routed locally for specific classifier tasks using WebMCP or local inference servers.

---

## Model Selection Configuration
The system allows dynamic model switching. The model selection settings are defined in the global configuration files:

- **Global Config Path**: `C:\Users\andre\.gemini\settings.json`
- **Plugin Specific Routing**:
  ```json
  {
    "experimental": {
      "gemmaModelRouter": {
        "enabled": true,
        "classifier": {
          "host": "http://localhost:9379",
          "model": "gemma3-1b-gpu-custom"
        }
      }
    }
  }
  ```

---

## Best Practices for Prompting Gemini in Antigravity
1. **Be Specific about Tools**: Gemini performs best when tools are clearly defined with arguments and types (using JSON Schema).
2. **Provide Rich Context**: Leverage system instructions to shape the agent's persona and limit the scope of its search.
3. **Structured Outputs**: Use standard JSON structures or Pydantic schemas to parse complex outputs reliably.
4. **Multimodal Inputs**: Provide images, logs, and screenshots directly in the conversation context when debugging visual tools like Blender.
