import os
import time
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("CREWAI_STORAGE_DIR", str(PROJECT_ROOT / ".crewai"))
os.environ.setdefault("CREWAI_TRACING_ENABLED", "false")

from src.refactored_sniffle.main import DEFAULT_MOTION, DebateState, run_debate_session


def add_custom_css():
    """Add custom CSS for enhanced visuals"""
    st.markdown("""
    <style>
        /* Main background */
        .main {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        /* Pro side styling - Green theme */
        .pro-container {
            background: linear-gradient(135deg, rgba(46, 204, 113, 0.1) 0%, rgba(39, 174, 96, 0.1) 100%);
            border-left: 5px solid #2ecc71;
            border-radius: 10px;
            padding: 20px;
        }
        
        /* Con side styling - Red theme */
        .con-container {
            background: linear-gradient(135deg, rgba(231, 76, 60, 0.1) 0%, rgba(192, 57, 43, 0.1) 100%);
            border-left: 5px solid #e74c3c;
            border-radius: 10px;
            padding: 20px;
        }
        
        /* Judge section */
        .judge-container {
            background: linear-gradient(135deg, rgba(241, 196, 15, 0.1) 0%, rgba(230, 126, 34, 0.1) 100%);
            border-top: 3px solid #f39c12;
            border-bottom: 3px solid #f39c12;
            padding: 25px;
        }
        
        /* Winner announcement */
        .winner-banner {
            text-align: center;
            padding: 40px;
            margin: 30px 0;
            border-radius: 15px;
            font-size: 48px;
            font-weight: bold;
            animation: slideDown 0.8s ease-out;
        }
        
        .pro-winner {
            background: linear-gradient(135deg, #2ecc71, #27ae60);
            color: white;
            box-shadow: 0 8px 32px rgba(46, 204, 113, 0.4);
        }
        
        .con-winner {
            background: linear-gradient(135deg, #e74c3c, #c0392b);
            color: white;
            box-shadow: 0 8px 32px rgba(231, 76, 60, 0.4);
        }
        
        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-50px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .thinking {
            animation: pulse 1.5s infinite;
        }
        
        /* Topic styling */
        .topic-container {
            background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(255,255,255,0.85));
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
    </style>
    """, unsafe_allow_html=True)


