from relationship_analysers_classifier.crud_classifier.interface_crud_classifier import InterfaceCrudClassifier
from relationship_analysers_classifier.crud_classifier.crud_actions import CrudAction
from relationship_analysers_classifier.crud_classifier.load_crud_mappings import load_crud_mappings 
from dotenv import load_dotenv

from gensim.models import KeyedVectors

import os
import numpy as np

class GensimWord2VecCRUDClassifier(InterfaceCrudClassifier):
    '''
        Google Word2Vec-based CRUD operation categorizer.
        This class utilizes Google Word2Vec embeddings to categorize CRUD operations based on their textual descriptions.

        The following links can be helpful:
            - https://code.google.com/archive/p/word2vec/?utm_source=chatgpt.com

        We are using Gensim (https://radimrehurek.com/gensim/apiref.html#api-reference) for the implementation instead of tenserflow word2vec (https://www.tensorflow.org/text/tutorials/word2vec) due to the simplicity and ease of use it offers.
    '''
    
    load_dotenv()
    
    CLASSES: dict[str, list[str]] = load_crud_mappings()
    MODEL_NAME: str = os.getenv("GENSIM_MODEL_NAME")   
    
    def __init__(self, bag_of_words_size: int = 1):
        existing_model = GensimWord2VecCRUDClassifier.get_gensim_instance() 
        if existing_model:
            return existing_model 
        
        model_path = os.getenv("GENSIM_MODEL_PATH")
        
        if bag_of_words_size:
            GensimWord2VecCRUDClassifier.CLASSES = load_crud_mappings(file_name=f"crud_mappings_{bag_of_words_size}")
            
        model = KeyedVectors.load_word2vec_format(model_path, binary=True)
        
        def _centroid(words):
            vectors = [model.get_vector(w.lower()) for w in words if w.lower() in model]
            if not vectors:
                return np.zeros(model.vector_size)
            return np.mean(vectors, axis=0)
        
        self.model = model
        self.centroids = {c: _centroid(ws) for c, ws in self.CLASSES.items()}
        
        super().__init__(GensimWord2VecCRUDClassifier.MODEL_NAME, model)
        
        
    @staticmethod
    def get_gensim_instance() -> InterfaceCrudClassifier:
        return InterfaceCrudClassifier.get_instance(model_name=GensimWord2VecCRUDClassifier.MODEL_NAME)
    
    def classify(self, operation: str) -> tuple[CrudAction, float]:
        operation_lower = operation.lower()
        words = operation_lower.split()
        
        # Get vectors for all words that exist in the model
        vectors = [self.model.get_vector(w) for w in words if w in self.model]
        
        # Index for single-word CRUD actions
        if len(words) == 1:
            if words[0] in GensimWord2VecCRUDClassifier.CLASSES["create"]:
                return CrudAction.CREATE, 1.0
            if words[0] in GensimWord2VecCRUDClassifier.CLASSES["read"]:
                return CrudAction.READ, 1.0
            if words[0] in GensimWord2VecCRUDClassifier.CLASSES["update"]:
                return CrudAction.UPDATE, 1.0
            if words[0] in GensimWord2VecCRUDClassifier.CLASSES["delete"]:
                return CrudAction.DELETE, 1.0
        
        # Handle Out-of-Vocabulary (OOV) tokens
        if not vectors:
            return CrudAction.from_string("other"), 0.0
        
        # Average the word vectors
        v = np.mean(vectors, axis=0)

        # Calculate cosine similarities to all centroids
        sims: dict[str, float] = {
            c: float(np.dot(v, cvec) / 
                     (np.linalg.norm(v) * np.linalg.norm(cvec)))
            for c, cvec in self.centroids.items()
        }

        best_label = max(
            sims,
            key=sims.get
        )
        result_similarity = sims[best_label]

        return CrudAction.from_string(best_label), result_similarity