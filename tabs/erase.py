import streamlit as st
from PIL import Image
import io
from streamlit_drawable_canvas import st_canvas
from services.erase_foreground import erase_foreground
from utils.download_image import download_image

def render():
    st.header("🎨 Erase Elements")
    st.markdown("Upload an image and select the area you want to erase.")

    uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"], key="erase_upload")
    if uploaded_file:
        col1, col2 = st.columns(2)
        
        with col1:
            # Display original image
            st.image(uploaded_file, caption="Original Image", use_column_width=True)
            
            # Get image dimensions for canvas
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
            
            # Add drawing canvas using Streamlit's drawing canvas component
            stroke_width = st.slider("Brush width", 1, 50, 20, key="erase_brush_width")
            stroke_color = st.color_picker("Brush color", "#fff", key="erase_brush_color")
            
            # Create canvas with background image
            canvas_result = st_canvas(
                fill_color="rgba(255, 255, 255, 0.0)",  # Transparent fill
                stroke_width=stroke_width,
                stroke_color=stroke_color,
                background_color="",  # Transparent background
                background_image=img,  # Pass PIL Image directly
                drawing_mode="freedraw",
                height=canvas_height,
                width=canvas_width,
                key="erase_canvas",
            )
            
            # Options for erasing
            st.subheader("Erase Options")
            content_moderation = st.checkbox("Enable Content Moderation", False, key="erase_content_mod")
            
            if st.button("🎨 Erase Selected Area", key="erase_btn"):
                if not canvas_result.image_data is None:
                    with st.spinner("Erasing selected area..."):
                        try:
                            # Convert canvas result to mask
                            mask_img = Image.fromarray(canvas_result.image_data.astype('uint8'), mode='RGBA')
                            mask_img = mask_img.convert('L')
                            
                            # Convert uploaded image to bytes
                            image_bytes = uploaded_file.getvalue()
                            
                            result = erase_foreground(
                                st.session_state.api_key,
                                image_data=image_bytes,
                                content_moderation=content_moderation
                            )
                            
                            if result:
                                if "result_url" in result:
                                    st.session_state.edited_image = result["result_url"]
                                    st.success("✨ Area erased successfully!")
                                else:
                                    st.error("No result URL in the API response. Please try again.")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                            if "422" in str(e):
                                st.warning("Content moderation failed. Please ensure the image is appropriate.")
                else:
                    st.warning("Please draw on the image to select the area to erase.")
        
        with col2:
            if st.session_state.edited_image:
                st.image(st.session_state.edited_image, caption="Result", use_column_width=True)
                image_data = download_image(st.session_state.edited_image)
                if image_data:
                    st.download_button(
                        "⬇️ Download Result",
                        image_data,
                        "erased_image.png",
                        "image/png",
                        key="erase_download"
                    )