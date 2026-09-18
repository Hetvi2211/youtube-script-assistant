import streamlit as st

st.set_page_config(
    page_title="YouTube Script Writing Assistant",
    page_icon="🎬",
    layout="wide"
)


AUDIENCE_OPTIONS = [
    "Beginners",
    "Tech Enthusiasts",
    "Students",
    "General Audience",
]
TONE_OPTIONS = [
    "Informative",
    "Casual/Friendly",
    "Humorous",
    "Professional",
    "Inspirational",
]
VIDEO_LENGTH_OPTIONS = [
    "Short (< 3 mins)",
    "Medium (5 - 10 mins)",
    "Long (10 - 15+ mins)",
]
CONTENT_STYLE_OPTIONS = [
    "Storytelling",
    "Step-by-Step Tutorial",
    "Top 5 List",
    "Deep-dive Analysis",
]
MIN_TOPIC_LENGTH = 10
MAX_TOPIC_LENGTH = 300


def initialize_session_state():
    """Set default values without overwriting values during reruns."""
    defaults = {
        "topic": "",
        "audience": AUDIENCE_OPTIONS[0],
        "tone": TONE_OPTIONS[0],
        "video_length": VIDEO_LENGTH_OPTIONS[1],
        "content_style": CONTENT_STYLE_OPTIONS[0],
        "generated": False,
        "is_processing": False,
        "generation_status": "Ready for input",
        "generated_content": None,
    }

    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def reset_session_state():
    """Clear the form and any previous result."""
    st.session_state.topic = ""
    st.session_state.audience = AUDIENCE_OPTIONS[0]
    st.session_state.tone = TONE_OPTIONS[0]
    st.session_state.video_length = VIDEO_LENGTH_OPTIONS[1]
    st.session_state.content_style = CONTENT_STYLE_OPTIONS[0]
    st.session_state.generated = False
    st.session_state.is_processing = False
    st.session_state.generation_status = "Ready for input"
    st.session_state.generated_content = None


def validate_topic(topic: str):
    """Return a user-facing validation message, or None when the topic is valid."""
    cleaned_topic = topic.strip()

    if not cleaned_topic:
        return "Please enter a video topic."
    if len(cleaned_topic) < MIN_TOPIC_LENGTH:
        return f"The topic is too short. Use at least {MIN_TOPIC_LENGTH} characters."
    if len(cleaned_topic) > MAX_TOPIC_LENGTH:
        return f"The topic is too long. Keep it under {MAX_TOPIC_LENGTH} characters."
    return None


def create_week4_placeholder():
    """Create a clearly marked result until Week 5 connects the LLM."""
    return {
        "title": "AI title generation will be connected in Week 5.",
        "script": "AI script generation will be connected in Week 5.",
        "additional": "Hooks, descriptions, tags, and other content will be added in later weeks.",
    }


def handle_generation():
    """Validate input and prepare the Week 4 placeholder result."""
    validation_error = validate_topic(st.session_state.topic)
    if validation_error:
        st.session_state.generated = False
        st.session_state.generated_content = None
        st.session_state.generation_status = "Input validation failed"
        st.error(validation_error)
        return

    try:
        st.session_state.is_processing = True
        st.session_state.generation_status = "Preparing content"
        with st.spinner("Preparing your content workspace..."):
            st.session_state.generated_content = create_week4_placeholder()
        st.session_state.generated = True
        st.session_state.generation_status = "Placeholder ready"
        st.success("Your inputs were accepted. The Week 4 result area is ready.")
    except Exception as error:
        st.session_state.generated = False
        st.session_state.generated_content = None
        st.session_state.generation_status = "Generation failed"
        st.error(f"Unable to prepare the content area: {error}")
    finally:
        st.session_state.is_processing = False


def render_results():
    """Render result tabs only after valid input has been submitted."""
    if not st.session_state.generated or not st.session_state.generated_content:
        st.info("Complete the form and select Generate Content to see the result area.")
        return

    st.subheader("Content Workspace")
    st.caption("Week 4 placeholder: connect the existing LangChain generators in Week 5.")
    title_tab, script_tab, additional_tab = st.tabs(
        ["Generated Title", "Generated Script", "Additional Content"]
    )

    with title_tab:
        st.info(st.session_state.generated_content["title"])
    with script_tab:
        st.info(st.session_state.generated_content["script"])
    with additional_tab:
        st.info(st.session_state.generated_content["additional"])


def main():
    initialize_session_state()

    st.title("YouTube Script Writing Assistant")
    st.caption("Build a structured starting point for your next YouTube video.")

    with st.sidebar:
        st.header("Video Preferences")
        st.text_area(
            "Video Topic",
            key="topic",
            height=100,
            placeholder="e.g. How AI is changing web development",
            help=f"Enter between {MIN_TOPIC_LENGTH} and {MAX_TOPIC_LENGTH} characters.",
        )
        st.selectbox("Target Audience", AUDIENCE_OPTIONS, key="audience")
        st.selectbox("Tone", TONE_OPTIONS, key="tone")
        st.selectbox("Video Length", VIDEO_LENGTH_OPTIONS, key="video_length")
        st.selectbox("Content Style", CONTENT_STYLE_OPTIONS, key="content_style")

        generate_clicked = st.button("Generate Content", type="primary", use_container_width=True)
        st.button(
            "Clear / Reset",
            on_click=reset_session_state,
            use_container_width=True,
        )

    if generate_clicked:
        handle_generation()

    status_col, input_col = st.columns([1, 2])
    with status_col:
        st.metric("Workflow Status", st.session_state.generation_status)
    with input_col:
        st.caption("Week 4 scope: collect and validate inputs without calling the LLM.")

    st.divider()
    render_results()

if __name__ == "__main__":
    main()
