import streamlit as st
import time
import pathlib
from streamlit_pdf_viewer import pdf_viewer
import os

st.set_page_config(page_title="ChatBot Của Tôi", page_icon="💬")

# Custom CSS for dynamic message styling
st.markdown("""
<style>
.user-message {
    background-color: #f0f2f6;
    border-radius: 10px;
    padding: 10px;
    margin-bottom: 10px;
    display: inline-block;
    max-width: 80%;
    margin-left: auto;
}
.bot-message {
    background-color: #e6f2ff;
    border-radius: 10px;
    padding: 10px;
    margin-bottom: 10px;
    display: inline-block;
    max-width: 80%;
}
</style>
""", unsafe_allow_html=True)

# Khởi tạo trạng thái Session State nếu chưa tồn tại
if "conversations" not in st.session_state:
    st.session_state.conversations = {"Chat 1": []}  # Lưu các hội thoại {id: messages}
if "selected_conversation" not in st.session_state:
    st.session_state.selected_conversation = "Chat 1"
if "menu_states" not in st.session_state:
    st.session_state.menu_states = {}  # Lưu trạng thái của menu tùy chọn

# Hàm hiển thị PDF
def display_pdf(file_path):
    try:
        # Kiểm tra file PDF tồn tại
        if not os.path.exists(file_path):
            st.error(f"Không tìm thấy file PDF tại đường dẫn: {file_path}")
            return
        
        # Đọc toàn bộ PDF
        with open(file_path, "rb") as pdf_file:
            pdf_data = pdf_file.read()

        # Hiển thị toàn bộ PDF (cho phép cuộn)
        pdf_viewer(input=pdf_data, width=800, height=600)
    except Exception as e:
        st.error(f"Có lỗi xảy ra khi hiển thị PDF: {str(e)}")

def create_new_chat():
    new_id = f"Chat {len(st.session_state.conversations) + 1}"
    st.session_state.conversations[new_id] = []
    st.session_state.selected_conversation = new_id
    
def create_chat_button(chat_id):
    col1, col2 = st.columns([6, 1])
    with col1:
        if st.button(chat_id, key=f"chat_select_{chat_id}"):
            st.session_state.selected_conversation = chat_id
            st.session_state.messages = st.session_state.conversations[chat_id]
    with col2:
        if st.button("⋮", key=f"menu_{chat_id}"):
            st.session_state.menu_states[chat_id] = not st.session_state.menu_states.get(chat_id, False)

# Sidebar    
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>Lịch sử trò chuyện</h2>", unsafe_allow_html=True)
    if st.button("➕ New chat"):
        create_new_chat()
    for chat_id in list(st.session_state.conversations.keys()):
        create_chat_button(chat_id)
        if st.session_state.menu_states.get(chat_id, False):
            with st.expander(f"Cài đặt cho '{chat_id}'", expanded=True):
                new_name = st.text_input(f"Đổi tên '{chat_id}' thành:", value="", placeholder=chat_id, key=f"rename_{chat_id}")
                if new_name and new_name != chat_id:
                    if new_name not in st.session_state.conversations:
                        if st.button("Đổi tên", key=f"rename_button_{chat_id}"):
                            st.session_state.conversations[new_name] = st.session_state.conversations.pop(chat_id)
                            if st.session_state.selected_conversation == chat_id:
                                st.session_state.selected_conversation = new_name
                            st.session_state.menu_states[chat_id] = False
                    else:
                        st.warning(f"Tên '{new_name}' đã tồn tại.")
                if st.button("Xóa hội thoại", key=f"delete_button_{chat_id}"):
                    if len(st.session_state.conversations) > 1:
                        st.session_state.conversations.pop(chat_id)
                        chat_ids = list(st.session_state.conversations.keys())
                        if st.session_state.selected_conversation == chat_id:
                            st.session_state.selected_conversation = chat_ids[0] if chat_ids else None
                        st.session_state.menu_states[chat_id] = False
                    else:
                        st.warning("Không thể xóa hội thoại cuối cùng.")

# Lấy hội thoại hiện tại
selected_chat = st.session_state.selected_conversation

if selected_chat:       
    # Main chat area
    st.header("🤖 Guru")
    st.markdown("---")
    
    # Khởi tạo messages cho conversation hiện tại nếu chưa tồn tại
    if "messages" not in st.session_state:
        st.session_state.messages = st.session_state.conversations[selected_chat]

    # Hiển thị các tin nhắn của conversation hiện tại
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-message">{message["content"]}</div>', unsafe_allow_html=True)
            
    def display_typing_message(prompt):
        full_res = ""
        holder = st.empty()
        for word in prompt.split():
            full_res += word + " "
            time.sleep(0.1)
            holder.markdown(f'<div class="bot-message">{full_res}▌</div>', unsafe_allow_html=True)
        
        holder.markdown(f'<div class="bot-message">{full_res}</div>', unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": full_res})
        st.session_state.conversations[selected_chat] = st.session_state.messages

    # Nhập tin nhắn của người dùng
    if prompt := st.chat_input("Nhập tin nhắn của bạn..."):
        st.markdown(f'<div class="user-message">{prompt}</div>', unsafe_allow_html=True)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Bot phản hồi
        if "hiển thị pdf" in prompt.lower():
            pdf_path = "example.pdf"  # Đường dẫn đến PDF
            display_pdf(pdf_path)
        else:
            display_typing_message(prompt)
else:
    st.title("Chưa chọn hội thoại!")
    st.markdown("Hãy chọn hoặc tạo hội thoại mới từ sidebar.")
