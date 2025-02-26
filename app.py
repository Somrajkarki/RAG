import streamlit as st
import time
from backend import initialize_chatbot, process_uploaded_files, get_response

st.title("Anomaly, thy name is child")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Initialize chatbot
initialize_chatbot()

# File upload
uploaded_files = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    process_uploaded_files(uploaded_files)
    st.success(f"Uploaded {len(uploaded_files)} files successfully.")

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["message"])

# Function to clean the response
def clean_response(response):
    if isinstance(response, dict) and "result" in response:
        response_text = response["result"]
    else:
        response_text = response
    
    # Remove unwanted elements
    response_text = response_text.replace("\n", " ").replace("[", "").replace("]", "").replace("* ", "")
    
    return response_text.strip()

# User input and chatbot response
if user_input := st.chat_input("You:", key="user_input"):
    user_message = {"role": "user", "message": user_input}
    st.session_state.chat_history.append(user_message)

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Assistant is typing..."):
            raw_response = get_response(user_input)
            response_text = clean_response(raw_response)
            st.markdown(response_text)
            st.markdown("")

            chatbot_message = {"role": "assistant", "message": response_text}
            st.session_state.chat_history.append(chatbot_message)




# import streamlit as st
# import time
# from backend import initialize_chatbot, process_uploaded_files, get_response

# st.title("Anomaly, thy name is child")

# # Initialize session state
# if "chat_history" not in st.session_state:
#     st.session_state.chat_history = []

# initialize_chatbot()

# # File upload
# uploaded_files = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True)

# if uploaded_files:
#     process_uploaded_files(uploaded_files)
#     st.success(f"Uploaded {len(uploaded_files)} files successfully.")

# # Display chat history
# for message in st.session_state.chat_history:
#     with st.chat_message(message["role"]):
#         st.markdown(message["message"])

# # User input and chatbot response
# if user_input := st.chat_input("You:", key="user_input"):
#     user_message = {"role": "user", "message": user_input}
#     st.session_state.chat_history.append(user_message)

#     with st.chat_message("user"):
#         st.markdown(user_input)

#     with st.chat_message("assistant"):
#         with st.spinner("Assistant is typing..."):
#             response_text = get_response(user_input)
#             st.markdown(response_text)

#             chatbot_message = {"role": "assistant", "message": response_text}
#             st.session_state.chat_history.append(chatbot_message)



# import streamlit as st
# import time
# from backend import initialize_chatbot, process_uploaded_files, get_response

# st.title("Anomaly,thy name is child")

# # Initialize chatbot
# initialize_chatbot()

# # Add file upload option
# uploaded_files = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True)

# # Save uploaded files and process them
# if uploaded_files:
#     process_uploaded_files(uploaded_files)
#     st.success(f"Uploaded {len(uploaded_files)} files successfully.")

# # Display chat history
# for message in st.session_state.chat_history:
#     with st.chat_message(message["role"]):
#         st.markdown(message["message"])

# # User input
# if user_input := st.chat_input("You:", key="user_input"):
#     user_message = {"role": "user", "message": user_input}
#     st.session_state.chat_history.append(user_message)

#     with st.chat_message("user"):
#         st.markdown(user_input)

#     with st.chat_message("assistant"):
#         with st.spinner("Assistant is typing..."):
#             response = get_response(user_input)
#     #     message_placeholder = st.empty()
#     #     full_response = ""
#     #     #for chunk in response.split():
#     #         #full_response += chunk + " "
#     #     if response:    
#     #         for chunk in response.splitlines():
#     #             full_response += chunk + "\n"
#     #             time.sleep(0.05)
#     #             message_placeholder.markdown(full_response + "▌")
#     #     else:
#     #         st.error("Received an empty response. Please try again.")
        
#     #     message_placeholder.markdown(full_response, unsafe_allow_html=True)
#     #     #message_placeholder.markdown(full_response)

#     chatbot_message = {"role": "assistant", "message": response}
#     st.session_state.chat_history.append(chatbot_message)
