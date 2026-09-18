import streamlit as st

st.set_page_config(
    page_title="YouTube Script Writing Assistant",
    page_icon="🎬",
    layout="wide"
)

def main():
    st.title("🎬 YouTube Script Writing Assistant")
    st.caption("Powered by LangChain & LLMs")
    
    st.info("Week 1 Project Setup Completed! Detailed requirement analysis, folder architecture, and tech stack are finalized.")
    
    with st.sidebar:
        st.header("⚙️ Preferences")
        topic = st.text_input("Video Topic", placeholder="e.g. How AI is changing Web Development")
        audience = st.selectbox("Target Audience", ["Beginners", "Tech Enthusiasts", "Students", "General Audience"])
        tone = st.selectbox("Tone", ["Informative", "Casual/Friendly", "Humorous", "Professional", "Inspirational"])
        length = st.select_slider("Video Length", options=["Short (< 3 mins)", "Medium (5 - 10 mins)", "Long (10 - 15+ mins)"])
        style = st.selectbox("Content Style", ["Storytelling", "Step-by-Step Tutorial", "Top 5 List", "Deep-dive Analysis"])
        
    st.markdown("### Workflow Status")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Documentation", "Completed ✅")
    col2.metric("Folder Structure", "Initialized ✅")
    col3.metric("Git & Env", "Configured ✅")
    col4.metric("LLM Provider", "Decision Pending ⏳")

if __name__ == "__main__":
    main()
