from transformers import pipeline
from relationship_analysers_classifier.relationship_analysers.relation_resolver import RelationResolver
from utilis.util_functions import get_article
from utilis.annotation_graph_components import TypeGraphUs
from torch.cuda import is_available as cuda_is_available

import dotenv
import os

from statistics import mean

dotenv.load_dotenv()

class SemanticEquivalenceAnalyserTransformer(RelationResolver):
    """
    Analyzes semantic equivalence between elements using BART-large-MNLI zero-shot classification.
    
    Detects whether two elements from user stories (entities, actions, or personas) are semantically
    equivalent and can be used interchangeably in requirements engineering contexts.
    
    Attributes:
        typ (TypeGraphUs): The type of element being compared (ENTITY, ACTION, or PERSONA)
        classifier: The Hugging Face transformer pipeline for zero-shot classification
    """
    MODEL_ENV_VAR = "TRANSFORMER_MODEL_NAME"
        
    def __init__(self, typ: TypeGraphUs = TypeGraphUs.ENTITY) -> None:
        """
        Initialize the semantic equivalence analyzer.
        
        Args:
            typ (TypeGraphUs): Type of element to analyze - ENTITY (nouns), ACTION (verbs), or PERSONA (roles).
                              Defaults to ENTITY.
        """
        model_name = os.getenv(self.MODEL_ENV_VAR, "facebook/bart-large-mnli")
        device = 0 if cuda_is_available() else -1
        
        self.typ: TypeGraphUs = typ 
        
        self.classifier = pipeline(
            "zero-shot-classification", 
            model=model_name,
            device=device
        )
    
    def compute_relations(self, child: str, parent: str, threshold: float = 0.7) -> tuple[bool, float]:
        if not child or not parent:
            raise ValueError("Words must be non-empty")
        return self.is_semantical_equivalent(child.lower(), parent.lower(), threshold)

    def is_semantical_equivalent(self, first_element: str, second_element: str, threshold: float) -> tuple[bool, float]:
        """
        Detects generalization relationships between entities.
        Returns True if parent is a generalization/supertype of child.
        Example: child="boot", parent="vehicle" -> True (boot is a type of vehicle)
        """
        
        if (first_element == second_element):
            return True, 1.0
    
        if (self.typ == TypeGraphUs.PERSONA): 
            art_ch, art_pa = get_article(first_element), get_article(second_element)
                      
            premise = (
                "System specifications define that two personas are considered semantically identical if they describe the same role and are associated with equivalent or sufficiently similar tasks."
            )         
               
            candidate_labels = [
                f"'{art_ch} {first_element}' and '{art_pa} {second_element}' represent the same duties in a job.",
                f"'{art_ch} {first_element}' is equivalent to '{art_pa} {second_element}'",
                f"'{art_ch} {first_element}' is equal to '{art_pa} {second_element}'",
                f"'{art_ch} {first_element}' is synonymous to '{art_pa} {second_element}'",
                f"'{art_ch} {first_element}' is identical to '{art_pa} {second_element}'",
                f"'{art_ch} {first_element}' is the same as '{art_pa} {second_element}'",
                f"'{art_ch} {first_element}' corresponds to '{art_pa} {second_element}'",
                f"'{art_ch} {first_element}' is interchangeable with '{art_pa} {second_element}'",
                f"'{art_ch} {first_element}' and '{art_pa} {second_element}' describe the same role.",
                f"'{art_ch} {first_element}' and '{art_pa} {second_element}' have the same responsibilities.",
            ]

        elif (self.typ == TypeGraphUs.ACTION):
            premise = (
                "System specifications define that two actions are considered semantically identical if they describe the same task or tasks that are sufficiently similar in intent and outcome."
            )         
            
            candidate_labels = [
                f"'{first_element}' is equivalent to '{second_element}'",
                f"'{first_element}' is equal to '{second_element}'",
                f"'{first_element}' is synonymous to '{second_element}'", 
                f"'{first_element}' is comparable to '{second_element}'", 
                f"'{first_element}' is identical to '{second_element}'", 
                f"'{first_element}' is the same as '{second_element}'",
                f"'{first_element}' corresponds to '{second_element}'",
                f"'{first_element}' is interchangeable to '{second_element}'",
            ]

            
        elif (self.typ == TypeGraphUs.ENTITY):  
            art_ch, art_pa = get_article(first_element), get_article(second_element)
                      
            premise = (
                "System specifications define that two entities are considered semantically identical if they represent the same concept or concepts that are equivalent in meaning and purpose."
            )            
            candidate_labels = [
                f"'{art_ch} {first_element}' is equivalent to {art_pa} '{second_element}'",
                f"'{art_ch} {first_element}' is equal to {art_pa} '{second_element}'",
                f"'{art_ch} {first_element}' is synonymous to {art_pa} '{second_element}'",
                f"'{art_ch} {first_element}' is comparable to {art_pa} '{second_element}'",
                f"'{art_ch} {first_element}' is identical to {art_pa} '{second_element}'",
                f"'{art_ch} {first_element}' is the same as {art_pa} '{second_element}'",
                f"'{art_ch} {first_element}' corresponds to {art_pa} '{second_element}'",
                f"'{art_ch} {first_element}' is interchangeable to {art_pa} '{second_element}'",
                f"'{art_ch} {first_element}' and {art_pa} '{second_element}' have identical meanings",
                f"'{art_ch} {first_element}' and {art_pa} '{second_element}' describe the same real-world object",
            ]

        else:
            raise ValueError(f"Unsupported TypeGraphUs: {self.typ}")
        
        result = self.classifier(
            premise,
            candidate_labels,
            multi_label=True  
        )
        
        # max_confidence = mean(result['scores']) 
        max_confidence = max(result['scores'])
        return max_confidence >= threshold, max_confidence


# gat = SemanticEquivalenceAnalyser(TypeGraphUs.PERSONA)

# result, confidence = gat.compute_relations("helper", "Admin", threshold=0.7)
# print(f"Is 'helper' and 'Admin' semantically equivalent? {result} (confidence: {confidence:.4f})")

# ---

# result, confidence = gat.compute_relations("customer", "client", threshold=0.7)
# print(f"Is 'customer' and 'client' semantically equivalent? {result} (confidence: {confidence:.4f})")

# gat = SemanticEquivalenceAnalyser(TypeGraphUs.ACTION)

# result, confidence = gat.compute_relations("Perform", "Send", threshold=0.7)
# print(f"Is 'Perform' and 'Send' semantically equivalent? {result} (confidence: {confidence:.4f})")

# result, confidence = gat.compute_relations("Perform", "fly", threshold=0.7)
# print(f"Is 'Perform' and 'fly' semantically equivalent? {result} (confidence: {confidence:.4f})")

# result, confidence = gat.compute_relations("create", "add", threshold=0.7)
# print(f"Is 'create' and 'add' semantically equivalent? {result} (confidence: {confidence:.4f})")

# gat = SemanticEquivalenceAnalyser(TypeGraphUs.ENTITY)

# result, confidence = gat.compute_relations("Database", "Database Entry", threshold=0.7)
# print(f"Is 'Database' and 'Database Entry' semantically equivalent? {result} (confidence: {confidence:.4f})")

# result, confidence = gat.compute_relations("email", "electronical mail", threshold=0.7)
# print(f"Is 'email' and 'electronical mail' semantically equivalent? {result} (confidence: {confidence:.4f})")

# result, confidence = gat.compute_relations("email", "email", threshold=0.7)
# print(f"Is 'email' and 'email' semantically equivalent? {result} (confidence: {confidence:.4f})")