def render_debate(state: DebateState) -> None:
    """Render the debate with enhanced visuals"""
    
    # Debate topic in a catchy container
    st.markdown("""
    <div class='topic-container'>
        <h2 style='margin: 0; color: #667eea;'>🎯 DEBATE TOPIC</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"<h3 style='text-align: center; color: white; font-size: 28px; margin: 10px 0;'>\"{state.motion}\"</h3>", unsafe_allow_html=True)
    st.markdown("")
    
    # Pro and Con columns
    pro_col, con_col = st.columns(2, gap="large")

    # PRO SIDE - Left
    with pro_col:
        st.markdown("""
        <div style='text-align: center; margin-bottom: 15px;'>
            <span style='font-size: 40px;'>🟢</span>
            <h2 style='margin: 10px 0; color: #2ecc71;'>AFFIRMATIVE</h2>
            <span style='color: #27ae60; font-weight: bold;'>Pro Side</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Pro thinking animation
        with st.spinner("🤔 Affirmative is constructing arguments..."):
            time.sleep(0.3)
        
        # Pro opening statement
        with st.container():
            st.markdown("""
            <div class='pro-container'>
                <h3 style='color: #2ecc71; margin-top: 0;'>📢 OPENING STATEMENT</h3>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(state.pro_opening)
            st.markdown("")
        
        # Pro rebuttal
        with st.container():
            st.markdown("""
            <div class='pro-container'>
                <h3 style='color: #2ecc71; margin-top: 0;'>⚔️ REBUTTAL</h3>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(state.pro_rebuttal)

    # CON SIDE - Right
    with con_col:
        st.markdown("""
        <div style='text-align: center; margin-bottom: 15px;'>
            <span style='font-size: 40px;'>🔴</span>
            <h2 style='margin: 10px 0; color: #e74c3c;'>OPPOSITION</h2>
            <span style='color: #c0392b; font-weight: bold;'>Con Side</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Con thinking animation
        with st.spinner("🤔 Opposition is preparing counterarguments..."):
            time.sleep(0.3)
        
        # Con opening statement
        with st.container():
            st.markdown("""
            <div class='con-container'>
                <h3 style='color: #e74c3c; margin-top: 0;'>📢 OPENING STATEMENT</h3>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(state.con_opening)
            st.markdown("")
        
        # Con rebuttal
        with st.container():
            st.markdown("""
            <div class='con-container'>
                <h3 style='color: #e74c3c; margin-top: 0;'>⚔️ REBUTTAL</h3>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(state.con_rebuttal)

    # Judge verdict section - full width at bottom
    st.markdown("")
    st.markdown("")
    st.markdown("""
    <div style='height: 2px; background: linear-gradient(90deg, #2ecc71, #f39c12, #e74c3c); margin: 30px 0;'></div>
    """, unsafe_allow_html=True)
    
    # Winner announcement with celebration
    winner = state.winner if state.winner in {"Pro", "Con"} else "Pending"
    
    if winner == "Pro":
        st.balloons()
        time.sleep(0.5)
        st.markdown(
            "<div class='winner-banner pro-winner'>🏆 🎊 AFFIRMATIVE WINS! 🎊 🏆</div>",
            unsafe_allow_html=True
        )
    elif winner == "Con":
        st.balloons()
        time.sleep(0.5)
        st.markdown(
            "<div class='winner-banner con-winner'>🏆 🎊 OPPOSITION WINS! 🎊 🏆</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            "<div style='text-align: center; padding: 30px; background: rgba(243, 156, 18, 0.2); border-radius: 15px; margin: 20px 0;'><h2 style='color: #f39c12; margin: 0;'>⚔️ THE DEBATE STANDS UNDECIDED ⚔️</h2></div>",
            unsafe_allow_html=True
        )
    
    st.markdown("")
    
    # Judge section with enhanced styling
    st.markdown("""
    <div class='judge-container'>
        <h2 style='text-align: center; color: #e67e22; margin-top: 0;'>⚖️ JUDGE'S VERDICT ⚖️</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("")
    
    # Judge commentary
    col1, col2, col3 = st.columns([0.5, 3, 0.5])
    with col2:
        with st.container():
            st.markdown("""
            <div style='background: rgba(255, 255, 255, 0.95); border-left: 4px solid #f39c12; padding: 20px; border-radius: 8px;'>
                <h3 style='color: #e67e22; margin-top: 0;'>📝 JUDGE'S COMMENTARY</h3>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(state.judge_description)
    
    st.markdown("")
    
    # Judge scorecard
    col1, col2, col3 = st.columns([0.5, 3, 0.5])
    with col2:
        with st.expander("📊 VIEW DETAILED SCORECARD", expanded=True):
            st.markdown(state.verdict)
    
    st.markdown("")
    st.markdown("")
    
    # Download button
    st.download_button(
        "⬇️ 📥 Download Full Transcript",
        data=state.transcript,
        file_name="debate.md",
        mime="text/markdown",
        use_container_width=True,
    )


def main() -> None:
    st.set_page_config(
        page_title="Debate Arena",
        page_icon=":speech_balloon:",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    
    # Add custom CSS
    add_custom_css()

    # Header with gradient
    st.markdown("""
    <div style='text-align: center; padding: 30px 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 15px; margin-bottom: 30px;'>
        <h1 style='color: white; margin: 0; font-size: 56px;'>🎤 DEBATE ARENA 🎤</h1>
        <p style='color: rgba(255,255,255,0.9); font-size: 18px; margin: 10px 0 0 0;'>⚡ The Ultimate AI Debate Platform</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("Choose your debate topic and watch both sides battle it out with AI-powered arguments!")
    st.markdown("")

    # Styled input form
    with st.form("debate_form"):
        motion = st.text_input(
            "💭 Enter Debate Topic:",
            value=DEFAULT_MOTION,
            placeholder="e.g., AI should replace traditional exams in higher education.",
        )
        col1, col2, col3 = st.columns(3)
        with col2:
            submitted = st.form_submit_button("🚀 START DEBATE", use_container_width=True)

    if submitted:
        cleaned_motion = motion.strip()
        if not cleaned_motion:
            st.error("❌ Please enter a debate topic before starting the debate.")
        else:
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("⏳ Initializing debate engine...")
            progress_bar.progress(10)
            time.sleep(0.5)
            
            status_text.text("🟢 Affirmative is preparing arguments...")
            progress_bar.progress(40)
            time.sleep(0.5)
            
            status_text.text("🔴 Opposition is constructing counterarguments...")
            progress_bar.progress(70)
            time.sleep(0.5)
            
            status_text.text("⚖️ Judge is analyzing both sides...")
            progress_bar.progress(90)
            
            try:
                st.session_state["debate_result"] = run_debate_session(cleaned_motion)
                progress_bar.progress(100)
                status_text.text("✅ Debate complete! Rendering results...")
                time.sleep(0.5)
                progress_bar.empty()
                status_text.empty()
            except Exception as exc:
                st.error(f"❌ Debate failed: {exc}")

    debate_result = st.session_state.get("debate_result")
    if isinstance(debate_result, DebateState):
        render_debate(debate_result)
    else:
        st.markdown("""
        <div style='text-align: center; padding: 60px 20px; background: rgba(102, 126, 234, 0.1); 
                    border-radius: 15px; margin: 40px 0;'>
            <h2 style='color: #667eea; margin-top: 0;'>🎯 READY FOR DEBATE?</h2>
            <p style='font-size: 18px; color: #666;'>Enter a topic above and press START DEBATE to watch AI debaters face off!</p>
            <p style='font-size: 14px; color: #999;'>💡 Example: Should social media be regulated by governments?</p>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
