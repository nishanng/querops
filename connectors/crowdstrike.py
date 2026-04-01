from connectors.base import BaseConnector

KNOWN_HOSTS = {"acme-lt002", "acme-pc003", "acme-lt001", "acme-dc01", "acme-fs01"}


class CrowdStrikeConnector(BaseConnector):

    def get_name(self) -> str:
        return "CrowdStrike Falcon"

    def test_connection(self) -> bool:
        return True

    def get_detections(self, client_name: str = None) -> list:
        return [
            {
                "id": "det-001",
                "severity": "high",
                "device": "ACME-LT002",
                "tactic": "Credential Access",
                "technique": "Brute Force",
                "description": "Multiple failed authentication attempts detected — possible credential stuffing",
                "status": "open",
                "detected_at": "2026-04-01T19:22:00Z",
                "user": "john.smith@acmecorp.com",
                "client": "Acme Corp",
            },
            {
                "id": "det-002",
                "severity": "medium",
                "device": "ACME-PC003",
                "tactic": "Execution",
                "technique": "Command and Scripting Interpreter",
                "description": "Suspicious PowerShell execution — encoded command detected",
                "status": "under_review",
                "detected_at": "2026-04-01T20:47:00Z",
                "user": "sarah.jones@acmecorp.com",
                "client": "Acme Corp",
            },
            {
                "id": "det-003",
                "severity": "low",
                "device": "ACME-LT001",
                "tactic": "Discovery",
                "technique": "Network Service Discovery",
                "description": "Port scanning activity detected from this endpoint",
                "status": "open",
                "detected_at": "2026-04-01T17:10:00Z",
                "user": "mike.chen@acmecorp.com",
                "client": "Acme Corp",
            },
        ]

    def get_device_status(self, hostname: str) -> dict:
        if hostname.lower() in KNOWN_HOSTS:
            return {
                "hostname": hostname,
                "sensor_status": "active",
                "prevention_policy": "Standard Prevention",
                "last_seen": "2026-04-01T21:00:00Z",
                "os": "Windows 11 Pro",
                "detection_count": 2,
                "client": "Acme Corp",
            }

        return {
            "hostname": hostname,
            "sensor_status": "not_found",
            "message": "No CrowdStrike sensor detected on this device",
        }

    def get_summary(self, client_name: str = None) -> dict:
        return {
            "client": "Acme Corp",
            "total_devices_protected": 5,
            "sensors_active": 4,
            "sensors_offline": 1,
            "open_detections": 2,
            "detections_under_review": 1,
            "critical_detections": 0,
            "high_detections": 1,
            "medium_detections": 1,
            "low_detections": 1,
            "overall_risk": "medium",
            "last_updated": "2026-04-01T21:00:00Z",
        }
