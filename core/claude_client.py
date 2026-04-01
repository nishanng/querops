import json
import os
import re

import anthropic

from connectors.azure_ad import AzureADConnector
from connectors.ninjaone import NinjaOneConnector
from connectors.crowdstrike import CrowdStrikeConnector

SYSTEM_PROMPT = """You are Querops, an AI assistant built specifically for MSP (Managed Service Provider) engineers.

You receive real-time data fetched from client systems and answer engineer questions accurately and concisely.

Rules:
- Always state which data source you used
- Use technical MSP language — engineers know their tools, don't over-explain basics
- Be concise — engineers are busy, no waffle
- If data is incomplete, say so explicitly
- Never guess or hallucinate — only use the data provided to you
- Format clearly: bullet points for multiple items, single sentence for simple answers
- If you cannot answer from the data provided, say exactly what additional data would help"""

USER_IDENTITY_KEYWORDS = [
    "user", "login", "sign in", "signin", "password", "mfa",
    "account", "email", "employee", "staff", "access", "locked",
    "disabled", "entra", "azure ad", "directory",
]

DEVICE_KEYWORDS = [
    "device", "computer", "laptop", "pc", "server",
    "workstation", "machine", "endpoint", "patch",
    "patches", "cpu", "memory", "disk", "offline",
    "online", "hardware", "rmm", "ninjaone", "ninja",
    "alert", "alerts",
]

SECURITY_KEYWORDS = [
    "security", "threat", "detection", "malware",
    "virus", "crowdstrike", "falcon", "incident",
    "breach", "attack", "suspicious", "powershell",
    "credential", "brute force", "vulnerability",
    "sensor", "edr", "endpoint protection",
]


class QueryEngine:

    def __init__(
        self,
        azure_connector: AzureADConnector,
        ninja_connector: NinjaOneConnector,
        crowdstrike_connector: CrowdStrikeConnector,
    ):
        self.azure = azure_connector
        self.ninja = ninja_connector
        self.crowdstrike = crowdstrike_connector
        self.client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

    def _route_to_azure(self, question: str) -> bool:
        q = question.lower()
        return any(kw in q for kw in USER_IDENTITY_KEYWORDS)

    def _route_to_ninja(self, question: str) -> bool:
        q = question.lower()
        return any(kw in q for kw in DEVICE_KEYWORDS)

    def _route_to_crowdstrike(self, question: str) -> bool:
        q = question.lower()
        return any(kw in q for kw in SECURITY_KEYWORDS)

    def _extract_email(self, question: str) -> str | None:
        match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", question)
        return match.group(0) if match else None

    def _extract_hostname(self, question: str) -> str | None:
        match = re.search(r"ACME-\w+", question, re.IGNORECASE)
        return match.group(0) if match else None

    def _fetch_azure_data(self, question: str) -> str:
        q = question.lower()
        email = self._extract_email(question)

        if "all users" in q or "list users" in q or "show users" in q:
            users = self.azure.get_all_users()
            return f"Azure AD Users:\n{json.dumps(users, indent=2, default=str)}"

        if email:
            data_parts = []
            user_info = self.azure.get_user(email)
            data_parts.append(f"User Profile:\n{json.dumps(user_info, indent=2, default=str)}")

            if any(kw in q for kw in ["sign in", "signin", "login", "last"]):
                signin = self.azure.get_user_signin_logs(email)
                data_parts.append(f"Sign-In Logs:\n{json.dumps(signin, indent=2, default=str)}")

            return "\n\n".join(data_parts)

        users = self.azure.get_all_users()
        return f"Azure AD Users:\n{json.dumps(users, indent=2, default=str)}"

    def _fetch_ninja_data(self, question: str) -> str:
        q = question.lower()
        hostname = self._extract_hostname(question)

        if "all devices" in q or "list devices" in q:
            devices = self.ninja.get_all_devices()
            return f"NinjaOne Devices:\n{json.dumps(devices, indent=2, default=str)}"

        if "alert" in q:
            alerts = self.ninja.get_alerts()
            return f"NinjaOne Alerts:\n{json.dumps(alerts, indent=2, default=str)}"

        if hostname:
            device = self.ninja.get_device(hostname)
            return f"NinjaOne Device ({hostname}):\n{json.dumps(device, indent=2, default=str)}"

        devices = self.ninja.get_all_devices()
        return f"NinjaOne Devices:\n{json.dumps(devices, indent=2, default=str)}"

    def _fetch_crowdstrike_data(self, question: str) -> str:
        q = question.lower()
        hostname = self._extract_hostname(question)

        if "summary" in q or "posture" in q or "overview" in q:
            summary = self.crowdstrike.get_summary()
            return f"CrowdStrike Summary:\n{json.dumps(summary, indent=2, default=str)}"

        if "detection" in q or "threat" in q:
            detections = self.crowdstrike.get_detections()
            return f"CrowdStrike Detections:\n{json.dumps(detections, indent=2, default=str)}"

        if hostname:
            status = self.crowdstrike.get_device_status(hostname)
            return f"CrowdStrike Device Status ({hostname}):\n{json.dumps(status, indent=2, default=str)}"

        summary = self.crowdstrike.get_summary()
        detections = self.crowdstrike.get_detections()
        return (
            f"CrowdStrike Summary:\n{json.dumps(summary, indent=2, default=str)}\n\n"
            f"CrowdStrike Detections:\n{json.dumps(detections, indent=2, default=str)}"
        )

    def ask(self, question: str, client_name: str | None = None) -> str:
        context_parts = []

        if client_name:
            context_parts.append(f"Client: {client_name}")

        route_azure = self._route_to_azure(question)
        route_ninja = self._route_to_ninja(question)
        route_crowdstrike = self._route_to_crowdstrike(question)

        if route_azure:
            context_parts.append(self._fetch_azure_data(question))
        if route_ninja:
            context_parts.append(self._fetch_ninja_data(question))
        if route_crowdstrike:
            context_parts.append(self._fetch_crowdstrike_data(question))

        if not (route_azure or route_ninja or route_crowdstrike):
            return (
                "I couldn't determine which data source to query for that question. "
                "Try mentioning a user, device, or specific system."
            )

        data_context = "\n\n".join(context_parts)
        user_message = f"Engineer's question: {question}\n\nData from connectors:\n{data_context}"

        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        return response.content[0].text
