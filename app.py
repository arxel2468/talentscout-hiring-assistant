"""
TalentScout Hiring Assistant - Main Streamlit Application
Supports multiple LLM providers: Groq, OpenAI, HuggingFace
"""

import streamlit as st
from chatbot import HiringAssistant
from llm_providers import LLMProviderFactory
from utils import format_tech_stack_display, mask_sensitive_data
from config import APP_TITLE, APP_ICON, ConversationState, LLMProvider

# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    /* Main container styling */
    .main-header {
        text-align: center;
        padding: 1.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    /* Chat styling */
    .stChatMessage {
        border-radius: 15px;
    }
    
    /* Sidebar styling */
    .provider-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    .provider-groq {
        background: linear-gradient(90deg, #f97316, #ea580c);
        color: white;
    }
    
    .provider-openai {
        background: linear-gradient(90deg, #10a37f, #0d8c6d);
        color: white;
    }
    
    .provider-huggingface {
        background: linear-gradient(90deg, #ff9d00, #ff6b00);
        color: white;
    }
    
    .provider-fallback {
        background: #6b7280;
        color: white;
    }
    
    /* Progress section */
    .progress-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    
    /* Info cards */
    .info-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin-bottom: 0.5rem;
    }
    
    /* Start button styling */
    .stButton > button {
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    /* Welcome box */
    .welcome-box {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = HiringAssistant()
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'conversation_started' not in st.session_state:
        st.session_state.conversation_started = False
    if 'conversation_ended' not in st.session_state:
        st.session_state.conversation_ended = False


def display_header():
    """Display the application header."""
    st.markdown("""
        <div class="main-header">
            <h1>🎯 TalentScout</h1>
            <p>AI-Powered Hiring Assistant</p>
        </div>
    """, unsafe_allow_html=True)


def get_provider_badge(provider_name: str) -> str:
    """Get HTML badge for the current provider."""
    provider_classes = {
        "Groq": "provider-groq",
        "OpenAI": "provider-openai",
        "HuggingFace": "provider-huggingface",
        "Fallback (No API)": "provider-fallback"
    }
    
    css_class = provider_classes.get(provider_name, "provider-fallback")
    return f'<span class="provider-badge {css_class}">🤖 {provider_name}</span>'


def display_sidebar():
    """Display sidebar with progress, provider info, and controls."""
    with st.sidebar:
        # Provider info
        st.markdown("### 🔌 LLM Provider")
        provider_name = st.session_state.chatbot.get_provider_name()
        st.markdown(get_provider_badge(provider_name), unsafe_allow_html=True)
        
        # Provider selector
        available_providers = LLMProviderFactory.get_available_providers()
        provider_options = ["auto"] + [p["name"] for p in available_providers if p["available"]]
        
        if len(provider_options) > 1:
            selected_provider = st.selectbox(
                "Switch Provider",
                options=provider_options,
                index=0,
                key="provider_selector",
                help="Select which LLM provider to use"
            )
            
            if st.button("Apply", use_container_width=True, key="apply_provider_btn"):
                st.session_state.chatbot.switch_provider(selected_provider)
                st.rerun()
        
        # Show available providers status
        with st.expander("📋 Provider Status"):
            for provider in available_providers:
                status = "✅" if provider["available"] else "❌"
                st.write(f"{status} {provider['display_name']}")
        
        st.markdown("---")
        
        # Progress section
        st.markdown("### 📊 Screening Progress")
        
        progress = st.session_state.chatbot.get_progress()
        
        # Progress bar
        st.progress(progress['percentage'] / 100)
        st.caption(f"Step {progress['current_step']} of {progress['total_steps']}")
        
        # Current stage indicator
        stage_names = {
            ConversationState.GREETING: "👋 Welcome",
            ConversationState.COLLECTING_NAME: "📝 Name",
            ConversationState.COLLECTING_EMAIL: "📧 Email",
            ConversationState.COLLECTING_PHONE: "📱 Phone",
            ConversationState.COLLECTING_EXPERIENCE: "💼 Experience",
            ConversationState.COLLECTING_POSITION: "🎯 Position",
            ConversationState.COLLECTING_LOCATION: "📍 Location",
            ConversationState.COLLECTING_TECH_STACK: "💻 Tech Stack",
            ConversationState.TECHNICAL_QUESTIONS: "❓ Technical Q&A",
            ConversationState.COMPLETED: "✅ Complete"
        }
        
        current_stage = stage_names.get(progress['current_state'], "In Progress")
        st.info(f"**Current:** {current_stage}")
        
        st.markdown("---")
        
        # Collected information
        st.markdown("### 📋 Candidate Info")
        candidate = st.session_state.chatbot.candidate_info
        
        info_items = [
            ("👤 Name", candidate.get('name')),
            ("📧 Email", mask_sensitive_data(candidate.get('email', ''), 'email') if candidate.get('email') else None),
            ("📱 Phone", mask_sensitive_data(candidate.get('phone', ''), 'phone') if candidate.get('phone') else None),
            ("💼 Experience", f"{candidate.get('experience_years')} years" if candidate.get('experience_years') is not None else None),
            ("🎯 Position", candidate.get('desired_position')),
            ("📍 Location", candidate.get('location')),
        ]
        
        for label, value in info_items:
            if value:
                st.markdown(f"**{label}:** {value}")
        
        if candidate.get('tech_stack'):
            st.markdown("**💻 Tech Stack:**")
            st.caption(format_tech_stack_display(candidate['tech_stack']))
        
        st.markdown("---")
        
        # Reset button in sidebar
        if st.button("🔄 Start New Screening", use_container_width=True, key="sidebar_reset_btn"):
            reset_conversation()
        
        # Help section
        with st.expander("ℹ️ Help & Tips"):
            st.markdown("""
            **Tips for candidates:**
            - Answer questions clearly and completely
            - Be specific about your tech stack
            - Take your time with technical questions
            
            **Commands:**
            - Type `exit`, `quit`, or `bye` to end
            
            **Privacy:**
            - Your data is handled securely
            - Sensitive info is masked in the UI
            """)


def reset_conversation():
    """Reset the conversation state."""
    st.session_state.chatbot.reset_conversation()
    st.session_state.messages = []
    st.session_state.conversation_started = False
    st.session_state.conversation_ended = False
    st.rerun()


def display_chat():
    """Display the chat interface."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def handle_user_input(user_input: str):
    """
    Process user input and get chatbot response.
    
    Args:
        user_input: The user's message
    """
    # Add user message to chat
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    
    # Get chatbot response
    with st.spinner("Thinking..."):
        response, is_ended = st.session_state.chatbot.process_input(user_input)
    
    # Add assistant response to chat
    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })
    
    # Check if conversation ended
    if is_ended:
        st.session_state.conversation_ended = True


def display_welcome_screen():
    """Display the welcome screen before conversation starts."""
    st.markdown("""
    <div class="welcome-box">
        <h2>👋 Welcome to TalentScout!</h2>
        <p>Your AI-powered hiring assistant</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Start Screening Process", use_container_width=True, type="primary", key="start_screening_btn"):
            # Get greeting from chatbot
            with st.spinner("Initializing..."):
                greeting = st.session_state.chatbot.get_greeting()
            st.session_state.messages.append({
                "role": "assistant",
                "content": greeting
            })
            st.session_state.conversation_started = True
            st.rerun()
    
    # Information cards
    st.markdown("### What to expect:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        📝 **Information Gathering**
        - Basic contact details
        - Professional experience
        - Desired position
        """)
        
        st.markdown("""
        💻 **Technical Assessment**
        - Skills-based questions
        - Tailored to your tech stack
        - 3-5 questions total
        """)
    
    with col2:
        st.markdown("""
        ⏱️ **Time Required**
        - About 5-10 minutes
        - Go at your own pace
        - Exit anytime with 'quit'
        """)
        
        st.markdown("""
        🔒 **Privacy First**
        - Secure data handling
        - GDPR compliant
        - Data used only for screening
        """)


def display_completion_screen():
    """Display the completion screen."""
    st.success("✅ Screening Complete!")
    st.balloons()
    
    # Summary
    candidate = st.session_state.chatbot.candidate_info
    
    with st.expander("📄 View Your Summary", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Personal Information**")
            st.write(f"- **Name:** {candidate.get('name', 'N/A')}")
            st.write(f"- **Location:** {candidate.get('location', 'N/A')}")
            st.write(f"- **Experience:** {candidate.get('experience_years', 'N/A')} years")
        
        with col2:
            st.markdown("**Professional Details**")
            st.write(f"- **Position:** {candidate.get('desired_position', 'N/A')}")
            tech_stack_raw = candidate.get('tech_stack_raw', 'N/A')
            if tech_stack_raw and len(tech_stack_raw) > 50:
                tech_stack_raw = tech_stack_raw[:50] + "..."
            st.write(f"- **Tech Stack:** {tech_stack_raw}")
    
    # Technical Q&A Summary
    if candidate.get('technical_answers'):
        with st.expander("📝 Technical Q&A Summary"):
            for i, qa in enumerate(candidate['technical_answers'], 1):
                st.markdown(f"**Q{i}:** {qa['question']}")
                st.markdown(f"**A:** {qa['answer'][:200]}{'...' if len(qa['answer']) > 200 else ''}")
                st.markdown("---")
    
    # Next steps
    st.info("""
    **What happens next?**
    1. Our recruitment team will review your profile
    2. You'll receive an email within 3-5 business days
    3. If selected, we'll schedule a detailed interview
    """)
    
    # Action button - using unique key
    if st.button("🔄 Start New Screening", use_container_width=True, key="completion_reset_btn"):
        reset_conversation()


def main():
    """Main application function."""
    # Initialize session state
    initialize_session_state()
    
    # Display header
    display_header()
    
    # Display sidebar
    display_sidebar()
    
    # Main content area
    if not st.session_state.conversation_started:
        display_welcome_screen()
    elif st.session_state.conversation_ended:
        # Show chat history
        st.markdown("### 💬 Conversation History")
        display_chat()
        st.markdown("---")
        display_completion_screen()
    else:
        # Active conversation
        st.markdown("### 💬 Chat with our Hiring Assistant")
        
        # Display chat history
        display_chat()
        
        # Chat input
        if user_input := st.chat_input("Type your response here...", key="chat_input"):
            handle_user_input(user_input)
            st.rerun()


if __name__ == "__main__":
    main()