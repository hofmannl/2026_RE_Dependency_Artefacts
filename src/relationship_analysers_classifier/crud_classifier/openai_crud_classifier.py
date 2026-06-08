import math
from openai import OpenAI
from prompt_configs.crud.crud_prompts_llm import build_prompt
from relationship_analysers_classifier.crud_classifier.interface_crud_classifier import InterfaceCrudClassifier
from relationship_analysers_classifier.crud_classifier.crud_actions import CrudAction
from relationship_analysers_classifier.relationship_analysers.utitls.utils import convert_triples, detect_and_reprompt_missing_elements, extract_triple_elements
import dotenv, os, tiktoken

dotenv.load_dotenv()
    
class CrudAnalyserOpenAI(InterfaceCrudClassifier):    
    def __init__(self, model: str = os.getenv("MODEL_OPENAI"), single_word: bool = True) -> None:
        """
        Initialize the OpenAI CRUD analyzer.
        
        Args:
            single_word (bool): Whether to classify single words or sentences
            model (str): OpenAI model to use. Defaults to gpt-3.5-turbo
        """
        model_name = f"openai_{model}"
        
        client = OpenAI(
            api_key=os.getenv("MODEL_OPENAI"),
        )
        
        super().__init__(model_name, client)
        
        self.model_name_str = model
        self.single_word = single_word
        
        self.temperature = os.getenv("TEMPERATURE", 0.0)
        self.top_p = os.getenv("TOP_P", 0.3)
        self.max_batch_size = int(os.getenv("MAX_BATCH_SIZE_LLM", 100))
        
        try: 
            self.encoding = tiktoken.encoding_for_model(model)
        except Exception:
            self.encoding = tiktoken.get_encoding("cl100k_base")
        
        tokens: int = int(os.getenv("OPEN_AI_MODEL_CONTEXT_WINDOWS"))
        context_safty_margin: float = float(os.getenv("CONTEXT_SAFETY_MARGIN", 0.65))
        self.context_windows = math.floor(tokens * context_safty_margin)
    
    def classify(self, operation: str) -> tuple[CrudAction, float]:
        try:
            response = self.model.chat.completions.create(
                model=self.model_name_str,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a deterministic classification service.\nYour task is to assign a single English verb to exactly one CRUD class.\nThere is no context other than the word itself.\nRespond only in the required output format, with no additional text."
                    },
                    {
                        "role": "user",
                        "content": build_prompt(operation, self.single_word)
                    }
                ],
                temperature=float(self.temperature),
                top_p=float(self.top_p),
            )
            
            temp_result = response.choices[0].message.content.strip().lower().split("--")
            
            if len(temp_result) == 2 and len(temp_result[0]) > 0 and len(temp_result[1]) > 0:
                crud_type = temp_result[1].strip()
                if crud_type == "create":
                    return (CrudAction.CREATE, 1.0)
                elif crud_type == "read":
                    return (CrudAction.READ, 1.0)
                elif crud_type == "update":
                    return (CrudAction.UPDATE, 1.0)
                elif crud_type == "delete":
                    return (CrudAction.DELETE, 1.0)
            
            return (CrudAction.UNKNOWN, 0.0)
        except Exception as e:
            print(f"An error occurred during OpenAI API call: {e}")
            return (CrudAction.UNKNOWN, 0.0)
    
    def __del__(self):
        if self.model and hasattr(self.model, 'close'):
            self.model.close()
            self.model = None