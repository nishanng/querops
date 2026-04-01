from abc import ABC, abstractmethod


class BaseConnector(ABC):
    """Abstract base class for all Querops connectors.

    Every integration (Azure AD, NinjaOne, CrowdStrike, etc.)
    inherits from this class and implements the required methods.
    """

    @abstractmethod
    def test_connection(self) -> bool:
        """Test connectivity to the external service.

        Returns True if the connection is healthy, False otherwise.
        Should print a helpful error message on failure.
        """

    @abstractmethod
    def get_name(self) -> str:
        """Return the human-readable connector name (e.g. 'Azure AD')."""
