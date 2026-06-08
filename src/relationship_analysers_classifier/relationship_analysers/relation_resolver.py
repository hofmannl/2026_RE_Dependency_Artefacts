from abc import ABC, abstractmethod


class RelationResolver(ABC):
    @abstractmethod
    def compute_relations(data):
        pass