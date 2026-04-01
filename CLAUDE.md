# Querops — Claude Code Context

## What This Project Is

Querops is an AI-powered assistant for MSP
(Managed Service Provider) engineers. It lets
engineers ask questions in plain English about
their clients' IT environments and get instant
answers — without opening multiple dashboards.

Instead of opening 6 different tools to
troubleshoot one issue, engineers ask Querops
one question and get one synthesised answer.

## The Problem We Solve

MSP engineers waste 15-20 minutes per incident
switching between tools:
- PSA (tickets/history)
- RMM (device health)
- Azure AD (user/identity)
- EDR (security alerts)
- Firewall/network tools
- Cloud platforms

Querops queries all of them via APIs, fetches
live data, and uses Claude AI to synthesise
a plain English answer in under 10 seconds.

## Architecture Principles

1. CONNECTOR PATTERN
   Every tool = one connector class
   Every connector inherits from BaseConnector
   Claude AI never knows which tool it queries —
   it receives structured data and answers in
   plain English

2. DATA NEVER STORED
   Raw API responses are NEVER stored permanently
   Data is fetched live on each query
   Only metadata logged (who asked what, when)
   Critical for MSP client data security

3. READ-ONLY BY DEFAULT
   All connectors use read-only API credentials
   Querops observes — never makes changes

4. GRACEFUL DEGRADATION
   If a connector fails, say so clearly
   Never guess or hallucinate data
   Partial answer from working connectors is
   better than silence

5. MULTI-CLIENT AWARE
   Every query scoped to a specific client
   Client A data never appears in Client B response

## Current State (v0.2.0)

Phase 1 complete — local CLI proof of concept.

Connectors:
  - Azure AD (LIVE — real Microsoft Graph API)
  - NinjaOne RMM (DEMO — mock data)
  - CrowdStrike Falcon (DEMO — mock data)

Interface: Local CLI (python3 main.py)
AI Engine: Claude API (claude-sonnet-4-6)

## Tech Stack

Language:    Python 3.11+
AI:          Anthropic Claude API
Auth:        MSAL (Microsoft Authentication)
HTTP:        httpx
API:         FastAPI (future Teams bot)
Config:      python-dotenv
Interface:   CLI now → Teams bot Phase 4

## Project Structure

querops/
├── main.py                  ← CLI entry point
├── connectors/
│   ├── base.py              ← Abstract base class
│   ├── azure_ad.py          ← Live Azure AD connector
│   ├── ninjaone.py          ← Mock NinjaOne RMM
│   └── crowdstrike.py       ← Mock CrowdStrike
├── core/
│   └── claude_client.py     ← Query engine + routing
├── .env                     ← Never committed
├── .env.example             ← Template
├── requirements.txt
└── CLAUDE.md                ← This file

## Security Rules — Always Follow

- Credentials ALWAYS from .env — never hardcoded
- .env ALWAYS in .gitignore — never committed
- Never print or log raw credentials
- API responses used then discarded — not stored
- Every error returns structured dict, never crashes
- All connectors read-only by default

## Development Phases

Phase 1 (COMPLETE): CLI + Azure AD + mock connectors
Phase 2 (NEXT): Intune connector + cross-connector
                queries (one question, multiple sources)
Phase 3: FortiManager + Aruba Central connectors
Phase 4: Microsoft Teams bot interface
Phase 5: Web dashboard + SaaS billing + multi-tenant

## Adding a New Connector

1. Create connectors/toolname.py
2. Inherit from BaseConnector
3. Implement test_connection() and get_name()
4. Add relevant methods (get_devices, get_alerts etc)
5. Add routing keywords to core/claude_client.py
6. Add data fetch method to QueryEngine
7. Update routing in ask() method
8. Update main.py to initialise and show status
9. Add to .env.example if real credentials needed
10. Update README.md integrations list

## Running Locally

source .venv/bin/activate.fish
python3 main.py
