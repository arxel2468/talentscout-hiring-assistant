"""
LLM Provider abstraction layer for TalentScout Hiring Assistant.
Supports: Groq, OpenAI, and HuggingFace Inference API.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict
import requests

from config import (
    LLMProvider,
    OPENAI_API_KEY, OPENAI_MODEL,
    GROQ_API_KEY, GROQ_MODEL,
    HUGGINGFACE_API_KEY, HUGGINGFACE_MODEL,
    MAX_TOKENS, TEMPERATURE, TOP_P,
    get_available_provider
)


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = None) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt for context
            
        Returns:
            str: The generated response
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available (has valid API key)."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the provider name."""
        pass


class GroqProvider(BaseLLMProvider):
    """
    Groq LLM Provider - Fast and free inference!
    
    Groq provides extremely fast inference for open-source models.
    Free tier available with generous rate limits.
    """
    
    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize Groq provider.
        
        Args:
            api_key: Groq API key (optional, uses env var if not provided)
            model: Model to use (optional, uses default if not provided)
        """
        self.api_key = api_key or GROQ_API_KEY
        self.model = model or GROQ_MODEL
        self.client = None
        
        if self.api_key:
            try:
                from groq import Groq
                self.client = Groq(api_key=self.api_key)
            except ImportError:
                print("Groq library not installed. Run: pip install groq")
            except Exception as e:
                print(f"Error initializing Groq client: {e}")
    
    def generate(self, prompt: str, system_prompt: str = None) -> str:
        """Generate response using Groq API."""
        if not self.client:
            return None
        
        try:
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Create completion (non-streaming for simplicity)
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
                top_p=TOP_P,
                stream=False
            )
            
            return completion.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"Groq API Error: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if Groq is available."""
        return self.client is not None
    
    @property
    def name(self) -> str:
        return "Groq"


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI LLM Provider.
    
    Uses OpenAI's GPT models (requires paid API key).
    """
    
    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key
            model: Model to use (e.g., 'gpt-3.5-turbo', 'gpt-4')
        """
        self.api_key = api_key or OPENAI_API_KEY
        self.model = model or OPENAI_MODEL
        self.client = None
        
        if self.api_key:
            try:
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
            except ImportError:
                print("OpenAI library not installed. Run: pip install openai")
            except Exception as e:
                print(f"Error initializing OpenAI client: {e}")
    
    def generate(self, prompt: str, system_prompt: str = None) -> str:
        """Generate response using OpenAI API."""
        if not self.client:
            return None
        
        try:
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"OpenAI API Error: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if OpenAI is available."""
        return self.client is not None
    
    @property
    def name(self) -> str:
        return "OpenAI"


class HuggingFaceProvider(BaseLLMProvider):
    """
    HuggingFace Inference API Provider.
    
    Uses HuggingFace's free Inference API for various open-source models.
    Note: Free tier has rate limits and may be slower.
    """
    
    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize HuggingFace provider.
        
        Args:
            api_key: HuggingFace API token
            model: Model ID to use
        """
        self.api_key = api_key or HUGGINGFACE_API_KEY
        self.model = model or HUGGINGFACE_MODEL
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model}"
        self.headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
    
    def generate(self, prompt: str, system_prompt: str = None) -> str:
        """Generate response using HuggingFace Inference API."""
        if not self.api_key:
            return None
        
        try:
            # Format prompt for instruction-following models
            if system_prompt:
                full_prompt = f"""<s>[INST] {system_prompt}

{prompt} [/INST]"""
            else:
                full_prompt = f"<s>[INST] {prompt} [/INST]"
            
            payload = {
                "inputs": full_prompt,
                "parameters": {
                    "max_new_tokens": MAX_TOKENS,
                    "temperature": TEMPERATURE,
                    "top_p": TOP_P,
                    "do_sample": True,
                    "return_full_text": False
                }
            }
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "").strip()
                return str(result).strip()
            elif response.status_code == 503:
                # Model is loading
                return None
            else:
                print(f"HuggingFace API Error: {response.status_code} - {response.text}")
                return None
        
        except Exception as e:
            print(f"HuggingFace API Error: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if HuggingFace is available."""
        return bool(self.api_key)
    
    @property
    def name(self) -> str:
        return "HuggingFace"


class FallbackProvider(BaseLLMProvider):
    """
    Fallback provider that returns pre-defined responses.
    Used when no LLM API is available.
    """
    
    def __init__(self):
        """Initialize fallback provider."""
        pass
    
    def generate(self, prompt: str, system_prompt: str = None) -> str:
        """Return None to trigger fallback responses in chatbot."""
        return None
    
    def is_available(self) -> bool:
        """Fallback is always 'available' as last resort."""
        return True
    
    @property
    def name(self) -> str:
        return "Fallback (No API)"


class LLMProviderFactory:
    """
    Factory class to create and manage LLM providers.
    
    Automatically selects the best available provider or allows
    manual provider selection.
    """
    
    _providers = {
        LLMProvider.GROQ.value: GroqProvider,
        LLMProvider.OPENAI.value: OpenAIProvider,
        LLMProvider.HUGGINGFACE.value: HuggingFaceProvider,
    }
    
    @classmethod
    def create(cls, provider: str = None) -> BaseLLMProvider:
        """
        Create an LLM provider instance.
        
        Args:
            provider: Provider name ('groq', 'openai', 'huggingface', or 'auto')
                     If 'auto' or None, automatically selects best available.
        
        Returns:
            BaseLLMProvider: An instance of the appropriate provider
        """
        if provider is None or provider == "auto":
            provider = get_available_provider()
        
        if provider in cls._providers:
            instance = cls._providers[provider]()
            if instance.is_available():
                return instance
        
        # Try all providers in priority order
        for prov_name in [LLMProvider.GROQ.value, 
                          LLMProvider.OPENAI.value, 
                          LLMProvider.HUGGINGFACE.value]:
            if prov_name in cls._providers:
                instance = cls._providers[prov_name]()
                if instance.is_available():
                    return instance
        
        # Return fallback if nothing else works
        return FallbackProvider()
    
    @classmethod
    def get_available_providers(cls) -> List[Dict[str, str]]:
        """
        Get list of available providers with their status.
        
        Returns:
            List of dicts with provider info
        """
        available = []
        
        for name, provider_class in cls._providers.items():
            instance = provider_class()
            available.append({
                "name": name,
                "display_name": instance.name,
                "available": instance.is_available()
            })
        
        return available