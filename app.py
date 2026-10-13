import streamlit as st

from modules.llm import get_llm
from modules.script_generator import generate_script, generate_titles
from modules.conversation import (
    refine_script_with_chat,
    regenerate_script_alternative,
    modify_script_quick,
)
from modules.script_analyzer import (
    DEFAULT_SPEAKING_RATE_WPM,
    ScriptAnalysisError,
    analysis_is_current,
    analyze_script,
    script_fingerprint,
)

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
        # Conversation History & Script Evolution State
        "chat_history": [],
        "script_history": [],
        "active_script_version": 1,
        "analysis_result": None,
        "analysis_script_hash": None,
        "analysis_script_version": None,
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
    st.session_state.chat_history = []
    st.session_state.script_history = []
    st.session_state.active_script_version = 1
    clear_analysis_state()


def clear_analysis_state():
    """Remove analysis tied to an earlier script draft."""
    st.session_state.analysis_result = None
    st.session_state.analysis_script_hash = None
    st.session_state.analysis_script_version = None


def handle_analysis():
    """Analyze the active script only when the user explicitly requests it."""
    generated_content = st.session_state.generated_content
    script = generated_content.get("script", "").strip() if generated_content else ""
    if not script:
        st.warning("Generate or select a script before analyzing it.")
        return

    preferences = {
        "topic": st.session_state.topic,
        "audience": st.session_state.audience,
        "tone": st.session_state.tone,
        "length": st.session_state.video_length,
        "style": st.session_state.content_style,
    }
    try:
        with st.spinner("Analyzing the active script..."):
            result = analyze_script(
                script=script,
                preferences=preferences,
                speaking_rate_wpm=DEFAULT_SPEAKING_RATE_WPM,
                llm=get_llm(temperature=0.2),
            )
        st.session_state.analysis_result = result
        st.session_state.analysis_script_hash = script_fingerprint(script)
        st.session_state.analysis_script_version = st.session_state.active_script_version
        st.success("Script analysis completed.")
    except (ScriptAnalysisError, ValueError) as error:
        clear_analysis_state()
        st.error(f"Script analysis could not be completed: {error}")
    except Exception as error:
        clear_analysis_state()
        st.error(f"Script analysis failed unexpectedly: {error}")


def render_analysis(result):
    """Render the validated analysis payload in a compact, readable layout."""
    st.caption(
        "Scores are AI-assisted estimates, not objective scientific measurements. "
        "Each criterion uses 0-10; the overall score is their average converted to 0-100."
    )
    score_col, word_col, time_col = st.columns(3)
    score_col.metric("Overall Quality", f"{result['overall_score']:.1f}/100")
    word_col.metric("Word Count", f"{result['word_count']}")
    time_col.metric(
        "Estimated Reading Time",
        f"{result['estimated_reading_time_minutes']:.2f} min",
    )

    st.markdown(f"**Overall assessment:** {result['overall_summary']}")
    st.markdown("### Criterion evaluations")
    for criterion in result["criteria"]:
        score = float(criterion["score"])
        with st.expander(
            f"{criterion['criterion']} — {score:.1f}/10 ({criterion['rating']})"
        ):
            st.progress(int(round(score * 10)))
            st.write(criterion["explanation"])
            st.info(f"Suggested action: {criterion['suggestion']}")

    strengths_col, missing_col = st.columns(2)
    with strengths_col:
        st.markdown("### Strengths")
        if result["strengths"]:
            for strength in result["strengths"]:
                st.markdown(f"- {strength}")
        else:
            st.write("No strengths were returned.")
    with missing_col:
        st.markdown("### Missing elements")
        if result["missing_elements"]:
            for element in result["missing_elements"]:
                st.markdown(f"- {element}")
        else:
            st.write("No important missing elements were identified.")

    st.markdown("### Prioritized improvement suggestions")
    if result["improvement_suggestions"]:
        for index, suggestion in enumerate(result["improvement_suggestions"], 1):
            st.markdown(f"{index}. {suggestion}")
    else:
        st.write("No improvement suggestions were returned.")


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


def calculate_script_metrics(script_text: str):
    """Calculates approximate word count and estimated spoken time (at ~140 wpm)."""
    words = len(script_text.split())
    minutes = words / 140.0
    min_part = int(minutes)
    sec_part = int((minutes - min_part) * 60)
    return words, f"{min_part}m {sec_part:02d}s"


