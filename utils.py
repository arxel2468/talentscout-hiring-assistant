"""
Utility functions for TalentScout Hiring Assistant
"""

import re
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from config import EXIT_KEYWORDS, TECH_CATEGORIES

def validate_email(email: str) -> bool:
    """
    Validate email format using regex.
    
    Args:
        email: Email string to validate
        
    Returns:
        bool: True if valid email format, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))

def validate_phone(phone: str) -> bool:
    """
    Validate phone number format (flexible validation).
    
    Args:
        phone: Phone string to validate
        
    Returns:
        bool: True if valid phone format, False otherwise
    """
    # Remove common separators and check if remaining chars are digits
    cleaned = re.sub(r'[\s\-\(\)\+\.]', '', phone)
    return len(cleaned) >= 10 and cleaned.isdigit()

def validate_experience(experience: str) -> Optional[int]:
    """
    Extract years of experience from user input.
    
    Args:
        experience: User input about experience
        
    Returns:
        int or None: Years of experience if found, None otherwise
    """
    # Try to find numbers in the input
    numbers = re.findall(r'\d+', experience)
    if numbers:
        years = int(numbers[0])
        if 0 <= years <= 50:  # Reasonable range
            return years
    return None

def is_exit_command(text: str) -> bool:
    """
    Check if user wants to exit the conversation.
    
    Args:
        text: User input text
        
    Returns:
        bool: True if exit command detected, False otherwise
    """
    text_lower = text.lower().strip()
    return any(keyword in text_lower for keyword in EXIT_KEYWORDS)

def extract_tech_stack(text: str) -> Dict[str, list]:
    """
    Extract and categorize technologies from user input.
    
    Args:
        text: User input describing their tech stack
        
    Returns:
        dict: Categorized tech stack
    """
    text_lower = text.lower()
    extracted = {
        "programming_languages": [],
        "frameworks": [],
        "databases": [],
        "tools": []
    }
    
    for category, technologies in TECH_CATEGORIES.items():
        # Only use first 4 categories for display
        if category in extracted:
            for tech in technologies:
                if tech in text_lower:
                    extracted[category].append(tech.capitalize())
    
    return extracted

def save_candidate_data(candidate_info: Dict[str, Any], filename: str = "data/candidates.json") -> bool:
    """
    Save candidate information to JSON file (simulated database).
    
    Args:
        candidate_info: Dictionary containing candidate information
        filename: Path to the JSON file
        
    Returns:
        bool: True if save successful, False otherwise
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Load existing data or create new list
        data = []
        
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:  # Only parse if file is not empty
                        data = json.loads(content)
                        if not isinstance(data, list):
                            data = []
            except (json.JSONDecodeError, ValueError):
                # If JSON is invalid, start fresh
                print("Warning: Invalid JSON in candidates file, starting fresh.")
                data = []
        
        # Create a copy of candidate_info to avoid modifying original
        candidate_copy = candidate_info.copy()
        
        # Add timestamp and ID
        candidate_copy['timestamp'] = datetime.now().isoformat()
        candidate_copy['id'] = len(data) + 1
        
        # Append new candidate
        data.append(candidate_copy)
        
        # Save back to file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully saved candidate data. Total candidates: {len(data)}")
        return True
        
    except Exception as e:
        print(f"Error saving candidate data: {e}")
        return False

def mask_sensitive_data(data: str, data_type: str) -> str:
    """
    Mask sensitive data for display purposes.
    
    Args:
        data: The sensitive data to mask
        data_type: Type of data ('email', 'phone')
        
    Returns:
        str: Masked data string
    """
    if not data:
        return ""
        
    if data_type == 'email':
        parts = data.split('@')
        if len(parts) == 2:
            username = parts[0]
            if len(username) > 2:
                masked_username = username[0] + '*' * (len(username) - 2) + username[-1]
            else:
                masked_username = username[0] + '*'
            return f"{masked_username}@{parts[1]}"
    elif data_type == 'phone':
        if len(data) >= 4:
            return '*' * (len(data) - 4) + data[-4:]
    
    return data

def format_tech_stack_display(tech_stack: Dict[str, list]) -> str:
    """
    Format tech stack dictionary for display.
    
    Args:
        tech_stack: Categorized tech stack dictionary
        
    Returns:
        str: Formatted string for display
    """
    if not tech_stack:
        return "No specific technologies identified"
        
    lines = []
    category_names = {
        "programming_languages": "💻 Languages",
        "frameworks": "🔧 Frameworks",
        "databases": "🗄️ Databases",
        "tools": "🛠️ Tools"
    }
    
    for category, techs in tech_stack.items():
        if techs and category in category_names:
            name = category_names[category]
            lines.append(f"{name}: {', '.join(techs)}")
    
    return '\n'.join(lines) if lines else "No specific technologies identified"

def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent injection attacks.
    
    Args:
        text: Raw user input
        
    Returns:
        str: Sanitized input
    """
    if not text:
        return ""
    # Remove potentially harmful characters
    sanitized = re.sub(r'[<>{}[\]\\]', '', text)
    # Limit length
    return sanitized[:1000].strip()