import streamlit as st
from PIL import Image
import numpy as np
import io
from streamlit_drawable_canvas import st_canvas

from utils.polling import check_generated_images, auto_check_images
from utils.download_image import download_image
from services.generative_fill import generative_fill as fill
def render():
    st.header("🎨 Generative Fill")
    st.markdown("Draw a mask on the image and describe what you want to generate in that area.")
    
    uploaded_file = st.file_uploader("Upload Product Image", type=["png", "jpg", "jpeg"], key="fill_upload")
    if uploaded_file:
        col1, col2 = st.columns(2)
        import io

        with col1:
            st.image(uploaded_file, caption="Original Image", use_column_width=True)
            
            # Product editing options
            edit_option = st.selectbox("Select Edit Option", [
                "Create Packshot",
                "Add Shadow",
                "Lifestyle Shot"
            ])
            
            if edit_option == "Create Packshot":
                col_a, col_b = st.columns(2)
                with col_a:
                    bg_color = st.color_picker("Background Color", "#FFFFFF")
                    sku = st.text_input("SKU (optional)", "")
                with col_b:
                    force_rmbg = st.checkbox("Force Background Removal", False)
            img = Image.open(uploaded_file)
            img_width, img_height = img.size
            
            # Calculate aspect ratio and set canvas height
            aspect_ratio = img_height / img_width
            canvas_width = min(img_width, 800)  # Max width of 800px
            canvas_height = int(canvas_width * aspect_ratio)
            
            # Resize image to match canvas dimensions
            img = img.resize((canvas_width, canvas_height))
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Convert to numpy array with proper shape and type
            img_array = np.array(img).astype(np.uint8)
            
            # Add drawing canvas using Streamlit's drawing canvas component
            stroke_width = st.slider("Brush width", 1, 50, 20)
            stroke_color = st.color_picker("Brush color", "#fff")
            drawing_mode = "freedraw"
            
            # Create canvas with background image
            canvas_result = st_canvas(
                fill_color="rgba(255, 255, 255, 0.0)",  # Transparent fill
                stroke_width=stroke_width,
                stroke_color=stroke_color,
                drawing_mode=drawing_mode,
                background_color="",  # Transparent background
                background_image=img if img_array.shape[-1] == 3 else None,  # Only pass RGB images
                height=canvas_height,
                width=canvas_width,
                key="canvas",
            )
            
            # Options for generation
            st.subheader("Generation Options")
            prompt = st.text_area("Describe what to generate in the masked area")
            negative_prompt = st.text_area("Describe what to avoid (optional)")
            
            col_a, col_b = st.columns(2)
            with col_a:
                num_results = st.slider("Number of variations", 1, 4, 1)
                sync_mode = st.checkbox("Synchronous Mode", False,
                    help="Wait for results instead of getting URLs immediately",
                    key="gen_fill_sync_mode")
            
            with col_b:
                seed = st.number_input("Seed (optional)", min_value=0, value=0,
                    help="Use same seed to reproduce results")
                content_moderation = st.checkbox("Enable Content Moderation", False,
                    key="gen_fill_content_mod")
            
            if st.button("🎨 Generate", type="primary"):
                if not prompt:
                    st.error("Please enter a prompt describing what to generate.")
                    return
                
                if canvas_result.image_data is None:
                    st.error("Please draw a mask on the image first.")
                    return
                
                # Convert canvas result to mask
                mask_img = Image.fromarray(canvas_result.image_data.astype('uint8'), mode='RGBA')
                mask_img = mask_img.convert('L')
                
                # Convert mask to bytes
                mask_bytes = io.BytesIO()
                mask_img.save(mask_bytes, format='PNG')
                mask_bytes = mask_bytes.getvalue()
                
                # Convert uploaded image to bytes
                image_bytes = uploaded_file.getvalue()
                
                with st.spinner("🎨 Generating..."):
                    try:
                        result = fill(
                            st.session_state.api_key,
                            image_bytes,
                            mask_bytes,
                            prompt,
                            negative_prompt=negative_prompt if negative_prompt else None,
                            num_results=num_results,
                            sync=sync_mode,
                            seed=seed if seed != 0 else None,
                            content_moderation=content_moderation
                        )
                        
                        if result:
                            st.write("Debug - API Response:", result)
                            
                            if sync_mode:
                                if "urls" in result and result["urls"]:
                                    st.session_state.edited_image = result["urls"][0]
                                    if len(result["urls"]) > 1:
                                        st.session_state.generated_images = result["urls"]
                                    st.success("✨ Generation complete!")
                                elif "result_url" in result:
                                    st.session_state.edited_image = result["result_url"]
                                    st.success("✨ Generation complete!")
                            else:
                                if "urls" in result:
                                    st.session_state.pending_urls = result["urls"][:num_results]
                                    
                                    # Create containers for status
                                    status_container = st.empty()
                                    refresh_container = st.empty()
                                    
                                    # Show initial status
                                    status_container.info(f"🎨 Generation started! Waiting for {len(st.session_state.pending_urls)} image{'s' if len(st.session_state.pending_urls) > 1 else ''}...")
                                    
                                    # Try automatic checking
                                    if auto_check_images(status_container):
                                        st.rerun()
                                    
                                    # Add refresh button
                                    if refresh_container.button("🔄 Check for Generated Images"):
                                        if check_generated_images():
                                            status_container.success("✨ Images ready!")
                                            st.rerun()
                                        else:
                                            status_container.warning("⏳ Still generating... Please check again in a moment.")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        st.write("Full error details:", str(e))
        
        with col2:
            if st.session_state.edited_image:
                st.image(st.session_state.edited_image, caption="Generated Result", use_column_width=True)
                image_data = download_image(st.session_state.edited_image)
                if image_data:
                    st.download_button(
                        "⬇️ Download Result",
                        image_data,
                        "generated_fill.png",
                        "image/png"
                    )
            elif st.session_state.pending_urls:
                st.info("Generation in progress. Click the refresh button above to check status.")