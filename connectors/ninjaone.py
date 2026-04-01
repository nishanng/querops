from connectors.base import BaseConnector


class NinjaOneConnector(BaseConnector):

    def get_name(self) -> str:
        return "NinjaOne RMM"

    def test_connection(self) -> bool:
        return True

    def get_device(self, hostname: str) -> dict:
        h = hostname.lower()

        if "server" in h or "dc" in h:
            return {
                "hostname": hostname,
                "device_type": "Server",
                "os": "Windows Server 2022",
                "online": True,
                "cpu_usage": 45,
                "memory_usage": 67,
                "disk_usage": 55,
                "last_seen": "2026-04-01T21:00:00Z",
                "patch_status": "Up to date",
                "pending_patches": 0,
                "alerts": [],
                "client": "Acme Corp",
            }

        if "laptop" in h or "pc" in h or "workstation" in h:
            return {
                "hostname": hostname,
                "device_type": "Workstation",
                "os": "Windows 11 Pro",
                "online": True,
                "cpu_usage": 12,
                "memory_usage": 45,
                "disk_usage": 78,
                "last_seen": "2026-04-01T20:55:00Z",
                "patch_status": "Patches pending",
                "pending_patches": 7,
                "alerts": ["Disk usage above 75%"],
                "client": "Acme Corp",
            }

        return {
            "hostname": hostname,
            "device_type": "Unknown",
            "os": "Windows 10 Pro",
            "online": False,
            "cpu_usage": 0,
            "memory_usage": 0,
            "disk_usage": 0,
            "last_seen": "2026-03-28T10:00:00Z",
            "patch_status": "Unknown",
            "pending_patches": 0,
            "alerts": ["Device offline — last seen 4 days ago"],
            "client": "Acme Corp",
        }

    def get_all_devices(self, client_name: str = None) -> list:
        return [
            {
                "hostname": "ACME-DC01",
                "device_type": "Server",
                "os": "Windows Server 2022",
                "online": True,
                "cpu_usage": 45,
                "memory_usage": 67,
                "disk_usage": 55,
                "patch_status": "Up to date",
                "pending_patches": 0,
                "alerts": [],
                "client": "Acme Corp",
            },
            {
                "hostname": "ACME-FS01",
                "device_type": "Server",
                "os": "Windows Server 2019",
                "online": True,
                "cpu_usage": 23,
                "memory_usage": 41,
                "disk_usage": 82,
                "patch_status": "Patches pending",
                "pending_patches": 3,
                "alerts": ["Disk usage critical — 82%"],
                "client": "Acme Corp",
            },
            {
                "hostname": "ACME-LT001",
                "device_type": "Workstation",
                "os": "Windows 11 Pro",
                "online": True,
                "cpu_usage": 12,
                "memory_usage": 45,
                "disk_usage": 78,
                "patch_status": "Patches pending",
                "pending_patches": 7,
                "alerts": ["Disk usage above 75%"],
                "client": "Acme Corp",
            },
            {
                "hostname": "ACME-LT002",
                "device_type": "Workstation",
                "os": "Windows 11 Pro",
                "online": False,
                "cpu_usage": 0,
                "memory_usage": 0,
                "disk_usage": 0,
                "patch_status": "Unknown",
                "pending_patches": 12,
                "alerts": ["Device offline", "12 patches overdue"],
                "client": "Acme Corp",
            },
            {
                "hostname": "ACME-PC003",
                "device_type": "Workstation",
                "os": "Windows 10 Pro",
                "online": True,
                "cpu_usage": 88,
                "memory_usage": 91,
                "disk_usage": 45,
                "patch_status": "Up to date",
                "pending_patches": 0,
                "alerts": ["High CPU — 88%", "High memory — 91%"],
                "client": "Acme Corp",
            },
        ]

    def get_alerts(self, client_name: str = None) -> list:
        return [
            {
                "device": "ACME-FS01",
                "severity": "critical",
                "message": "Disk usage critical — 82% on C: drive",
                "triggered": "2026-04-01T18:30:00Z",
                "client": "Acme Corp",
            },
            {
                "device": "ACME-LT002",
                "severity": "high",
                "message": "Device offline — 12 patches overdue",
                "triggered": "2026-03-28T10:00:00Z",
                "client": "Acme Corp",
            },
            {
                "device": "ACME-PC003",
                "severity": "warning",
                "message": "High CPU (88%) and memory (91%) usage",
                "triggered": "2026-04-01T21:05:00Z",
                "client": "Acme Corp",
            },
            {
                "device": "ACME-LT001",
                "severity": "warning",
                "message": "Disk usage above threshold — 78%",
                "triggered": "2026-04-01T19:45:00Z",
                "client": "Acme Corp",
            },
        ]
