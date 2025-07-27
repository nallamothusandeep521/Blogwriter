import streamlit as st
import os
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage
import time
import re

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="🤖 Blog Writer",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling and alignment
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 2.5rem;
        margin-bottom: 1rem;
        padding: 1rem 0;
    }
    
    .subtitle {
        text-align: center;
        color: #666;
        font-style: italic;
        margin-bottom: 2rem;
    }
    
    .thinking-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
        text-align: center;
    }
    
    .blog-output {
        background: #ffffff;
        padding: 2.5rem;
        border-radius: 15px;
        border: 1px solid #e1e8ed;
        margin: 1.5rem 0;
        font-family: 'Georgia', serif;
        line-height: 1.8;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    .blog-output h1 {
        color: #1a202c;
        font-size: 2.4rem;
        margin-bottom: 1.5rem;
        text-align: center;
        border-bottom: 3px solid #3182ce;
        padding-bottom: 1rem;
        font-weight: 700;
    }
    
    .blog-output h2 {
        color: #2d3748;
        font-size: 1.6rem;
        margin-top: 2.5rem;
        margin-bottom: 1.2rem;
        border-left: 5px solid #3182ce;
        padding-left: 1.5rem;
        font-weight: 600;
    }
    
    .blog-output h3 {
        color: #4a5568;
        font-size: 1.3rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    .blog-output p {
        margin-bottom: 1.5rem;
        text-align: justify;
        color: #2d3748;
        font-size: 1.1rem;
    }
    
    .enhancement-card {
        background: #f7fafc;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .enhancement-card pre {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        font-family: 'Arial', sans-serif;
        color: #2d3748;
        line-height: 1.6;
        margin: 0;
    }
    
    .stats-box {
        background: linear-gradient(135deg, #e6f3ff 0%, #cce7ff 100%);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin: 1.5rem 0;
        border: 1px solid #bee3f8;
    }
    
    .stats-box h4 {
        margin-bottom: 1rem;
        color: #2b6cb0;
    }
    
    .input-section {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin: 1rem 0;
    }
    
    .tools-section {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .section-header {
        color: #2d3748;
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e2e8f0;
    }
    
    .copy-button-container {
        position: relative;
        margin-top: 1rem;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .blog-output {
            padding: 1.5rem;
        }
        
        .blog-output h1 {
            font-size: 2rem;
        }
        
        .blog-output h2 {
            font-size: 1.4rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize LLM
@st.cache_resource
def initialize_llm():
    """Initialize the ChatGroq LLM with API key"""
    api_key = "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"
    if not api_key:
        st.error("⚠️ Please set your GROQ_API_KEY in the environment variables or .env file")
        st.stop()
    
    return ChatGroq(
        model="deepseek-r1-distill-llama-70b",
        api_key=api_key,
        temperature=0.7
    )

# Utility Functions
def count_words(text):
    """Count words in text"""
    return len(text.split())

def format_blog_content(content):
    """Format blog content with proper HTML structure"""
    if not content:
        return ""
    
    # Clean up the content first - remove ** formatting
    content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)
    
    # Split content into lines
    lines = content.split('\n')
    formatted_lines = []
    title_found = False
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if it's a title (first substantial line or ends with specific patterns)
        if not title_found and (len(line) > 10 and not line.lower().startswith(('introduction', 'conclusion', 'the ', 'in ', 'on ', 'at '))):
            title = line.replace('#', '').strip()
            formatted_lines.append(f"<h1>{title}</h1>")
            title_found = True
        # Check if it's a main heading (contains keywords or specific patterns)
        elif (line.lower().startswith(('introduction', 'conclusion', 'benefits', 'overview', 'summary')) or 
              any(keyword in line.lower() for keyword in [': ', 'chapter', 'part ', 'section']) or
              line.startswith('#')):
            heading = line.replace('#', '').replace(':', '').strip()
            formatted_lines.append(f"<h2>{heading}</h2>")
        # Check for subheadings (ends with colon or starts with ###)
        elif line.endswith(':') or line.startswith('###'):
            subheading = line.replace('#', '').replace(':', '').strip()
            formatted_lines.append(f"<h3>{subheading}</h3>")
        # Regular paragraph
        else:
            formatted_lines.append(f"<p>{line}</p>")
    
    return '\n'.join(formatted_lines)

# Prompt Templates
def get_blog_generation_prompt(topic, niche, tone, style, word_count):
    return f"""<think>
I need to write a blog post about "{topic}" in the {niche} niche with a {tone} tone and {style} style, targeting around {word_count} words.

Let me structure this properly:
1. Create an engaging title
2. Write a compelling introduction
3. Develop the main content with clear sections
4. Add a strong conclusion
5. Make sure the tone is {tone} and style is {style}
6. Use proper heading format without ** symbols
</think>

You are a skilled blog writer. Write a comprehensive blog post with the following specifications:

Topic: "{topic}"
Niche: {niche}
Tone: {tone}
Style: {style}
Target Word Count: Around {word_count} words

IMPORTANT FORMATTING RULES:
- Use clean headings WITHOUT ** symbols or markdown formatting
- Structure headings as: "Introduction", "Main Topic: Subtitle", "Conclusion"
- Write in clean, readable format
- Do not use ** or any markdown symbols in the output

Structure your blog post with:
- An engaging title (no formatting symbols)
- Introduction section
- Main body with clear section headings
- co with a call-to-action

Style Guidelines:
- If style is "Conversational": Use "you" and speak directly to the reader
- If style is "Conversational (American)": Use American slang and casual phrases
- If style is "Normal": Use professional but accessible language

Tone Guidelines:
- Friendly: Warm, approachable, helpful
- Witty: Include light humor and clever wordplay
- Professional: Authoritative, informative, formal
- Empathetic: Understanding, supportive, caring
- Bold: Confident, assertive, compelling

Make the content engaging, informative, and well-structured with clean headings."""

def get_text_enhancement_prompt(text, enhancement_type, tone=None, style=None, word_count=None):
    base_prompt = f"<think>\nI need to enhance this text by {enhancement_type}. Let me analyze what needs to be improved and apply the appropriate changes.\n</think>\n\n"
    
    if enhancement_type == "humanize":
        return base_prompt + f"""Make this text sound more natural, warm, and human-written. Remove any robotic or AI-like language while maintaining the core message and structure:

Text to humanize:
{text}"""
    
    elif enhancement_type == "grammar":
        return base_prompt + f"""Improve the grammar, clarity, and readability of this text. Fix any errors and enhance flow while keeping the original meaning and tone:

Text to improve:
{text}"""
    
    elif enhancement_type == "tone_change":
        return base_prompt + f"""Rewrite this text to match the {tone} tone while keeping the same information and structure:

Original text:
{text}"""
    
    elif enhancement_type == "style_change":
        return base_prompt + f"""Rewrite this text in {style} style while maintaining the same content and message:

Original text:
{text}"""
    
    elif enhancement_type == "word_count":
        return base_prompt + f"""Adjust this text to approximately {word_count} words while maintaining quality and completeness. If expanding, add relevant details. If shortening, keep the most important points:

Original text:
{text}"""

def get_title_generator_prompt(topic, tone, niche):
    return f"""Generate exactly 5 blog titles for the topic "{topic}" with a {tone} tone in the {niche} niche.

Provide ONLY the titles in this exact format:
1. [Title]
2. [Title]
3. [Title] 
4. [Title]
5. [Title]

No thinking process, no explanations, no additional text - just the 5 titles."""

# LLM Function with thinking display
def call_llm(llm, prompt, show_thinking=True):
    """Call the LLM with thinking display and error handling"""
    try:
        thinking_placeholder = st.empty()
        
        if show_thinking:
            with thinking_placeholder:
                st.markdown("""
                <div class="thinking-box">
                    <h4>🤔 AI is thinking...</h4>
                    <p>Processing your request and generating content...</p>
                </div>
                """, unsafe_allow_html=True)
        
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content
        
        # Extract and display thinking if present
        if show_thinking and "<think>" in content:
            thinking_match = re.search(r"<think>(.*?)</think>", content, re.DOTALL)
            if thinking_match:
                thinking_content = thinking_match.group(1).strip()
                with thinking_placeholder:
                    st.markdown(f"""
                    <div class="thinking-box">
                        <h4>🤔 AI Thoughts:</h4>
                        <p>{thinking_content}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Remove thinking tags from final content
                content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
        else:
            thinking_placeholder.empty()
        
        return content
    except Exception as e:
        st.error(f"Error calling LLM: {str(e)}")
        return None

# Main App
def main():
    # Header Section
    st.markdown('<h1 class="main-header">🤖 Blog Writer</h1>', unsafe_allow_html=True)
    
    
    # Initialize LLM
    llm = initialize_llm()
    
    # Initialize session state
    if 'blog_content' not in st.session_state:
        st.session_state.blog_content = ""
    if 'user_text' not in st.session_state:
        st.session_state.user_text = ""
    
    # Main Layout
    col_sidebar, col_main = st.columns([1, 3])
    
    # Sidebar - Configuration Panel
    with col_sidebar:
        with st.sidebar:
            st.header("📝 Blog Configuration")
            
            # Blog Topic Input
            topic = st.text_input(
                "🎯 Blog Topic",
                placeholder="Enter your blog topic here...",
                help="What would you like to write about?"
            )
            
            # Word Count Selector
            word_count_options = {
                "300 words (Short)": 300,
                "600 words (Medium)": 600,
                "900-1000 words (Long)": 950
            }
            word_count_selection = st.selectbox(
                "📏 Word Count",
                options=list(word_count_options.keys())
            )
            word_count = word_count_options[word_count_selection]
            
            # Blog Style Selector
            style = st.radio(
                "🎨 Blog Style",
                options=["Normal", "Conversational", "Conversational (American)"]
            )
            
            # Tone/Emotion Selector
            tone = st.selectbox(
                "🎭 Tone",
                options=["Friendly", "Witty", "Professional", "Empathetic", "Bold"]
            )
            
            # Blog Niche Selector
            niche = st.selectbox(
                "🏷️ Blog Niche",
                options=["Technology", "Health", "Lifestyle", "Finance", "Travel", "Education", "Other"]
            )
            
            st.divider()
            
            # Main Action Button
            generate_blog = st.button(
                "✅ Generate Blog", 
                type="primary", 
                use_container_width=True,
                help="Generate a new blog post with your specifications"
            )
            
            st.divider()
            
            # Additional Tools
            st.subheader("🔧 Quick Tools")
            col1, col2 = st.columns(2)
            with col2:
                generate_titles = st.button("📝 Title Ideas", use_container_width=True)
    
    # Main Content Area
    with col_main:
        # User Text Input Section
        # st.markdown('<div class="input-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">✍️ Your Text Input</div>', unsafe_allow_html=True)
        st.markdown("*Paste your own text here to enhance it, or generate a new blog using the sidebar*")
        
        user_text = st.text_area(
            "Enter your text here:",
            value=st.session_state.user_text,
            height=150,
            placeholder="Paste your existing text here to enhance it with AI tools...",
            key="user_input_area"
        )
        st.session_state.user_text = user_text
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Enhancement Tools Section
        st.markdown('<div class="tools-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">🛠️ Enhancement Tools</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            humanize_text = st.button("✨ Humanize", use_container_width=True, help="Make text more natural")
        with col2:
            improve_grammar = st.button("🧠 Grammar Fix", use_container_width=True, help="Improve grammar and clarity")
        with col3:
            change_tone = st.button("🎭 Change Tone", use_container_width=True, help="Apply selected tone")
        with col4:
            change_style = st.button("🎨 Change Style", use_container_width=True, help="Apply selected style")
        with col5:
            adjust_length = st.button("📏 Adjust Length", use_container_width=True, help="Adjust to target word count")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Determine which text to work with
        working_text = st.session_state.user_text if st.session_state.user_text.strip() else st.session_state.blog_content
        
        # Process Actions
        if generate_blog:
            if topic:
                prompt = get_blog_generation_prompt(topic, niche, tone, style, word_count)
                result = call_llm(llm, prompt)
                if result:
                    st.session_state.blog_content = result
                    st.session_state.user_text = result
                    st.success("✅ Blog generated successfully!")
                    st.rerun()
            else:
                st.warning("⚠️ Please enter a blog topic first!")
        
        # Enhancement Actions
        if humanize_text and working_text:
            prompt = get_text_enhancement_prompt(working_text, "humanize")
            result = call_llm(llm, prompt)
            if result:
                st.session_state.user_text = result
                st.session_state.blog_content = result
                st.success("✨ Text humanized!")
                st.rerun()
        
        if improve_grammar and working_text:
            prompt = get_text_enhancement_prompt(working_text, "grammar")
            result = call_llm(llm, prompt)
            if result:
                st.session_state.user_text = result
                st.session_state.blog_content = result
                st.success("🧠 Grammar improved!")
                st.rerun()
        
        if change_tone and working_text:
            prompt = get_text_enhancement_prompt(working_text, "tone_change", tone=tone)
            result = call_llm(llm, prompt)
            if result:
                st.session_state.user_text = result
                st.session_state.blog_content = result
                st.success(f"🎭 Tone changed to {tone}!")
                st.rerun()
        
        if change_style and working_text:
            prompt = get_text_enhancement_prompt(working_text, "style_change", style=style)
            result = call_llm(llm, prompt)
            if result:
                st.session_state.user_text = result
                st.session_state.blog_content = result
                st.success(f"🎨 Style changed to {style}!")
                st.rerun()
        
        if adjust_length and working_text:
            prompt = get_text_enhancement_prompt(working_text, "word_count", word_count=word_count)
            result = call_llm(llm, prompt)
            if result:
                st.session_state.user_text = result
                st.session_state.blog_content = result
                st.success(f"📏 Length adjusted to ~{word_count} words!")
                st.rerun()
        
        # Display Results Section
        if working_text:
            # Statistics
            word_count_actual = count_words(working_text)
            reading_time = max(1, word_count_actual // 200)
            
            st.markdown(f"""
            <div class="stats-box">
                <h4>📊 Content Statistics</h4>
                <div style="display: flex; justify-content: space-around; flex-wrap: wrap;">
                    <div><strong>Words:</strong> {word_count_actual}</div>
                    <div><strong>Characters:</strong> {len(working_text):,}</div>
                    <div><strong>Reading Time:</strong> {reading_time} min</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Formatted Output with Copy Button
            st.markdown('<div class="section-header">📄 Formatted Blog Post</div>', unsafe_allow_html=True)
            
            col_content, col_copy = st.columns([10, 1])
            
            with col_content:
                formatted_content = format_blog_content(working_text)
                st.markdown(f'<div class="blog-output">{formatted_content}</div>', unsafe_allow_html=True)
            
            with col_copy:
                st.markdown('<div class="copy-button-container">', unsafe_allow_html=True)
                if st.button("📋", help="Copy content", key="copy_main"):
                    st.success("Ready to copy!")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Download Options
            st.markdown('<div class="section-header">📥 Download Options</div>', unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.download_button(
                    label="📄 Download as TXT",
                    data=working_text,
                    file_name=f"blog_{topic.replace(' ', '_') if topic else 'enhanced'}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with col2:
                st.download_button(
                    label="🌐 Download as HTML",
                    data=f"<!DOCTYPE html><html><head><meta charset='UTF-8'><title>Blog Post</title></head><body style='font-family: Georgia, serif; max-width: 800px; margin: 0 auto; padding: 2rem; line-height: 1.8;'>{formatted_content}</body></html>",
                    file_name=f"blog_{topic.replace(' ', '_') if topic else 'enhanced'}.html",
                    mime="text/html",
                    use_container_width=True
                )
            
            with col3:
                # Create markdown version
                markdown_content = working_text.replace('**', '')
                st.download_button(
                    label="📝 Download as MD",
                    data=markdown_content,
                    file_name=f"blog_{topic.replace(' ', '_') if topic else 'enhanced'}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
        
        else:
            st.info("👆 Configure your blog settings in the sidebar and click 'Generate Blog', or paste your own text in the input area above to get started!")
        
        # Additional Tools Results
        # Change this to only handle title suggestions:
        if generate_titles:
            st.markdown('<div class="section-header">🔧 Tool Results</div>', unsafe_allow_html=True)
            st.subheader("📝 Title Suggestions")
            if topic:
                prompt = get_title_generator_prompt(topic, tone, niche)
                result = call_llm(llm, prompt, show_thinking=False)
                if result:
                    # Extract only lines that start with 1., 2., 3., 4., or 5.
                    title_lines = [line.strip() for line in result.strip().splitlines() if re.match(r"^\d\.", line.strip())]
                    if title_lines:
                        html_titles = """
                        <div class="enhancement-card" style="background:#f0f8ff; padding:1.5rem; border-radius:12px; margin-bottom:1rem;">
                            <h4 style="margin-top:0; color:#2b6cb0;">Your 5 Blog Title Ideas</h4>
                            <ol style='padding-left:1.5em; font-size:1.1rem; color:#2d3748;'>
                        """
                        for line in title_lines:
                            title_text = re.sub(r"^\d\.\s*", "", line)
                            html_titles += f"<li style='margin-bottom:0.5em;'>{title_text}</li>"
                        html_titles += "</ol></div>"
                        st.markdown(html_titles, unsafe_allow_html=True)
                    else:
                        st.info("No titles found. Please try again.")
                    # Place the copy button below the titles for better UX
                    if st.button("📋 Copy All Titles", key="copy_titles", use_container_width=True):
                        st.success("Titles ready to copy!")
            else:
                st.warning("⚠️ Please enter a blog topic first!")
    
    

if __name__ == "__main__":
    main()
