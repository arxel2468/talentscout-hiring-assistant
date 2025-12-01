"""
Configuration settings for TalentScout Hiring Assistant
Supports multiple LLM providers: OpenAI, Groq, HuggingFace
"""

import os
from dotenv import load_dotenv
from enum import Enum

load_dotenv()

# =============================================================================
# LLM Provider Configuration
# =============================================================================

class LLMProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    GROQ = "groq"
    HUGGINGFACE = "huggingface"

# API Keys - Load from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")

# Default provider (will auto-detect based on available keys if not set)
DEFAULT_PROVIDER = os.getenv("LLM_PROVIDER", "auto")

# =============================================================================
# Model Configuration for Each Provider
# =============================================================================

# OpenAI Models
OPENAI_MODEL = "gpt-3.5-turbo"

# Groq Models (Free and fast!)
# Available models: llama-3.3-70b-versatile, llama-3.1-8b-instant, 
#                   mixtral-8x7b-32768, gemma2-9b-it
GROQ_MODEL = "llama-3.3-70b-versatile"

# HuggingFace Models (Inference API)
# Popular free models: mistralai/Mistral-7B-Instruct-v0.2, 
#                      microsoft/DialoGPT-large, google/flan-t5-xxl
HUGGINGFACE_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

# =============================================================================
# Generation Parameters
# =============================================================================

MAX_TOKENS = 1000
TEMPERATURE = 0.7
TOP_P = 0.9

# =============================================================================
# Application Settings
# =============================================================================

APP_TITLE = "TalentScout Hiring Assistant"
APP_ICON = "🎯"

# =============================================================================
# Conversation States
# =============================================================================

class ConversationState:
    GREETING = "greeting"
    COLLECTING_NAME = "collecting_name"
    COLLECTING_EMAIL = "collecting_email"
    COLLECTING_PHONE = "collecting_phone"
    COLLECTING_EXPERIENCE = "collecting_experience"
    COLLECTING_POSITION = "collecting_position"
    COLLECTING_LOCATION = "collecting_location"
    COLLECTING_TECH_STACK = "collecting_tech_stack"
    TECHNICAL_QUESTIONS = "technical_questions"
    COMPLETED = "completed"

# =============================================================================
# Exit Keywords
# =============================================================================

EXIT_KEYWORDS = [
    "quit", "exit", "bye", "goodbye", "end", "stop", 
    "cancel", "terminate", "close", "done"
]

# =============================================================================
# Tech Stack Categories
# =============================================================================

TECH_CATEGORIES = {
    "programming_languages": [
        "python", "java", "javascript", "typescript", "c++", "c#", 
        "ruby", "go", "rust", "php", "swift", "kotlin", "scala",
        "r", "matlab", "perl", "shell", "bash"
    ],
    "frameworks": [
        "django", "flask", "fastapi", "react", "angular", "vue", 
        "node.js", "express", "spring", "spring boot", "rails", 
        ".net", "nextjs", "nuxt", "svelte", "jquery", "bootstrap",
        "tailwind", "laravel", "symfony"
    ],
    "databases": [
        "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
        "sqlite", "oracle", "cassandra", "dynamodb", "firebase",
        "mariadb", "neo4j", "couchdb"
    ],
    "tools": [
        "docker", "kubernetes", "aws", "azure", "gcp", "git",
        "jenkins", "terraform", "ansible", "linux", "nginx",
        "apache", "kafka", "rabbitmq", "graphql", "rest api",
        "ci/cd", "github actions", "gitlab"
    ],
    "ai_ml": [
        "tensorflow", "pytorch", "keras", "scikit-learn", "pandas",
        "numpy", "opencv", "nltk", "spacy", "huggingface", "langchain",
        "machine learning", "deep learning", "nlp", "computer vision"
    ]
}

# =============================================================================
# Helper function to detect available provider
# =============================================================================

def get_available_provider() -> str:
    """
    Detect which LLM provider is available based on API keys.
    
    Returns:
        str: The provider name ('groq', 'openai', 'huggingface', or 'none')
    """
    if DEFAULT_PROVIDER != "auto":
        return DEFAULT_PROVIDER
    
    # Priority: Groq (free & fast) > OpenAI > HuggingFace
    if GROQ_API_KEY:
        return LLMProvider.GROQ.value
    elif OPENAI_API_KEY:
        return LLMProvider.OPENAI.value
    elif HUGGINGFACE_API_KEY:
        return LLMProvider.HUGGINGFACE.value
    else:
        return "none"