# 🎯 TalentScout Hiring Assistant

An intelligent AI-powered chatbot for initial candidate screening, built for TalentScout - a fictional recruitment agency specializing in technology placements.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.29+-red.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5/4-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Demo](#demo)
- [Installation](#installation)
- [Usage](#usage)
- [Technical Details](#technical-details)
- [Prompt Design](#prompt-design)
- [Challenges & Solutions](#challenges--solutions)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

TalentScout Hiring Assistant is a conversational AI chatbot designed to streamline the initial candidate screening process. It collects essential candidate information, assesses technical skills through dynamically generated questions, and provides a seamless, professional experience.

### Key Capabilities

- **Automated Information Gathering**: Collects name, contact details, experience, and preferences
- **Dynamic Technical Assessment**: Generates relevant technical questions based on declared tech stack
- **Context-Aware Conversations**: Maintains conversation flow and handles unexpected inputs gracefully
- **Data Privacy Compliance**: Implements secure handling of sensitive candidate information

## ✨ Features

### Core Features

| Feature | Description |
|---------|-------------|
| 👋 Smart Greeting | Personalized welcome message with process overview |
| 📝 Information Collection | Systematic gathering of candidate details with validation |
| 💻 Tech Stack Analysis | Intelligent parsing and categorization of technologies |
| ❓ Dynamic Questions | AI-generated technical questions tailored to skills |
| 🔄 Context Management | Seamless conversation flow with state tracking |
| 🛡️ Fallback Handling | Graceful handling of unexpected inputs |
| 📊 Progress Tracking | Visual progress indicator for candidates |

### Technical Features

- **Input Validation**: Email, phone, and experience validation
- **Data Sanitization**: Protection against injection attacks
- **Session Management**: Persistent conversation state
- **Error Handling**: Robust error management with fallbacks

## 🎬 Demo

[Add your demo link here - Loom video or live deployment URL]

### Screenshots

**Welcome Screen**
![Welcome Screen](screenshots/welcome.png)

**Chat Interface**
![Chat Interface](screenshots/chat.png)

**Technical Questions**
![Technical Questions](screenshots/questions.png)

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- OpenAI API key
- pip (Python package manager)

### Step-by-Step Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/talentscout-hiring-assistant.git
   cd talentscout-hiring-assistant

Create Virtual Environment

Bash

python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
Install Dependencies

Bash

pip install -r requirements.txt
Configure Environment Variables

Bash

# Copy example env file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your_api_key_here
Create Data Directory

Bash

mkdir -p data
Run the Application

Bash

streamlit run app.py
Access the Application

Open your browser and navigate to http://localhost:8501

📖 Usage
Starting a Screening Session
Click "Start Screening Process" on the welcome page
Follow the chatbot's prompts to provide your information
Answer technical questions based on your declared skills
Complete the screening and wait for follow-up
Conversation Commands
Command	Action
exit, quit, bye	End conversation gracefully
help	Get assistance (if stuck)
Example Conversation Flow
text

🤖 Assistant: Welcome to TalentScout! I'm your hiring assistant...
              May I have your full name to get started?

👤 User: John Smith

🤖 Assistant: Nice to meet you, John! Could you please provide your email?

👤 User: john.smith@email.com

🤖 Assistant: Thank you! What's the best phone number to reach you?

... [continues through all stages]
🔧 Technical Details
Architecture
text

┌─────────────────────────────────────────────────────────────┐
│                     Streamlit Frontend                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Header    │  │    Chat     │  │      Sidebar        │ │
│  │  Component  │  │  Interface  │  │  (Progress/Info)    │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Chatbot Engine                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │    State    │  │   Prompt    │  │      Response       │ │
│  │   Manager   │  │   Builder   │  │     Generator       │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                      OpenAI API                              │
│               (GPT-3.5-turbo / GPT-4)                       │
└─────────────────────────────────────────────────────────────┘
Libraries Used
Library	Purpose	Version
Streamlit	Web UI Framework	1.29.0
OpenAI	LLM API Client	1.6.1
python-dotenv	Environment Management	1.0.0
pydantic	Data Validation	2.5.2
regex	Pattern Matching	2023.10.3
File Structure
text

talentscout-hiring-assistant/
├── app.py              # Main Streamlit application
├── chatbot.py          # Core chatbot logic
├── prompts.py          # Prompt templates
├── utils.py            # Utility functions
├── config.py           # Configuration settings
├── requirements.txt    # Dependencies
├── .env.example        # Environment template
├── .gitignore          # Git ignore rules
├── README.md           # Documentation
└── data/
    └── candidates.json # Simulated data storage
State Machine
text

GREETING → COLLECTING_NAME → COLLECTING_EMAIL → COLLECTING_PHONE
                                                        ↓
COMPLETED ← TECHNICAL_QUESTIONS ← COLLECTING_TECH_STACK ← 
                                                        ↑
         COLLECTING_EXPERIENCE → COLLECTING_POSITION → COLLECTING_LOCATION
🎨 Prompt Design
Design Philosophy
Clarity: Each prompt has a single, clear purpose
Context-Awareness: Prompts include relevant conversation context
Guardrails: Built-in instructions to prevent off-topic responses
Flexibility: Prompts handle diverse inputs gracefully
Prompt Categories
1. System Prompt
Establishes the chatbot's persona and behavioral guidelines:

Python

SYSTEM_PROMPT = """You are an intelligent and professional Hiring Assistant 
for TalentScout. Your role is to:
1. Greet candidates warmly
2. Collect information systematically
3. Generate relevant technical questions
4. Maintain professional tone
5. Handle unexpected inputs gracefully
..."""
2. Information Collection Prompts
Sequential prompts for gathering candidate details:

Python

COLLECT_EMAIL_PROMPT = """The candidate's name is {name}. 
Thank them and ask for their email address professionally."""
3. Technical Question Generation
Dynamic prompt that adapts to candidate's tech stack:

Python

GENERATE_QUESTIONS_PROMPT = """Based on the candidate's tech stack: {tech_stack}
Generate exactly {num_questions} technical interview questions that:
1. Are specific to the technologies mentioned
2. Range from intermediate to advanced level
3. Test practical knowledge
..."""
Handling Edge Cases
Scenario	Handling Strategy
Invalid email format	Re-prompt with format example
Off-topic input	Politely redirect to current stage
Exit commands	Graceful conversation termination
Empty input	Request clarification
API failure	Fallback to pre-defined responses
🔐 Data Privacy
Compliance Measures
Data Minimization: Only collect necessary information
Secure Storage: Data stored locally in JSON (simulated)
Data Masking: Sensitive info masked in UI displays
No Persistence: Conversation data cleared on reset
Input Sanitization: All inputs sanitized before processing
GDPR Considerations
Candidate data is stored only with implicit consent (completing screening)
Data can be "deleted" by resetting the conversation
No data sharing with third parties
Transparent about data usage in greeting
🚧 Challenges & Solutions
Challenge 1: Maintaining Conversation Context
Problem: LLMs don't inherently remember previous messages.
Solution: Implemented a state machine with explicit context passing to each LLM call.

Challenge 2: Dynamic Question Generation
Problem: Generating relevant questions for diverse tech stacks.
Solution:

Created a comprehensive tech category mapping
Implemented fallback questions for unrecognized technologies
Used experience level to calibrate question difficulty
Challenge 3: Input Validation
Problem: Users provide information in various formats.
Solution: Created flexible validation functions with regex patterns that accept multiple formats.

Challenge 4: Handling Off-Topic Inputs
Problem: Users may ask unrelated questions or provide unexpected inputs.
Solution: Implemented fallback and redirect prompts that acknowledge input while guiding back to the screening process.

Challenge 5: API Rate Limits and Failures
Problem: OpenAI API may be unavailable or rate-limited.
Solution: Implemented comprehensive fallback responses for every conversation state.

🚀 Future Enhancements
Planned Features
 Sentiment Analysis: Gauge candidate emotional state
 Multilingual Support: Support for multiple languages
 Resume Parsing: Extract info from uploaded resumes
 Interview Scheduling: Integration with calendar systems
 Analytics Dashboard: Screening metrics and insights
Technical Improvements
 Database Integration: Replace JSON with PostgreSQL
 Caching: Implement response caching for common queries
 Authentication: Add recruiter login system
 Webhooks: Notify recruiters of completed screenings
🤝 Contributing
Contributions are welcome! Please follow these steps:

Fork the repository
Create a feature branch (git checkout -b feature/AmazingFeature)
Commit your changes (git commit -m 'Add some AmazingFeature')
Push to the branch (git push origin feature/AmazingFeature)
Open a Pull Request
📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

👤 Author
Your Name

GitHub: @yourusername
LinkedIn: Your LinkedIn
Email: your.email@example.com
🙏 Acknowledgments
OpenAI for the GPT API
Streamlit team for the amazing framework
TalentScout (fictional) for the project inspiration
Made with ❤️ for the AI/ML Intern Assignment


---

## 10. Running the Application

### Quick Start Commands

```bash
# 1. Set up environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables
cp .env.example .env
# Edit .env and add your OpenAI API key

# 4. Run the app
streamlit run app.py

Testing Without API Key
The application includes fallback responses, so it will work even without an OpenAI API key (with reduced functionality).

## 🔌 LLM Provider Support

TalentScout supports multiple LLM providers. Choose the one that works best for you:

| Provider | Cost | Speed | Quality | Setup Difficulty |
|----------|------|-------|---------|-----------------|
| **Groq** ⭐ | Free | Very Fast | Excellent | Easy |
| OpenAI | Paid | Fast | Excellent | Easy |
| HuggingFace | Free | Slower | Good | Easy |

### Recommended: Groq (Free & Fast!)

Groq offers free API access with extremely fast inference. Perfect for this project!

1. Go to [Groq Console](https://console.groq.com/keys)
2. Sign up for free
3. Create an API key
4. Add to your `.env` file:

GROQ_API_KEY=your_key_here


### Alternative: HuggingFace (Free)

1. Go to [HuggingFace](https://huggingface.co/settings/tokens)
2. Create an access token (free account)
3. Add to your `.env` file:

HUGGINGFACE_API_KEY=your_token_here


### Alternative: OpenAI (Paid)

1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create an API key (requires payment method)
3. Add to your `.env` file:
OPENAI_API_KEY=your_key_here



---

## How to Get Groq API Key (Step by Step)

1. **Go to Groq Cloud Console**: https://console.groq.com/
2. **Sign Up** (if you haven't): Click "Sign Up" and create an account (free!)
3. **Navigate to API Keys**: Click on "API Keys" in the sidebar
4. **Create New Key**: Click "Create API Key"
5. **Copy the Key**: Copy the generated key immediately (you won't see it again!)
6. **Add to .env file**: `GROQ_API_KEY=gsk_your_key_here`

## Testing Your Setup

```bash
# Quick test to verify Groq is working
python -c "
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

response = client.chat.completions.create(
    model='llama-3.3-70b-versatile',
    messages=[{'role': 'user', 'content': 'Say hello!'}],
    max_tokens=50
)
print('Success! Response:', response.choices[0].message.content)
"