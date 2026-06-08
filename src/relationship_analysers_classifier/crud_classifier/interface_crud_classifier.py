

from abc import ABC, abstractmethod
from typing import Union
from relationship_analysers_classifier.crud_classifier.crud_actions import CrudAction


class InterfaceCrudClassifier(ABC):
    _instances: dict = {}
    
    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[cls] = instance
            instance.model_name = None 
        return cls._instances[cls]
    
    def __init__(self, model_name: str, model: object, *args, **kwargs):
        self.model_name = model_name
        self.model = model
    
    @staticmethod
    def get_instance(model_name) -> Union['InterfaceCrudClassifier', None]:
        result: Union['InterfaceCrudClassifier', None] = None
        for _ in InterfaceCrudClassifier._instances:
            if InterfaceCrudClassifier._instances[_].model_name == model_name:
                result = InterfaceCrudClassifier._instances[_]
        return result

    @abstractmethod
    def classify(self, operation: str) -> tuple[CrudAction, Union[float, None]]:
        pass
    
    def reset_crud_classifier(self, instance_class=None, model_name=None):
        """
        Reset the CRUD classifier instance.
        
        Args:
            model: New model to set (optional)
            model_name: New model name to set (optional)
        """
        if instance_class is None:
            to_remove: InterfaceCrudClassifier = None
            for _ in InterfaceCrudClassifier._instances:
                if InterfaceCrudClassifier._instances[_].model_name == model_name:
                    to_remove = InterfaceCrudClassifier._instances[_]
            if to_remove:
                del InterfaceCrudClassifier._instances[to_remove]
        if model_name is None:
            del InterfaceCrudClassifier._instances[instance_class]