def handle_generation():
    """Validate input and generate titles and a script."""
    validation_error = validate_topic(st.session_state.topic)
    if validation_error:
        st.session_state.generated = False
        st.session_state.generated_content = None
        clear_analysis_state()
        st.session_state.generation_status = "Input validation failed"
        st.error(validation_error)
        return

    try:
        st.session_state.is_processing = True
        st.session_state.generation_status = "Generating content"
        preferences = {
            "topic": st.session_state.topic.strip(),
            "audience": st.session_state.audience,
            "tone": st.session_state.tone,
            "length": st.session_state.video_length,
            "style": st.session_state.content_style,
        }

        with st.spinner("Generating titles and script..."):
            llm = get_llm()
            generated_titles = generate_titles(
                topic=preferences["topic"],
                audience=preferences["audience"],
                tone=preferences["tone"],
                style=preferences["style"],
                llm=llm,
            )
            generated_script = generate_script(
                topic=preferences["topic"],
                audience=preferences["audience"],
                tone=preferences["tone"],
                length=preferences["length"],
                style=preferences["style"],
                llm=llm,
            )

        if not isinstance(generated_titles, str) or not generated_titles.strip():
            raise ValueError("The title generator returned an empty or invalid response.")
        if not isinstance(generated_script, str) or not generated_script.strip():
            raise ValueError("The script generator returned an empty or invalid response.")

        clean_script = generated_script.strip()
        st.session_state.generated_content = {
            "titles": generated_titles.strip(),
            "script": clean_script,
            "additional": (
                f"Audience: {preferences['audience']}\n\n"
                f"Tone: {preferences['tone']}\n\n"
                f"Video length: {preferences['length']}\n\n"
                f"Content style: {preferences['style']}"
            ),
        }
        clear_analysis_state()
        st.session_state.generated = True
        st.session_state.generation_status = "Content ready"

        # Initialize Version & Chat History
        st.session_state.active_script_version = 1
        st.session_state.script_history = [
            {
                "version": 1,
                "label": "Initial Script (v1)",
                "script": clean_script,
            }
        ]
        st.session_state.chat_history = [
            {
                "role": "assistant",
                "content": (
                    "✨ **Initial script generated!** You can use the Quick Action buttons above "
                    "or chat below to request revisions (e.g., *'Make the hook more suspenseful'*, "
                    "*'Add a concrete real-world case study'*, or *'Shorten section 2'*)."
                ),
            }
        ]
        st.success("Titles and script generated successfully.")
    except Exception as error:
        st.session_state.generated = False
        st.session_state.generated_content = None
        clear_analysis_state()
        st.session_state.generation_status = "Generation failed"
        st.error(f"Something went wrong: {error}")
    finally:
        st.session_state.is_processing = False


def handle_quick_modification(action_type: str, custom_param: str = None):
    """Executes a quick targeted modification and updates the script version."""
    if not st.session_state.generated_content or not st.session_state.generated_content.get("script"):
        st.warning("No script found to modify. Please generate a script first.")
        return

    current_script = st.session_state.generated_content["script"]
    labels = {
        "shorten": "Shorten Script (Condense Word Count)",
        "expand": "Expand Script (Deeper Details & Visual Cues)",
        "change_tone": f"Change Tone to {custom_param}",
        "improve_intro": "Improve Hook & Introduction (High Retention)",
        "add_examples": "Add Real-World Examples & Case Studies",
    }
    action_label = labels.get(action_type, action_type.replace("_", " ").title())

    try:
        with st.spinner(f"Applying: {action_label}..."):
            llm = get_llm()
            revised_script = modify_script_quick(
                current_script=current_script,
                action=action_type,
                custom_param=custom_param,
                llm=llm,
            )

        if not revised_script or not revised_script.strip():
            raise ValueError("The modification returned an empty response.")

        clean_revised = revised_script.strip()
        new_version = st.session_state.active_script_version + 1
        st.session_state.active_script_version = new_version
        st.session_state.generated_content["script"] = clean_revised
        clear_analysis_state()

        st.session_state.script_history.append({
            "version": new_version,
            "label": f"v{new_version}: {action_label}",
            "script": clean_revised,
        })

        st.session_state.chat_history.append({
            "role": "user",
            "content": f"Action Requested: **{action_label}**",
        })
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": f"✅ Applied **{action_label}**. Script updated to **Version {new_version}**! View the updated text in the *Generated Script* tab.",
        })
        st.success(f"Script updated: {action_label} (Version {new_version})")
        st.rerun()

    except Exception as error:
        st.error(f"Modification failed: {error}")


