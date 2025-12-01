"""
Core chatbot logic for TalentScout Hiring Assistant
Updated to support multiple LLM providers (Groq, OpenAI, HuggingFace)
"""

from typing import Dict, Any, List, Tuple, Optional
from config import ConversationState, EXIT_KEYWORDS
from prompts import (
    SYSTEM_PROMPT, GREETING_PROMPT, COLLECT_EMAIL_PROMPT,
    COLLECT_PHONE_PROMPT, COLLECT_EXPERIENCE_PROMPT,
    COLLECT_POSITION_PROMPT, COLLECT_LOCATION_PROMPT,
    COLLECT_TECH_STACK_PROMPT, GENERATE_QUESTIONS_PROMPT,
    COMPLETION_PROMPT, FALLBACK_PROMPT, OFFTOPIC_REDIRECT_PROMPT
)
from utils import (
    validate_email, validate_phone, validate_experience,
    is_exit_command, extract_tech_stack, save_candidate_data,
    sanitize_input
)
from llm_providers import LLMProviderFactory, BaseLLMProvider


class HiringAssistant:
    """
    Main chatbot class that handles conversation flow and LLM interactions.
    Supports multiple LLM providers through abstraction layer.
    """
    
    def __init__(self, provider: str = None):
        """
        Initialize the Hiring Assistant.
        
        Args:
            provider: LLM provider to use ('groq', 'openai', 'huggingface', or 'auto')
        """
        self.llm_provider: BaseLLMProvider = LLMProviderFactory.create(provider)
        self.reset_conversation()
        print(f"Using LLM Provider: {self.llm_provider.name}")
    
    def reset_conversation(self):
        """Reset the conversation state and candidate information."""
        self.state = ConversationState.GREETING
        self.candidate_info = {
            "name": None,
            "email": None,
            "phone": None,
            "experience_years": None,
            "desired_position": None,
            "location": None,
            "tech_stack": None,
            "tech_stack_raw": None,
            "technical_answers": []
        }
        self.technical_questions = []
        self.current_question_index = 0
        self.conversation_history = []
    
    def switch_provider(self, provider: str):
        """
        Switch to a different LLM provider.
        
        Args:
            provider: New provider name
        """
        self.llm_provider = LLMProviderFactory.create(provider)
        print(f"Switched to LLM Provider: {self.llm_provider.name}")
    
    def get_provider_name(self) -> str:
        """Get the current LLM provider name."""
        return self.llm_provider.name
    
    def _call_llm(self, prompt: str, system_context: str = None) -> str:
        """
        Make a call to the LLM API.
        
        Args:
            prompt: The user prompt
            system_context: Optional system context override
            
        Returns:
            str: LLM response text
        """
        system_msg = system_context or SYSTEM_PROMPT.format(
            state=self.state,
            candidate_info=self._get_safe_candidate_info()
        )
        
        # Call the LLM provider
        response = self.llm_provider.generate(prompt, system_msg)
        
        # If LLM fails, use fallback
        if response is None:
            return self._get_fallback_response(prompt)
        
        return response
    
    def _get_fallback_response(self, context: str) -> str:
        """
        Provide fallback responses when LLM is unavailable.
        
        Args:
            context: Context for generating appropriate fallback
            
        Returns:
            str: Fallback response
        """
        fallbacks = {
            ConversationState.GREETING: (
                "👋 Welcome to TalentScout! I'm your AI hiring assistant.\n\n"
                "I'll help guide you through our initial screening process. "
                "This will take about 5-10 minutes.\n\n"
                "**Let's start! What is your full name?**"
            ),
            ConversationState.COLLECTING_NAME: (
                f"Nice to meet you! 😊\n\n"
                "Could you please provide your **email address**?"
            ),
            ConversationState.COLLECTING_EMAIL: (
                "Great, thank you!\n\n"
                "What's the best **phone number** to reach you?"
            ),
            ConversationState.COLLECTING_PHONE: (
                "Perfect!\n\n"
                "How many **years of experience** do you have in the tech industry?"
            ),
            ConversationState.COLLECTING_EXPERIENCE: (
                "Excellent experience!\n\n"
                "What **position(s)** are you interested in applying for?\n"
                "(e.g., Software Engineer, Full Stack Developer, Data Scientist)"
            ),
            ConversationState.COLLECTING_POSITION: (
                "Great choice!\n\n"
                "What is your **current location**? (City, Country)"
            ),
            ConversationState.COLLECTING_LOCATION: (
                "Thank you!\n\n"
                "Now, please list your **tech stack** including:\n"
                "• Programming languages\n"
                "• Frameworks\n"
                "• Databases\n"
                "• Tools & technologies\n\n"
                "Be as specific as possible - this helps us generate relevant questions!"
            ),
            ConversationState.TECHNICAL_QUESTIONS: (
                "Thank you for your answer! Let me ask the next question."
            ),
            ConversationState.COMPLETED: (
                "🎉 **Thank you for completing the screening!**\n\n"
                "Your information has been recorded successfully. "
                "Our recruitment team will review your profile and "
                "contact you within **3-5 business days**.\n\n"
                "We appreciate your interest in joining through TalentScout. "
                "Good luck! 🍀"
            )
        }
        return fallbacks.get(
            self.state, 
            "I apologize, but I'm having trouble processing that. Could you please try again?"
        )
    
    def _get_safe_candidate_info(self) -> Dict[str, Any]:
        """
        Get candidate info with sensitive data masked.
        
        Returns:
            dict: Masked candidate information
        """
        safe_info = self.candidate_info.copy()
        if safe_info.get('email'):
            safe_info['email'] = '[PROVIDED]'
        if safe_info.get('phone'):
            safe_info['phone'] = '[PROVIDED]'
        return safe_info
    
    def _generate_technical_questions(self) -> List[str]:
        """
        Generate technical questions based on candidate's tech stack.
        
        Returns:
            list: List of technical questions
        """
        prompt = GENERATE_QUESTIONS_PROMPT.format(
            tech_stack=self.candidate_info['tech_stack_raw'],
            num_questions=5,
            position=self.candidate_info['desired_position'],
            experience=self.candidate_info['experience_years']
        )
        
        response = self._call_llm(prompt)
        
        # Parse questions from response
        questions = []
        lines = response.split('\n')
        current_question = ""
        
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                if current_question:
                    questions.append(current_question.strip())
                # Clean the line prefix
                current_question = line.lstrip('0123456789.-•) ').strip()
            elif current_question and line:
                current_question += " " + line
        
        if current_question:
            questions.append(current_question.strip())
        
        # Filter out empty questions and limit
        questions = [q for q in questions if len(q) > 10]
        
        # Fallback questions if parsing failed
        if len(questions) < 3:
            questions = self._get_fallback_questions()
        
        return questions[:5]  # Limit to 5 questions
    
    def _get_fallback_questions(self) -> List[str]:
        """
        Get fallback technical questions based on tech stack.
        
        Returns:
            list: Default technical questions
        """
        tech = self.candidate_info.get('tech_stack_raw', '').lower()
        questions = []
        
        # Python questions
        if 'python' in tech:
            questions.extend([
                "Explain the difference between a list and a tuple in Python. When would you use each?",
                "What are Python decorators and can you give an example of when you'd use one?",
                "How does Python's garbage collection work? What is reference counting?"
            ])
        
        # JavaScript/Frontend questions
        if any(t in tech for t in ['javascript', 'react', 'angular', 'vue', 'node']):
            questions.extend([
                "Explain the concept of closures in JavaScript with a practical example.",
                "What is the event loop in JavaScript and how does it handle asynchronous operations?",
                "Describe the difference between '==' and '===' in JavaScript."
            ])
        
        # React specific
        if 'react' in tech:
            questions.extend([
                "Explain the Virtual DOM in React and how it improves performance.",
                "What are React Hooks? Explain useState and useEffect with examples.",
                "How do you handle state management in large React applications?"
            ])
        
        # Database questions
        if any(t in tech for t in ['sql', 'mysql', 'postgresql', 'database', 'mongodb']):
            questions.extend([
                "Explain the difference between SQL and NoSQL databases. When would you choose one over the other?",
                "What are database indexes and how do they improve query performance?",
                "Describe ACID properties in databases and why they're important."
            ])
        
        # DevOps/Cloud questions
        if any(t in tech for t in ['docker', 'kubernetes', 'aws', 'azure', 'devops']):
            questions.extend([
                "Explain the difference between containers and virtual machines.",
                "What is CI/CD and why is it important in modern software development?",
                "Describe your experience with cloud services and infrastructure as code."
            ])
        
        # Java questions
        if 'java' in tech:
            questions.extend([
                "Explain the difference between an abstract class and an interface in Java.",
                "What is the Java Virtual Machine (JVM) and how does it work?",
                "Describe the concept of multithreading in Java and how you handle synchronization."
            ])
        
        # Machine Learning questions
        if any(t in tech for t in ['machine learning', 'ml', 'tensorflow', 'pytorch', 'data science']):
            questions.extend([
                "Explain the difference between supervised and unsupervised learning with examples.",
                "What is overfitting and how do you prevent it?",
                "Describe a machine learning project you've worked on and the challenges you faced."
            ])
        
        # Generic fallback questions (if no specific tech matched)
        if len(questions) < 3:
            questions.extend([
                "Describe a challenging technical problem you solved recently. What was your approach?",
                "How do you ensure code quality in your projects? What practices do you follow?",
                "Explain your experience with version control systems and collaborative development.",
                "How do you approach learning new technologies or frameworks?",
                "Describe your debugging process when encountering a difficult bug."
            ])
        
        return questions[:5]
    
    def process_input(self, user_input: str) -> Tuple[str, bool]:
        """
        Process user input and return appropriate response.
        
        Args:
            user_input: The user's input text
            
        Returns:
            tuple: (response_text, is_conversation_ended)
        """
        # Sanitize input
        user_input = sanitize_input(user_input)
        
        # Check for exit commands
        if is_exit_command(user_input):
            return self._handle_exit(), True
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_input,
            "state": self.state
        })
        
        # Process based on current state
        response = self._process_state(user_input)
        
        # Add response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response,
            "state": self.state
        })
        
        is_ended = self.state == ConversationState.COMPLETED
        
        return response, is_ended
    
    def _process_state(self, user_input: str) -> str:
        """
        Process input based on current conversation state.
        
        Args:
            user_input: The user's input
            
        Returns:
            str: Response text
        """
        if self.state == ConversationState.GREETING:
            return self._handle_greeting()
        
        elif self.state == ConversationState.COLLECTING_NAME:
            return self._handle_name(user_input)
        
        elif self.state == ConversationState.COLLECTING_EMAIL:
            return self._handle_email(user_input)
        
        elif self.state == ConversationState.COLLECTING_PHONE:
            return self._handle_phone(user_input)
        
        elif self.state == ConversationState.COLLECTING_EXPERIENCE:
            return self._handle_experience(user_input)
        
        elif self.state == ConversationState.COLLECTING_POSITION:
            return self._handle_position(user_input)
        
        elif self.state == ConversationState.COLLECTING_LOCATION:
            return self._handle_location(user_input)
        
        elif self.state == ConversationState.COLLECTING_TECH_STACK:
            return self._handle_tech_stack(user_input)
        
        elif self.state == ConversationState.TECHNICAL_QUESTIONS:
            return self._handle_technical_answer(user_input)
        
        else:
            return self._get_fallback_response("")
    
    def _handle_greeting(self) -> str:
        """Handle the greeting state."""
        response = self._call_llm(GREETING_PROMPT)
        self.state = ConversationState.COLLECTING_NAME
        return response
    
    def _handle_name(self, user_input: str) -> str:
        """Handle name collection."""
        # Basic validation - name should have at least 2 characters
        name = user_input.strip()
        if len(name) < 2:
            return "I didn't quite catch that. Could you please tell me your **full name**?"
        
        # Clean up the name (capitalize properly)
        self.candidate_info['name'] = name.title()
        self.state = ConversationState.COLLECTING_EMAIL
        
        prompt = COLLECT_EMAIL_PROMPT.format(name=self.candidate_info['name'])
        return self._call_llm(prompt)
    
    def _handle_email(self, user_input: str) -> str:
        """Handle email collection."""
        email = user_input.strip().lower()
        
        if not validate_email(email):
            return (
                "That doesn't appear to be a valid email address. 📧\n\n"
                "Please provide a valid email in the format: **example@domain.com**"
            )
        
        self.candidate_info['email'] = email
        self.state = ConversationState.COLLECTING_PHONE
        
        prompt = COLLECT_PHONE_PROMPT.format(email="[provided]")
        return self._call_llm(prompt)
    
    def _handle_phone(self, user_input: str) -> str:
        """Handle phone number collection."""
        phone = user_input.strip()
        
        if not validate_phone(phone):
            return (
                "That doesn't appear to be a valid phone number. 📱\n\n"
                "Please provide a phone number with at least 10 digits.\n"
                "Example: +1-555-123-4567 or 5551234567"
            )
        
        self.candidate_info['phone'] = phone
        self.state = ConversationState.COLLECTING_EXPERIENCE
        
        return self._call_llm(COLLECT_EXPERIENCE_PROMPT)
    
    def _handle_experience(self, user_input: str) -> str:
        """Handle experience collection."""
        years = validate_experience(user_input)
        
        if years is None:
            return (
                "I couldn't understand that. 🤔\n\n"
                "Please tell me your years of experience as a number.\n"
                "Examples: '5 years', '3', 'about 2 years'"
            )
        
        self.candidate_info['experience_years'] = years
        self.state = ConversationState.COLLECTING_POSITION
        
        prompt = COLLECT_POSITION_PROMPT.format(years=years)
        return self._call_llm(prompt)
    
    def _handle_position(self, user_input: str) -> str:
        """Handle desired position collection."""
        position = user_input.strip()
        
        if len(position) < 2:
            return (
                "Could you please specify what position(s) you're interested in? 🎯\n\n"
                "Examples:\n"
                "• Software Engineer\n"
                "• Full Stack Developer\n"
                "• Data Scientist\n"
                "• DevOps Engineer"
            )
        
        self.candidate_info['desired_position'] = position
        self.state = ConversationState.COLLECTING_LOCATION
        
        prompt = COLLECT_LOCATION_PROMPT.format(position=self.candidate_info['desired_position'])
        return self._call_llm(prompt)
    
    def _handle_location(self, user_input: str) -> str:
        """Handle location collection."""
        location = user_input.strip()
        
        if len(location) < 2:
            return (
                "Could you please provide your current location? 📍\n\n"
                "Examples: 'New York, USA', 'London, UK', 'Bangalore, India'"
            )
        
        self.candidate_info['location'] = location
        self.state = ConversationState.COLLECTING_TECH_STACK
        
        return self._call_llm(COLLECT_TECH_STACK_PROMPT)
    
    def _handle_tech_stack(self, user_input: str) -> str:
        """Handle tech stack collection."""
        tech_stack = user_input.strip()
        
        if len(tech_stack) < 5:
            return (
                "Could you provide more details about your tech stack? 💻\n\n"
                "Please list:\n"
                "• **Programming languages** (Python, JavaScript, Java, etc.)\n"
                "• **Frameworks** (React, Django, Spring, etc.)\n"
                "• **Databases** (MySQL, MongoDB, PostgreSQL, etc.)\n"
                "• **Tools** (Docker, Git, AWS, etc.)"
            )
        
        self.candidate_info['tech_stack_raw'] = tech_stack
        self.candidate_info['tech_stack'] = extract_tech_stack(tech_stack)
        
        # Generate technical questions
        self.technical_questions = self._generate_technical_questions()
        self.current_question_index = 0
        self.state = ConversationState.TECHNICAL_QUESTIONS
        
        # Present first question
        intro = (
            f"Excellent! 🎯 Based on your tech stack, I have **{len(self.technical_questions)} "
            f"technical questions** for you.\n\n"
            f"Take your time with each answer. Here's the first one:\n\n"
            f"**Question 1/{len(self.technical_questions)}:**\n{self.technical_questions[0]}"
        )
        
        return intro
    
    def _handle_technical_answer(self, user_input: str) -> str:
        """Handle technical question answers."""
        # Store the answer
        self.candidate_info['technical_answers'].append({
            "question": self.technical_questions[self.current_question_index],
            "answer": user_input.strip()
        })
        
        self.current_question_index += 1
        
        # Check if there are more questions
        if self.current_question_index < len(self.technical_questions):
            q_num = self.current_question_index + 1
            total = len(self.technical_questions)
            
            response = (
                f"✅ Thank you for your answer!\n\n"
                f"**Question {q_num}/{total}:**\n"
                f"{self.technical_questions[self.current_question_index]}"
            )
            return response
        else:
            # All questions answered - complete the screening
            return self._complete_screening()
    
    def _complete_screening(self) -> str:
        """Complete the screening process."""
        self.state = ConversationState.COMPLETED
        
        # Save candidate data
        save_candidate_data(self.candidate_info)
        
        # Generate completion message
        response = self._call_llm(COMPLETION_PROMPT)
        
        return response
    
    def _handle_exit(self) -> str:
        """Handle conversation exit."""
        name = self.candidate_info.get('name', '')
        
        if name:
            return (
                f"Thank you for your time, **{name}**! 👋\n\n"
                f"If you'd like to complete the screening process later, "
                f"feel free to start a new conversation.\n\n"
                f"Have a great day! 🌟"
            )
        else:
            return (
                "Thank you for visiting TalentScout! 👋\n\n"
                "Feel free to return whenever you're ready to complete the screening.\n\n"
                "Have a great day! 🌟"
            )
    
    def get_greeting(self) -> str:
        """Get the initial greeting message."""
        return self._handle_greeting()
    
    def get_progress(self) -> Dict[str, Any]:
        """
        Get current progress in the screening process.
        
        Returns:
            dict: Progress information
        """
        states_order = [
            ConversationState.GREETING,
            ConversationState.COLLECTING_NAME,
            ConversationState.COLLECTING_EMAIL,
            ConversationState.COLLECTING_PHONE,
            ConversationState.COLLECTING_EXPERIENCE,
            ConversationState.COLLECTING_POSITION,
            ConversationState.COLLECTING_LOCATION,
            ConversationState.COLLECTING_TECH_STACK,
            ConversationState.TECHNICAL_QUESTIONS,
            ConversationState.COMPLETED
        ]
        
        current_index = states_order.index(self.state) if self.state in states_order else 0
        total_steps = len(states_order)
        
        return {
            "current_step": current_index + 1,
            "total_steps": total_steps,
            "percentage": int((current_index / (total_steps - 1)) * 100),
            "current_state": self.state
        }