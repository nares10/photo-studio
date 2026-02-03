import streamlit as st
from services import generate_hd_image, enhance_prompt

def render():
    st.header("Generate Images")
        
    col1, col2 = st.columns([2, 1])
    with col1:
        # Prompt input
        prompt = st.text_area("Enter your prompt", 
                            value="",
                            height=100,
                            key="prompt_input")
        
        # Store original prompt in session state when it changes
        if "original_prompt" not in st.session_state:
            st.session_state.original_prompt = prompt
        elif prompt != st.session_state.original_prompt:
            st.session_state.original_prompt = prompt
            st.session_state.enhanced_prompt = None  # Reset enhanced prompt when original changes
        
        # Enhanced prompt display
        if st.session_state.get('enhanced_prompt'):
            st.markdown("**Enhanced Prompt:**")
            st.markdown(f"*{st.session_state.enhanced_prompt}*")
        
        # Enhance Prompt button
        if st.button("✨ Enhance Prompt", key="enhance_button"):
            if not prompt:
                st.warning("Please enter a prompt to enhance.")
            else:
                with st.spinner("Enhancing prompt..."):
                    try:
                        result = enhance_prompt(st.session_state.api_key, prompt)
                        if result:
                            st.session_state.enhanced_prompt = result
                            st.success("Prompt enhanced!")
                            st.experimental_rerun()  # Rerun to update the display
                    except Exception as e:
                        st.error(f"Error enhancing prompt: {str(e)}")
                        
        # Debug information
        st.write("Debug - Session State:", {
            "original_prompt": st.session_state.get("original_prompt"),
            "enhanced_prompt": st.session_state.get("enhanced_prompt")
        })
    
    with col2:
        num_images = st.slider("Number of images", 1, 4, 1)
        aspect_ratio = st.selectbox("Aspect ratio", ["1:1", "16:9", "9:16", "4:3", "3:4"])
        enhance_img = st.checkbox("Enhance image quality", value=True)
        
        # Style options
        st.subheader("Style Options")
        style = st.selectbox("Image Style", [
            "Realistic", "Artistic", "Cartoon", "Sketch", 
            "Watercolor", "Oil Painting", "Digital Art"
        ])
        
        # Add style to prompt
        if style and style != "Realistic":
            prompt = f"{prompt}, in {style.lower()} style"
    
    # Generate button
    if st.button("🎨 Generate Images", type="primary"):
        if not st.session_state.api_key:
            st.error("Please enter your API key in the sidebar.")
            return
            
        with st.spinner("🎨 Generating your masterpiece..."):
            try:
                # Convert aspect ratio to proper format
                result = generate_hd_image(
                    prompt=st.session_state.enhanced_prompt or prompt,
                    api_key=st.session_state.api_key,
                    num_results=num_images,
                    aspect_ratio=aspect_ratio,  # Already in correct format (e.g. "1:1")
                    sync=True,  # Wait for results
                    enhance_image=enhance_img,
                    medium="art" if style != "Realistic" else "photography",
                    prompt_enhancement=False,  # We're already using our own prompt enhancement
                    content_moderation=True  # Enable content moderation by default
                )
                
                if result:
                    # Debug logging
                    st.write("Debug - Raw API Response:", result)
                    
                    if isinstance(result, dict):
                        if "result_url" in result:
                            st.session_state.edited_image = result["result_url"]
                            st.success("✨ Image generated successfully!")
                        elif "result_urls" in result:
                            st.session_state.edited_image = result["result_urls"][0]
                            st.success("✨ Image generated successfully!")
                        elif "result" in result and isinstance(result["result"], list):
                            for item in result["result"]:
                                if isinstance(item, dict) and "urls" in item:
                                    st.session_state.edited_image = item["urls"][0]
                                    st.success("✨ Image generated successfully!")
                                    break
                                elif isinstance(item, list) and len(item) > 0:
                                    st.session_state.edited_image = item[0]
                                    st.success("✨ Image generated successfully!")
                                    break
                    else:
                        st.error("No valid result format found in the API response.")
                        
            except Exception as e:
                st.error(f"Error generating images: {str(e)}")
                st.write("Full error:", str(e))