def handle_regenerate_full_script():
    """Generates an alternative script draft from scratch with fresh creative angles."""
    if not st.session_state.generated_content:
        st.warning("Please generate a script first.")
        return

    try:
        with st.spinner("Regenerating fresh script draft..."):
            llm = get_llm()
            new_script = regenerate_script_alternative(
                topic=st.session_state.topic.strip(),
                audience=st.session_state.audience,
                tone=st.session_state.tone,
                length=st.session_state.video_length,
                style=st.session_state.content_style,
                llm=llm,
            )

        if not new_script or not new_script.strip():
            raise ValueError("Regeneration returned an empty response.")

        clean_new = new_script.strip()
        new_version = st.session_state.active_script_version + 1
        st.session_state.active_script_version = new_version
        st.session_state.generated_content["script"] = clean_new
        clear_analysis_state()

        st.session_state.script_history.append({
            "version": new_version,
            "label": f"v{new_version}: Fresh Creative Draft",
            "script": clean_new,
        })

        st.session_state.chat_history.append({
            "role": "user",
            "content": "Requested: **Regenerate Full Script** with alternative creative angle.",
        })
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": f"🔄 Fresh script draft generated (Version {new_version})! Review it in the *Generated Script* tab.",
        })
        st.success(f"Fresh script draft created (Version {new_version})")
        st.rerun()

    except Exception as error:
        st.error(f"Regeneration failed: {error}")


def handle_chat_user_prompt(user_text: str):
    """Processes conversational modification prompts in context."""
    if not user_text or not user_text.strip():
        return

    current_script = st.session_state.generated_content.get("script", "")
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_text.strip(),
    })

    preferences = {
        "topic": st.session_state.topic,
        "audience": st.session_state.audience,
        "tone": st.session_state.tone,
    }

    try:
        with st.spinner("Processing refinement request..."):
            llm = get_llm()
            assistant_reply = refine_script_with_chat(
                current_script=current_script,
                user_instruction=user_text.strip(),
                chat_history=st.session_state.chat_history,
                preferences=preferences,
                llm=llm,
            )

        clean_reply = assistant_reply.strip()
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": clean_reply,
        })

        # If the reply contains a full revised script (e.g. headers or substantial text), offer or apply update
        if len(clean_reply.split()) > 150 and any(h in clean_reply for h in ["[HOOK]", "[INTRODUCTION]", "[MAIN CONTENT]", "Hook:"]):
            new_version = st.session_state.active_script_version + 1
            st.session_state.active_script_version = new_version
            st.session_state.generated_content["script"] = clean_reply
            clear_analysis_state()
            st.session_state.script_history.append({
                "version": new_version,
                "label": f"v{new_version}: Chat Refinement ('{user_text[:30]}...')",
                "script": clean_reply,
            })
            st.toast(f"Active script updated to Version {new_version}!")

        st.rerun()

    except Exception as error:
        st.error(f"Chat refinement failed: {error}")


def restore_version(version_entry):
    """Restores an earlier script draft from version history."""
    st.session_state.generated_content["script"] = version_entry["script"]
    st.session_state.active_script_version = version_entry["version"]
    clear_analysis_state()
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": f"⏪ Restored script to **Version {version_entry['version']}** ({version_entry['label']}).",
    })
    st.success(f"Restored to Version {version_entry['version']}")
    st.rerun()


