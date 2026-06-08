from openai import OpenAI
from prompt_configs.containment.containment_prompts_llm import build_prompt
from relationship_analysers_classifier.relationship_analysers.relation_resolver import RelationResolver
from relationship_analysers_classifier.relationship_analysers.utitls.utils import convert_triples, detect_and_reprompt_missing_elements, extract_triple_elements
import dotenv
import os
import tiktoken
import math

dotenv.load_dotenv()


class ContainmentAnalyserOpenAI(RelationResolver):    
    def __init__(self, model: str = os.getenv("OPENAI_MODEL")) -> None:
        """
        Initialize the OPENAI containment analyzer.
        
        Args:
            typ (TypeGraphUs): Type of element - ENTITY, ACTION, or PERSONA
            model (str): OPENAI model to use. Defaults to gpt-3.5-turbo
        """
        self.model = model
        self.client = OpenAI(
            api_key=os.getenv("MODEL_KEY_OPENAI")
        )
        
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
    
    def compute_relations(self, elements: set[tuple[str, str]] = None) -> list[tuple[str, str, bool]]:
        return self.are_contained(elements)
    
    def are_contained(self, pairs: set[tuple[str, str]]) -> list[tuple[str, str, bool]]:
        results: list[tuple[str, str, bool]] = []
        pairs_to_process: list[tuple[str, str]] = list(pairs)
        
        current_batch: list[tuple[str, str]] = []
        test_pair: str = ""
        test_batch: list[tuple[str, str]] = []
        batch_results: list[tuple[str, str, str]] = []
        prompt: str = ""
        
        while len(pairs_to_process) > 0:
            current_batch = []
            test_pair = ""
            test_batch = []
            
            while len(pairs_to_process) > 0 and len(test_batch) <= self.max_batch_size:
                test_pair = pairs_to_process[0]
                test_batch = current_batch.copy()
                test_batch.append(test_pair)
                
                prompt = build_prompt(test_batch)
                
                if len(self.encoding.encode(prompt)) <= self.context_windows:
                    current_batch.append(test_pair)
                    pairs_to_process.remove(test_pair)
                else:
                    break
            
            if current_batch:
                prompt = build_prompt(current_batch)
                
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are an expert in the field of requirements engineering and semantic analysis."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        temperature=self.top_p,
                        top_p=self.top_p,
                    )
                    
                    batch_results = extract_triple_elements(
                        response.choices[0].message.content, 
                        seperator="--", 
                        line_seperator="\n"
                    )
                    
                    temp = detect_and_reprompt_missing_elements(
                        batch_results,
                        set(current_batch),
                        self.client,
                        self.model,
                        self.top_p,
                        None,
                        build_prompt,
                        seperator="--"
                    )

                    if len(temp) > 0:
                        batch_results.extend(temp)       

                    results.extend(
                        convert_triples(batch_results)
                    )
                except Exception as e:
                    print(f"An error occurred during GDWG API call: {e}")
                    for pair in current_batch:
                        results.append((pair[0], pair[1], "error"))                
            else:
                raise ValueError("No pairs to process in the current batch.")
        
        return results
    
    def __del__(self):
        self.client.close()
        self.client = None