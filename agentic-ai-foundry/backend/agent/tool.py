from __future__ import annotations

import asyncio
import json
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from importlib import import_module
from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import Template


def load_tool_module(module_path: str, class_name: str, method_name: str, kwargs: Dict[str, Any]):
    module = import_module(module_path)
    cls = getattr(module, class_name)
    instance = cls(**kwargs)
    method = getattr(instance, method_name)
    return ToolWrapper(label=f"{class_name}.{method_name}", func=method)


@dataclass
class ToolWrapper:
    label: str
    func: Any

    async def invoke(self, **kwargs):
        if asyncio.iscoroutinefunction(self.func):
            return await self.func(**kwargs)
        # run sync function in thread
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: self.func(**kwargs))


class EmailTool:
    def __init__(self, smtp_host: str = "", smtp_port: int = 587, smtp_user: str = "", smtp_password: str = "", sender: str = "", dry_run: bool = True) -> None:
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.sender = sender
        self.dry_run = dry_run

    def send_email(self, prompt: str, uploads_dir: str, outputs_dir: str, templates: Dict[str, str]):
        # Pick template from config
        template_path = templates.get("email_template")
        if not template_path:
            raise ValueError("email_template not provided in templates")
        tpath = Path(template_path)
        if not tpath.exists():
            raise FileNotFoundError(f"Template not found: {tpath}")

        template = Template(tpath.read_text(encoding="utf-8"))
        # naive parsing of prompt for recipient/subject; in real agent this is LLM-driven
        # prompt format example: to:someone@example.com; subject:Hello; body:Message
        recipient = "test@example.com"
        subject = "Sample Email from Agent"
        body_text = prompt or "Hello from Agent"
        for part in prompt.split(";") if prompt else []:
            kv = part.split(":", 1)
            if len(kv) == 2:
                k = kv[0].strip().lower()
                v = kv[1].strip()
                if k == "to":
                    recipient = v
                elif k == "subject":
                    subject = v
                elif k == "body":
                    body_text = v

        rendered = template.render(subject=subject, body=body_text)

        # Save an artifact for download
        outputs = Path(outputs_dir)
        outputs.mkdir(parents=True, exist_ok=True)
        artifact_path = outputs / f"email_{subject.replace(' ', '_')}.txt"
        artifact_path.write_text(rendered, encoding="utf-8")

        if self.dry_run:
            return {"log": f"[DRY RUN] Prepared email to {recipient}", "artifact_path": str(artifact_path)}

        msg = EmailMessage()
        msg["From"] = self.sender
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.set_content(body_text)

        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            if self.smtp_user:
                server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)

        return {"log": f"Sent email to {recipient}", "artifact_path": str(artifact_path)}