def render_results():
    """Render result tabs only after valid input has been submitted."""
    if not st.session_state.generated or not st.session_state.generated_content:
        st.info("Complete the preferences form on the left and select **Generate Content** to start.")
        return

    st.subheader("Content Workspace")
    current_script = st.session_state.generated_content["script"]
    word_count, est_time = calculate_script_metrics(current_script)

    metric_c1, metric_c2, metric_c3, metric_c4 = st.columns(4)
    metric_c1.metric("Current Version", f"v{st.session_state.active_script_version}")
    metric_c2.metric("Word Count", f"{word_count} words")
    metric_c3.metric("Est. Speaking Time", est_time)
    metric_c4.metric("Saved Drafts", f"{len(st.session_state.script_history)}")

    st.divider()

    title_tab, script_tab, analyzer_tab, refine_tab, history_tab, info_tab = st.tabs(
        [
            "💡 Generated Titles",
            f"📜 Active Script (v{st.session_state.active_script_version})",
            "🔍 AI Script Analyzer",
            "💬 Interactive Refinement & Chat",
            "🕰️ Version History",
            "ℹ️ Parameters & Metadata",
        ]
    )

    with title_tab:
        st.markdown(st.session_state.generated_content["titles"])

    with script_tab:
        st.caption(f"Showing Active Version **{st.session_state.active_script_version}** • {word_count} words • Approx. {est_time} spoken time")
        st.markdown(current_script)
        st.download_button(
            label="📥 Download Script as TXT",
            data=current_script,
            file_name=f"youtube_script_v{st.session_state.active_script_version}.txt",
            mime="text/plain",
            use_container_width=False,
        )

    with analyzer_tab:
        st.markdown("### 🔍 AI Script Analyzer")
        st.caption(
            "Analyze the active script against your selected audience, tone, length, and style. "
            "Analysis runs only when you click the button."
        )
        if st.button("Analyze Script", type="primary", use_container_width=True):
            handle_analysis()

        analysis_result = st.session_state.analysis_result
        if analysis_result and analysis_is_current(
            analysis_result,
            st.session_state.analysis_script_hash,
            st.session_state.analysis_script_version,
            current_script,
            st.session_state.active_script_version,
        ):
            render_analysis(analysis_result)
        elif analysis_result:
            st.warning(
                "This analysis belongs to an older script version. "
                "Click **Analyze Script** to analyze the active draft."
            )
        else:
            st.info("Click **Analyze Script** to evaluate the active draft.")

    with refine_tab:
        st.markdown("### ⚡ Quick Script Modifications")
        st.caption("One-click targeted refinements to quickly alter pacing, structure, or tone:")

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            if st.button("🔄 Regenerate Draft", help="Generate an alternative creative draft from scratch", use_container_width=True):
                handle_regenerate_full_script()
        with col2:
            if st.button("✂️ Shorten Script", help="Trim word count by ~30%, removing fluff", use_container_width=True):
                handle_quick_modification("shorten")
        with col3:
            if st.button("📈 Expand Script", help="Enrich with deeper explanations & visual cues", use_container_width=True):
                handle_quick_modification("expand")
        with col4:
            if st.button("🚀 Improve Hook/Intro", help="Supercharge first 30 seconds for higher viewer retention", use_container_width=True):
                handle_quick_modification("improve_intro")
        with col5:
            if st.button("💡 Add Examples", help="Inject practical real-world case studies and examples", use_container_width=True):
                handle_quick_modification("add_examples")

        # Tone Modifier
        with st.expander("🎭 Change Script Tone", expanded=False):
            tone_col1, tone_col2 = st.columns([3, 1])
            with tone_col1:
                target_tone = st.selectbox(
                    "Select Target Tone",
                    ["Casual/Friendly", "Humorous", "Inspirational", "Professional", "Dramatic / Storytelling", "High Energy / Hype"],
                    key="quick_target_tone",
                )
            with tone_col2:
                st.write("")
                st.write("")
                if st.button("Apply New Tone", use_container_width=True):
                    handle_quick_modification("change_tone", custom_param=target_tone)

        st.divider()
        st.markdown("### 💬 Conversational Refinement")
        st.caption("Ask the AI assistant for any custom changes, adjustments, or additions in natural language:")

        # Render Chat History
        for msg in st.session_state.chat_history:
            role = msg.get("role", "assistant")
            with st.chat_message(role):
                st.markdown(msg.get("content", ""))

        # Chat Input
        user_input = st.chat_input("E.g., 'Make the hook more suspenseful', 'Add a funny joke in section 2', 'Explain point 3 simpler'...")
        if user_input:
            handle_chat_user_prompt(user_input)

    with history_tab:
        st.markdown("### 🕰️ Script Version History")
        st.caption("All drafts generated in this session. You can restore any earlier draft at any time:")

        if not st.session_state.script_history:
            st.info("No previous drafts recorded yet.")
        else:
            for item in reversed(st.session_state.script_history):
                v_num = item["version"]
                is_active = (v_num == st.session_state.active_script_version)
                badge = "*(ACTIVE)*" if is_active else ""

                with st.expander(f"Version {v_num}: {item['label']} {badge}", expanded=is_active):
                    st.text(item["script"][:400] + ("..." if len(item["script"]) > 400 else ""))
                    if not is_active:
                        if st.button(f"⏪ Restore Version {v_num}", key=f"restore_btn_{v_num}"):
                            restore_version(item)

    with info_tab:
        st.text(st.session_state.generated_content["additional"])


def main():
    initialize_session_state()

    st.title("🎬 YouTube Script Writing Assistant")
    st.caption("AI-powered content planner, scriptwriter, and interactive conversational refiner.")

    with st.sidebar:
        st.header("Video Preferences")
        st.text_area(
            "Video Topic",
            key="topic",
            height=100,
            placeholder="e.g. How small habits can improve your mornings",
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
        st.caption("Build title ideas, structured scripts, and interactively polish them with AI.")

    st.divider()
    render_results()


if __name__ == "__main__":
    main()
