import streamlit as st
import requests
import base64
from PIL import Image
import io

def main():
    st.title("Auto Tag Your Fashion Catalog")
    if 'display_language' not in st.session_state:
        st.session_state['display_language'] = 'EN'

    # Display your logo
    display_logo('logo.png')

    # Custom CSS to change font size and other styles
    st.markdown("""
        <style>
        .small-font {
            font-size:10px;
        }
        .image-upload {
            text-align: center;
        }
        </style>
        """, unsafe_allow_html=True)

    st.markdown('<p class="image-upload">Upload an Image (png, jpg, jpeg)</p>', unsafe_allow_html=True)
    uploaded_image = st.file_uploader("", type=["png", "jpg", "jpeg"])

    if uploaded_image is not None:
        # Display the uploaded image
        image = Image.open(uploaded_image)
        image = resize_image(image)
        st.image(image, caption='Uploaded Image', use_column_width='always')

        base64_image = convert_to_base64(image)
        result = load_response(base64_image)

        # Layout for buttons
        col1, col2 = st.columns(2)

        with col1:
            if st.button('EN'):
                st.session_state['display_language'] = 'EN'
        with col2:
            if st.button('AR'):
                st.session_state['display_language'] = 'AR'

        # Conditional display based on the selected language
        if st.session_state['display_language'] == 'EN':
            with col1:
                visualize_tags(result.get('eng_tags', {}), 'Title')
        elif st.session_state['display_language'] == 'AR':
            with col2:
                ar_tags = result.get('ar_tags', {})
                if "Title" in ar_tags:
                    ar_tags["العنوان"] = ar_tags.pop("Title")
                visualize_tags(ar_tags, 'العنوان')


@st.cache_data
def load_response(base64_image):
    """ Cache and load the response from the endpoint. """
    return send_request(base64_image)

def display_logo(logo_path):
    """ Display the logo at the top of the app. """
    logo = Image.open(logo_path)
    st.image(logo, width=130) # Adjust width as needed

def convert_to_base64(image):
    """ Convert the PIL image to a base64 string. """
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode()

def send_request(base64_image):
    """ Send the POST request to the endpoint and return the response. """
    url = "http://s24caeqautotagging.twentytoo.ai/predict_tags"
    data = {"image": base64_image}
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            return response.json()["body"]
        else:
            st.error("Error in API response")
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")


def resize_image(image):
    """ Resize the image while maintaining aspect ratio. """
    base_width = 600
    w_percent = (base_width / float(image.size[0]))
    h_size = int((float(image.size[1]) * float(w_percent)))

    # Updated resizing method for compatibility with newer versions of Pillow
    return image.resize((base_width, h_size), Image.Resampling.LANCZOS)


def visualize_tags(tags, title_key):
    """ Visualize the tags with improved design. """
    if title_key in tags:
        st.markdown(f"##### {tags[title_key]}")
        del tags[title_key]  # Remove the title to avoid duplication

    st.markdown("##### Tags:")
    for key, value in tags.items():
        st.markdown(f"- **{key}**: {value}", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
