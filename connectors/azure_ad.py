import os

import httpx
import msal

from connectors.base import BaseConnector


class AzureADConnector(BaseConnector):

    GRAPH_BASE = "https://graph.microsoft.com/v1.0"
    USER_FIELDS = "displayName,userPrincipalName,accountEnabled,jobTitle,department,createdDateTime"

    def __init__(self):
        self.tenant_id = os.environ.get("AZURE_TENANT_ID", "")
        self.client_id = os.environ.get("AZURE_CLIENT_ID", "")
        self.client_secret = os.environ.get("AZURE_CLIENT_SECRET", "")
        self._token: str | None = None
        self._msal_app: msal.ConfidentialClientApplication | None = None

    def get_name(self) -> str:
        return "Azure AD"

    def _get_msal_app(self) -> msal.ConfidentialClientApplication:
        if self._msal_app is None:
            authority = f"https://login.microsoftonline.com/{self.tenant_id}"
            self._msal_app = msal.ConfidentialClientApplication(
                client_id=self.client_id,
                client_credential=self.client_secret,
                authority=authority,
            )
        return self._msal_app

    def _get_token(self) -> str | None:
        """Acquire a token using client credentials flow. Caches via MSAL."""
        app = self._get_msal_app()
        scopes = ["https://graph.microsoft.com/.default"]

        # Try cache first
        result = app.acquire_token_silent(scopes, account=None)
        if not result:
            result = app.acquire_token_for_client(scopes=scopes)

        if result and "access_token" in result:
            self._token = result["access_token"]
            return self._token

        error = result.get("error_description", "Unknown error") if result else "No result"
        print(f"  Azure AD auth failed: {error}")
        return None

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self._token}"}

    def test_connection(self) -> bool:
        if not all([self.tenant_id, self.client_id, self.client_secret]):
            print("  Azure AD credentials not configured in .env")
            return False

        token = self._get_token()
        if not token:
            return False

        try:
            resp = httpx.get(
                f"{self.GRAPH_BASE}/users?$top=1",
                headers=self._headers(),
                timeout=10,
            )
            return resp.status_code == 200
        except httpx.HTTPError as e:
            print(f"  Azure AD connection test failed: {e}")
            return False

    def get_user(self, email: str) -> dict:
        token = self._get_token()
        if not token:
            return {"error": "Failed to authenticate with Azure AD"}

        try:
            resp = httpx.get(
                f"{self.GRAPH_BASE}/users/{email}?$select={self.USER_FIELDS}",
                headers=self._headers(),
                timeout=10,
            )
            if resp.status_code == 404:
                return {"error": "User not found"}
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPError as e:
            return {"error": f"Graph API request failed: {e}"}

    def get_all_users(self) -> list:
        token = self._get_token()
        if not token:
            return [{"error": "Failed to authenticate with Azure AD"}]

        try:
            resp = httpx.get(
                f"{self.GRAPH_BASE}/users?$top=10&$select={self.USER_FIELDS}",
                headers=self._headers(),
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json().get("value", [])
        except httpx.HTTPError as e:
            return [{"error": f"Graph API request failed: {e}"}]

    def get_user_signin_logs(self, email: str) -> dict:
        token = self._get_token()
        if not token:
            return {"error": "Failed to authenticate with Azure AD"}

        try:
            filter_query = f"userPrincipalName eq '{email}'"
            resp = httpx.get(
                f"{self.GRAPH_BASE}/auditLogs/signIns",
                params={"$filter": filter_query, "$top": "1"},
                headers=self._headers(),
                timeout=10,
            )
            resp.raise_for_status()
            entries = resp.json().get("value", [])

            if not entries:
                return {"last_signin": "Never"}

            latest = entries[0]
            return {
                "last_signin": latest.get("createdDateTime", "Unknown"),
                "location": latest.get("location", {}).get("city", "Unknown"),
                "status": latest.get("status", {}).get("errorCode", 0),
            }
        except httpx.HTTPError as e:
            return {"error": f"Sign-in logs request failed: {e}"}
