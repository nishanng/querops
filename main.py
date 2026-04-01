import sys

from dotenv import load_dotenv

load_dotenv()

from connectors.azure_ad import AzureADConnector
from connectors.ninjaone import NinjaOneConnector
from connectors.crowdstrike import CrowdStrikeConnector
from core.claude_client import QueryEngine

BANNER = """
╔═══════════════════════════════════════════╗
║          QUEROPS v0.2.0                   ║
║    MSP AI Assistant — Local Dev Mode      ║
║                                           ║
║    Connectors initialising...             ║
╚═══════════════════════════════════════════╝
"""

HELP_TEXT = """
Example queries:
  → Is testuser@domain.com account enabled?
  → Show me all users in Azure AD
  → Show me all devices for Acme Corp
  → What is the status of ACME-DC01?
  → Are there any alerts for Acme Corp?
  → Show me security detections for Acme Corp
  → What is the security posture of Acme Corp?
  → Any high severity threats detected?
  → What patches are overdue?
"""


def main():
    print(BANNER)

    # Initialise connectors
    azure = AzureADConnector()
    ninja = NinjaOneConnector()
    crowdstrike = CrowdStrikeConnector()

    if azure.test_connection():
        print("  ✅ Azure AD          connected")
    else:
        print("  ❌ Azure AD          not connected — check .env credentials")

    if ninja.test_connection():
        print("  ✅ NinjaOne RMM      connected (demo mode)")
    else:
        print("  ❌ NinjaOne RMM      not connected")

    if crowdstrike.test_connection():
        print("  ✅ CrowdStrike       connected (demo mode)")
    else:
        print("  ❌ CrowdStrike       not connected")

    engine = QueryEngine(
        azure_connector=azure,
        ninja_connector=ninja,
        crowdstrike_connector=crowdstrike,
    )

    print("\nReady. Ask anything about your MSP environment.")
    print("Type 'exit' to quit, 'help' for example queries.\n")

    while True:
        try:
            question = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye.")
            sys.exit(0)

        if not question:
            continue
        if question.lower() == "exit":
            print("Goodbye.")
            sys.exit(0)
        if question.lower() == "help":
            print(HELP_TEXT)
            continue

        try:
            answer = engine.ask(question)
            print(f"\nQuerops: {answer}\n")
        except Exception as e:
            print(f"\nQuerops: Something went wrong — {e}\n")


if __name__ == "__main__":
    main()
