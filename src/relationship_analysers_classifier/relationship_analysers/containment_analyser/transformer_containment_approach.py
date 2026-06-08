from transformers import pipeline
from relationship_analysers_classifier.relationship_analysers.relation_resolver import RelationResolver
from utilis.util_functions import get_article
import torch

import dotenv
import os

dotenv.load_dotenv()

class ContainmentAnalyserTransformer(RelationResolver):
    MODEL_ENV_VAR = "TRANSFORMER_MODEL_NAME"

    def __init__(self) -> None:
        model_name = os.getenv(self.MODEL_ENV_VAR, "facebook/bart-large-mnli")
        device = 0 if torch.cuda.is_available() else -1
        self.classifier = pipeline(
            "zero-shot-classification", 
            model=model_name,
            device=device
        )

    def compute_relations(self, child: str, parent: str, threshold: float = 0.7) -> tuple[bool, float]:
        if not child or not parent:
            raise ValueError("Words must be non-empty")
        return self.is_contained(child.lower(), parent.lower(), threshold)

    def is_contained(self, element: str, container: str, threshold: float) -> tuple[bool, float]:
        """
        Fixed: Evaluates all hypotheses in a single pass without a competing null label.
        """
        if element == container:
            return False, 0.0  
        
        art_ch, art_pa = get_article(element), get_article(container)
        
        premise = "System specifications often define compositional and structural relationships, where one element contains or may contain another."
        
        candidate_labels = [
            f"{art_pa} {container} includes {art_ch} {element}",
            f"{art_pa} {container} contains {art_ch} {element}",
            f"{art_pa} {container} holds at least one {element}",
            f"{art_pa} {container} can include {art_ch} {element}",
            f"{art_pa} {container} can hold at least one {element}",
            f"{art_pa} {container} has {art_ch} {element}",
            f"{art_pa} {container} consists of {element}s",
            f"{art_pa} {container} comprises {element}s",
            f"{art_pa} {container} incorporates {element}s",
            f"{art_pa} {container} has got {art_ch} {element}",
            f"{art_pa} {container} comes with {art_ch} {element}",
        ]
 
        result = self.classifier(
            premise,
            candidate_labels,
            multi_label=True  
        )
        
        max_confidence = max(result['scores'])
        return (max_confidence >= threshold, max_confidence)

# import time 

# cat = ContainmentAnalyserTransformer()

# start = time.time()
# result, confidence = cat.compute_relations("wheel", "bicycle", threshold=0.7)
# print(f"Is 'wheel' contained in 'bicycle'? {result} (confidence: {confidence:.4f})")
# result, confidence = cat.compute_relations("bicycle", "wheel", threshold=0.7)
# print(f"Is 'bicycle' contained in 'wheel'? {result} (confidence: {confidence:.4f})")
# result, confidence = cat.compute_relations("wheel", "bike", threshold=0.7)
# print(f"Is 'wheel' contained in 'bike'? {result} (confidence: {confidence:.4f})")
# result, confidence = cat.compute_relations("bike", "wheel", threshold=0.7)
# print(f"Is 'bike' contained in 'wheel'? {result} (confidence: {confidence:.4f})")
# result, confidence = cat.compute_relations("Ski", "Code", threshold=0.7)
# print(f"Is 'Ski' contained in 'Code'? {result} (confidence: {confidence:.4f})")
# result, confidence = cat.compute_relations("Code", "Ski", threshold=0.7)
# print(f"Is 'Code' contained in 'Ski'? {result} (confidence: {confidence:.4f})")
# end = time.time()
# print(f"Time taken for 6 operations: {end - start:.2f} seconds")