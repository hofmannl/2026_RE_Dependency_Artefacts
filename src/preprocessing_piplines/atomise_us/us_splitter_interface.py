from abc import ABC, abstractmethod


class USSplitterInterface(ABC):
    @abstractmethod
    def split_user_story(user_story: str) -> set[str]:
        pass