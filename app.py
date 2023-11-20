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
        .rtl {
            direction: rtl;
        }
        </style>
        """, unsafe_allow_html=True)

    st.markdown('<p class="image-upload">Upload an Image (png, jpg, jpeg)</p>', unsafe_allow_html=True)
    uploaded_image = st.file_uploader("", type=["png", "jpg", "jpeg"])

    if uploaded_image is not None:
        # Display the uploaded image and tags side by side
        col1, col2 = st.columns([3, 2])  # Adjust the column ratio as needed

        with col1:
            # Display the uploaded image
            image = Image.open(uploaded_image)
            image = resize_image(image)
            st.image(image, caption='Uploaded Image', use_column_width=True)

        with col2:
            # Load and display tags
            base64_image = convert_to_base64(image)
            result = load_response(base64_image)

            # Button to switch languages
            button_label = 'EN' if st.session_state['display_language'] == 'AR' else 'AR'
            if st.button(button_label):
                new_language = 'AR' if st.session_state['display_language'] == 'EN' else 'EN'
                st.session_state['display_language'] = new_language

            # Conditional display based on the selected language
            if st.session_state['display_language'] == 'EN':
                visualize_tags(result.get('eng_tags', {}), 'Title')
                st.session_state['display_language'] = 'AR'
            elif st.session_state['display_language'] == 'AR':
                ar_tags = result.get('ar_tags', {})
                if "Title" in ar_tags:
                    ar_tags["العنوان"] = ar_tags.pop("Title")
                visualize_tags(ar_tags, 'العنوان')
                st.session_state['display_language'] = 'EN'


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
        title_class = "rtl" if st.session_state['display_language'] == 'AR' else ""
        st.markdown(f"<h5 class='{title_class}'>{tags[title_key]}</h5>", unsafe_allow_html=True)
        del tags[title_key]  # Remove the title to avoid duplication

    tag_class = "rtl" if st.session_state['display_language'] == 'AR' else ""
    st.markdown(f"<h5 class='{tag_class}'>Tags:</h5>", unsafe_allow_html=True)
    for key, value in tags.items():
        st.markdown(f"<div class='{tag_class}'>- <b>{key}</b>: {value}</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
