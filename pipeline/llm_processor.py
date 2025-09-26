import requests
import re

class OllamaLLMProcessor:
    def __init__(self, model_name: str = "llama3.1:8b", base_url: str = "http://localhost:11434"):
        """
        Initialize Ollama LLM processor
        
        Args:
            model_name: Name of the Ollama model (e.g., 'llama3.1:8b', 'mistral', 'codellama')
            base_url: Ollama server URL (default: http://localhost:11434)
        """
        self.model_name = model_name
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/api/generate"
        
        # Test connection
        self._test_connection()
    
    def _test_connection(self):
        """Test if Ollama server is running and model is available"""
        try:
            # Check if Ollama server is running, /api/tags endpoint lists info about available models
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                available_models = [model['name'] for model in models]
                
                if not any(self.model_name in model for model in available_models):
                    print(f"Model '{self.model_name}' not found. Available models: {available_models}")
                    print(f"Run: ollama pull {self.model_name}")
                else:
                    print(f"Connected to Ollama. Model '{self.model_name}' is available.")
            else:
                print(f"Cannot connect to Ollama server at {self.base_url}")
        except requests.exceptions.ConnectionError:
            print(f"Ollama server not running. Start it with: ollama serve")
        except Exception as e:
            print(f"Error connecting to Ollama: {e}")
    
    def classify_log(self, log_message: str) -> str:
        """
        Classify a log message using Ollama
        
        Args:
            log_message: The log message to classify
            
        Returns:
            Classification label
        """
        
        # Create a focused prompt for log classification
        prompt = f"""You are a log analysis expert. Classify this log message into one of these categories:

Categories:
- Workflow Error: Business process failures
- Deprecation Warning: Deprecated feature usage warnings
if you can't classify, respond with "Unknown".
Respond with ONLY the category name (e.g., "Critical Error"), no explanation.

Log message: "{log_message}"
"""

        try:
            # Make request to Ollama
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Low temperature for consistent classification
                    "top_p": 0.9,
                    "num_predict": 20    # Limit response length
                }
            }
            
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                classification = result.get('response', '').strip()
                
                # Clean up the response
                classification = self._clean_classification(classification)
                return classification
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return "Unknown"
                
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return "Unknown"
        except Exception as e:
            print(f"Classification error: {e}")
            return "Unknown"
    
    def _clean_classification(self, classification: str) -> str:
        """Clean and validate the classification response"""
        
        # Remove quotes, extra whitespace, and common prefixes
        classification = re.sub(r'^["\']|["\']$', '', classification.strip())
        classification = re.sub(r'^(Category:|Classification:|Answer:)\s*', '', classification, flags=re.IGNORECASE)
        
        # Valid categories
        valid_categories = {
            "Workflow Error", "Deprecation Warning"
        }
        
        # Check if response matches any valid category (case insensitive)
        for category in valid_categories:
            if category.lower() in classification.lower():
                return category
        
        # If no exact match, return the cleaned response or "Unknown"
        return classification if len(classification) < 50 else "Unknown"

def llm_classification(log_message: str, model_name: str = "llama3.1:8b") -> str:
    """
    Convenience function for single log classification
    
    Args:
        log_message: The log message to classify
        model_name: Ollama model name
        
    Returns:
        Classification label
    """
    processor = OllamaLLMProcessor(model_name=model_name)
    return processor.classify_log(log_message)

if __name__ == "__main__":
    # Test with sample logs
    processor = OllamaLLMProcessor()
    
    test_logs = [
        "Lead conversion failed for prospect ID 7842 due to missing contact information", # Workflow Error
        "Case escalation for ticket ID 7324 failed because the assigned support agent is no longer active.", # Workflow Error
        "API endpoint 'getCustomerDetails' is deprecated and will be removed in version 3.2. Use 'fetchCustomerInfo' instead.", # Deprecation Warning
        "Customer follow-up process for lead ID 5621 failed due to missing next action", # Workflow Error
        "Escalation rule execution failed for ticket ID 9807 - undefined escalation level.", # Workflow Error
        "The 'ExportToCSV' feature is outdated. Please migrate to 'ExportToXLSX' by the end of Q3." # Deprecation Warning
    ]
    
    for log in test_logs:
        classification = processor.classify_log(log)
        print(f"Log: {log}\nClassified as: {classification}\n")