from relationship_analysers_classifier.crud_classifier.interface_crud_classifier import InterfaceCrudClassifier
from relationship_analysers_classifier.crud_classifier.crud_actions import CrudAction
from relationship_analysers_classifier.crud_classifier.load_crud_mappings import load_crud_mappings 
from dotenv import load_dotenv
import numpy as np
import fasttext
import os


class FastTextCrudAnalyserClassifier(InterfaceCrudClassifier):
    '''
        FastText-based CRUD operation categorizer.
        This class utilizes FastText embeddings to categorize CRUD operations based on their textual descriptions.
        
        The following links can be helpful:
            - https://fasttext.cc/docs/en/unsupervised-tutorial.html
            - https://fasttext.cc/docs/en/english-vectors.html
            - https://github.com/facebookresearch/fastText
    '''
    load_dotenv()
            
    CLASSES: dict[str, list[str]] = load_crud_mappings()
    MODEL_NAME: str = os.getenv("FASTTEXT_MODEL_NAME")
    
    def __init__(self, bag_of_words_size: int = 1):
        existing_model = FastTextCrudAnalyserClassifier.get_fast_text_instance()
        if existing_model:
            return existing_model 
        
        path = os.path.abspath(os.path.normpath(os.getenv("FASTTEXT_MODEL_PATH")))
        model = fasttext.load_model(path)
        
        if bag_of_words_size:
            FastTextCrudAnalyserClassifier.CLASSES = load_crud_mappings(file_name=f"crud_mappings_{bag_of_words_size}")
        
        ### Building centroids based on the sentences
        def _calculate_centroids(model):
            """Calculates and returns the centroids for all classes."""
            centroids = {}
            for c, ws in FastTextCrudAnalyserClassifier.CLASSES.items():
                centroids[c] = model.get_sentence_vector(" ".join(ws))
            return centroids

        self.centroids = _calculate_centroids(model)

        super().__init__(model_name=FastTextCrudAnalyserClassifier.MODEL_NAME, model=model)

    @staticmethod
    def get_fast_text_instance() -> InterfaceCrudClassifier:
        return InterfaceCrudClassifier.get_instance(model_name=FastTextCrudAnalyserClassifier.MODEL_NAME)
    
    def classify(self, operation: str) -> tuple[CrudAction, float]:
        words = operation.lower().split()
        words = [w for w in words if w.strip()]
        
        # Index for single-word CRUD actions
        if len(words) == 1:
            # Check if single word matches known keywords
            for crud_type, keywords in FastTextCrudAnalyserClassifier.CLASSES.items():
                if words[0] in keywords:
                    return CrudAction.from_string(crud_type), 1.0
        
        # Multi-word: use embedding-based similarity
        v = self.model.get_word_vector(operation.lower())
        sims = {
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