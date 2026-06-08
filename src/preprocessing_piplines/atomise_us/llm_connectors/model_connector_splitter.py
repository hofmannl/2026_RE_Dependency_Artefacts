from abc import ABC, abstractmethod

from utilis.dataclasses_user_story import UserStoryRecord

class ModelConnectorForSplitter(ABC):
    @abstractmethod
    def send_splitting_request(self, system_prompt: list[str], user_story_records: set[UserStoryRecord]) -> str:
        pass