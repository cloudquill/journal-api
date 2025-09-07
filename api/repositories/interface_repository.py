from abc import ABC, abstractmethod
from typing import Dict, Any, List

class DatabaseInterface(ABC):
    @abstractmethod
    async def create_entry(self, entry_data: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    async def get_all_entries(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def get_entry(self, entry_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def update_entry(self, entry_id: str, updated_data: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    async def delete_all_entries(self) -> None:
        pass

    @abstractmethod
    async def delete_entry(self, entry_id: str) -> None:
        pass