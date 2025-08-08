import streamlit as st
import requests
import time

# --- Page Configuration ---
st.set_page_config(
    page_title="HR Resource Query Chatbot 🤖",
    page_icon="🤖",
    layout="wide"
)

# --- Helper Functions & Styling ---
def local_css():
    """Injects custom CSS for styling UI elements."""
    css = """
    <style>
        .employee-card {
            border-radius: 15px;
            border: 1px solid #e0e0e0;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease-in-out;
            background-color: #ffffff;
        }
        .employee-card:hover {
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
            transform: translateY(-5px);
            border-color: #4A90E2;
        }
        .employee-card h3 {
            color: #333;
            margin-bottom: 15px;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def stream_response(text):
    """Simulates a streaming response for the chatbot word by word."""
    for word in text.split():
        yield word + " "
        time.sleep(0.05)

def display_employee_card(card_data):
    """Creates a visually appealing, clickable card for an employee."""
    with st.container():
        st.markdown('<div class="employee-card">', unsafe_allow_html=True)
        st.subheader(f"👤 {card_data['name']}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**📅 Experience:** {card_data['experience_years']} years")
        with col2:
            if card_data['availability'] == 'available':
                st.success(f"**Status:** Available")
            else:
                st.warning(f"**Status:** {card_data['availability']}")

        with st.expander("🛠️ View Skills & Projects"):
            st.write(f"**Skills:** `{', '.join(card_data['skills'])}`")
            st.write(f"**Past Projects:**")
            for project in card_data['projects']:
                st.markdown(f"- *{project}*")

        st.markdown('</div>', unsafe_allow_html=True)

# --- Main App ---

local_css()

API_BASE_URL = "http://127.0.0.1:8000"

with st.sidebar:
    st.title("HR Assistant Pro 🤖")
    st.info("Welcome! This chatbot helps you find the right talent for your projects.")
    st.markdown("---")
    st.subheader("How to Use:")
    st.markdown("""
    1.  **Ask specific questions** about skills, experience, or projects.
    2.  **Use natural language** for queries.
    3.  **Engage in small talk!**
    """)
    st.markdown("---")
    st.success("The system is online and ready.")

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("HR Resource Query Chatbot")

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
        st.markdown(message["content"])
        if "cards" in message and message["cards"]:
            st.markdown("---")
            for card in message["cards"]:
                display_employee_card(card)

if prompt := st.chat_input("Ask me to find an employee..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("🤖 Thinking..."):
            try:
                response = requests.post(f"{API_BASE_URL}/chat", json={"query": prompt})
                response.raise_for_status()
                response_data = response.json()
                
                full_response = response_data.get("answer", "Sorry, something went wrong.")
                retrieved_employees = response_data.get("retrieved_employees", [])
                
                st.write_stream(stream_response(full_response))
                
                assistant_message = {"role": "assistant", "content": full_response, "cards": retrieved_employees}
                st.session_state.messages.append(assistant_message)
                
                if retrieved_employees:
                    st.markdown("---")
                    for card in retrieved_employees:
                        display_employee_card(card)

            except requests.exceptions.RequestException:
                error_message = "Could not connect to the backend API. Please make sure it's running."
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message, "cards": []})
            except Exception as e:
                error_message = f"An unexpected error occurred: {e}"
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message, "cards": []})