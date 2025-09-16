from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List

from .tool import load_tool_module


@dataclass
class AgentConfig:
    name: str
    slug: str
    description: str
    system_message: str
    tools: List[Dict[str, Any]]
    templates: Dict[str, str]
    llm: Dict[str, Any]


def resolve_agent_config(config: Dict[str, Any], slug: str) -> AgentConfig:
    candidates = config.get("agents", [])
    for a in candidates:
        if a.get("slug") == slug:
            templates = a.get("templates", {})
            return AgentConfig(
                name=a.get("name", slug),
                slug=slug,
                description=a.get("description", ""),
                system_message=a.get("system_message", ""),
                tools=a.get("tools", []),
                templates=templates,
                llm=config.get("llm", {}),
            )
    raise ValueError("Agent not found in config")


class ConfiguredAgent:
    def __init__(self, config: Dict[str, Any], agent_slug: str, uploads_dir: str, outputs_dir: str) -> None:
        self.cfg = resolve_agent_config(config, agent_slug)
        self.uploads_dir = Path(uploads_dir)
        self.outputs_dir = Path(outputs_dir)

        # dynamic tool loading from config
        self._tools = []
        for t in self.cfg.tools:
            module_path = t.get("module")
            class_name = t.get("class")
            method_name = t.get("method")
            kwargs = t.get("kwargs", {})
            tool = load_tool_module(module_path, class_name, method_name, kwargs)
            self._tools.append(tool)

    async def run(self, prompt: str) -> AsyncGenerator[Dict[str, Any], None]:
        # Simulated streaming. A real Autogen agent would be orchestrated here using cfg.llm.
        yield {"type": "log", "message": f"Starting agent: {self.cfg.name}"}
        await asyncio.sleep(0.2)
        yield {"type": "log", "message": self.cfg.system_message}
        await asyncio.sleep(0.2)
        if prompt:
            yield {"type": "user", "message": prompt}
            await asyncio.sleep(0.2)

        # Execute tools as defined (e.g., send email)
        for tool in self._tools:
            yield {"type": "log", "message": f"Running tool: {tool.label}"}
            result = await tool.invoke(
                prompt=prompt,
                uploads_dir=str(self.uploads_dir),
                outputs_dir=str(self.outputs_dir),
                templates=self.cfg.templates,
            )
            if result.get("artifact_path"):
                yield {
                    "type": "artifact",
                    "file": Path(result["artifact_path"]).name,
                }
            if result.get("log"):
                yield {"type": "log", "message": result["log"]}

        yield {"type": "log", "message": "Agent run completed."}

