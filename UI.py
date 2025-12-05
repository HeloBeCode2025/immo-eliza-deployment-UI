import streamlit as st
import requests
import json
from pgeocode import Nominatim
import pandas as pd
import math

# Create the GeoNames instance for Belgium (country code "BE")
geo = Nominatim(country='be')

# Create property dictionary to predict, with average values and nulls as default
property = {
  "locality_name": "Bruxelles",
  "postal_code": 1000,
  "price": 0,
  "type_of_property": "House",
  "subtype_of_property": "House",
  "number_of_rooms": 4,
  "living_area": 180,
  "equipped_kitchen": 1,
  "furnished": 0.0,
  "open_fire": 0.0,
  "terrace": 0.0,
  "garden": 0.0,
  "number_of_facades": 3,
  "swimming_pool": 0.0,
  "state_of_building": "GOOD",
  "garden_surface": 0.0,
  "terrace_surface": 0
}

if "property_data" not in st.session_state:
    st.session_state.property_data = property.copy()

def get_locality(postal_code):
    try:
        # pgeocode expects a string or int; we normalize to string
        results = geo.query_postal_code(str(int(postal_code)))

        # If results is NaN or empty, it's invalid
        if results is None or (isinstance(results, float) and math.isnan(results)):
            return None

        # In pgeocode, the column is 'place_name'
        place = results.get("place_name", None)

        if place is None or (isinstance(place, float) and pd.isna(place)):
            return None

        return place

    except Exception:
        return None


import base64
from pathlib import Path

def image_button(png_path: str, key: str, size: int = 48, position: str | None = None) -> bool:
    """
    Renders a button that visually looks like just an image.
    Returns True when clicked.

    position:
        - "first" → style the first st.button on the page
        - "last"  → style the last st.button on the page
        - None    → style all (fallback, not recommended here)
    """

    # Render a normal button (will be restyled)
    clicked = st.button(" ", key=key)

    # Read and encode the local image
    file = Path(png_path)
    if file.exists():
        b64 = base64.b64encode(file.read_bytes()).decode()

        # choose which button(s) to target in CSS
        if position == "first":
            pseudo = ":first-of-type"
        elif position == "last":
            pseudo = ":last-of-type"
        else:
            pseudo = ""

        st.markdown(
            f"""
            <style>
            div[data-testid="stButton"] button[kind="secondary"]{pseudo} {{
                background-image: url("data:image/png;base64,{b64}");
                background-size: contain;
                background-repeat: no-repeat;
                background-position: center;
                height: {size}px;
                width: {size}px;
                padding: 0;
                border: none;
                color: transparent; /* hide any label text */
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.error(f"Icon not found: {file}")

    return clicked

def button_click(page):
    st.session_state.page = page

# Welcome Page
def welcome_page():
    st.title("Welcome to Our Prediction App!")
    st.markdown("""
    <p style="font-size:20px;">We are glad to have you here! Click the button below to start the prediction process.</p>
    """, unsafe_allow_html=True)

    # Custom pink button with large text
    if st.button("Let's start!", key="start_button", use_container_width=True):
        st.session_state.page = "Step 1"
        st.rerun()

def postal_code_page():
    st.title("Where is your property? 1/3")

    # input postal code
    postal_code_input = st.number_input("Enter your postal code:", min_value=0, step=1, key="postal_code")
    
    # Check if the postal code is valid
    if postal_code_input > 0:
        try:
            postal_code = int(postal_code_input)  # Convert input to integer to handle non-numeric input
            locality = get_locality(postal_code)

            # Provide feedback for the postal code
            if locality:
                st.success(f"Valid postal code! The locality for postal code {postal_code} is: {locality}")
                # enter inputs in the property data
                st.session_state.property_data["postal_code"] = postal_code_input
                st.session_state.property_data["locality_name"] = locality
            else:
                st.error(f"Invalid postal code! Please try again.")
        except ValueError:
            st.error("Please enter a valid numeric postal code.")

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
    
        #if image_button("icons/left-arrow.png", key="back_arrow"):
            #st.session_state.page = "Welcome"
        back = st.button("⬅️", key="Back1", help="Previous")
        if back:
            st.session_state.page = "Welcome"
            st.rerun()


    with col3:
        #if image_button("icons/right-arrow.png", key="next_arrow"):
         #   st.session_state.page = "Step 2"
        next = st.button("➡️", key="Next1", help = "Next")
        if next:
            st.session_state.page = "Step 2"
            st.rerun()

def general_page():
    st.title("What is your property like? 2/3")

    subtype_options = {
        "House": [
        "House",
        "Villa",
        "Chalet",
        "Cottage",
        "Bungalow",
        "Mansion",
        "MasterHouse",
        "Unknown"
    ],
        "Apartment": [
        "Flat",
        "FlatStudio",
        "Duplex",
        "Triplex",
        "GroundFloor",
        "Penthouse",
        "Loft",
        "MixedBuilding",
        "Unknown"
    ],
    }
    with st.expander("🏠 Property type"):
        # Dropdown menus
        type = st.selectbox("Type of property:", ['House', 'Apartment'], key="type_of_property")
        available_subtypes = subtype_options[type]

        # 4) Pick default subtype:
        #    - if a previous value exists AND is valid → reuse it
        #    - otherwise → first subtype in the list
        prev_subtype = st.session_state.property_data.get("subtype_of_property")
        if prev_subtype not in available_subtypes:
            prev_subtype = available_subtypes[0]
            st.session_state.property_data["subtype_of_property"] = prev_subtype

        subtype = st.selectbox(
            "Subtype of property:",
            available_subtypes,
            index=available_subtypes.index(prev_subtype),
            key="subtype_of_property",
        )
        state = st.selectbox("State:", [
            'Normal',
            'To renovate',
            'Excellent',
            'Fully renovated',
            'New',
            'To restore',
            'Under construction',
            'To demolish'
            'Unknown',
        ],key ="state_of_building")
        
    with st.expander("🏠 Property basics"): 
        
        facades = st.selectbox("Number of facades:", ['1', '2', '3', '4'], key="number_of_facades")
        area = st.number_input(
            "Living area (m²)",
            min_value=0,
            step=1,
            key="living_area"
        )
        rooms = st.number_input("Number of bedrooms:", min_value=0, step=1, key="number_of_rooms")
        

    st.session_state.property_data["type_of_property"] = st.session_state["type_of_property"]
    st.session_state.property_data["subtype_of_property"] = st.session_state["subtype_of_property"]
    st.session_state.property_data["state_of_building"] = st.session_state["state_of_building"]
    st.session_state.property_data["number_of_facades"] = st.session_state["number_of_facades"]
    st.session_state.property_data["number_of_rooms"] = st.session_state["number_of_rooms"]
    st.session_state.property_data["living_area"] = st.session_state["living_area"]

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        back = st.button("⬅️", key="Back2", help="Previous")
        if back:
            st.session_state.page = "Step 1"
            st.rerun()

    with col3:
        next = st.button("➡️", key="Next2", help = "Next")
        if next:
            st.session_state.page = "Step 3"
            st.rerun()

def extra_page():
    st.title("Anything ✨extras✨?  3/3")

    garden = st.selectbox("Is there a garden?:", ['Yes', 'No'], key="garden")
    if garden == "Yes":
        st.number_input(
            "Garden surface (m²)",
            min_value=0,
            step=1,
            key="garden_surface"
        )
    else:
        st.session_state.garden_surface = 0.0

    terrace = st.selectbox("Is there a terrace?:", ['Yes', 'No'], key="terrace")
    if terrace == "Yes":
        st.number_input(
            "Terrace surface (m²)",
            min_value=0,
            step=1,
            key="terrace_surface"
        )
    else:
        st.session_state.terrace_surface = 0

    pool = st.selectbox("Is there a swimming pool?:", ['Yes', 'No'], key="swimming_pool")
    fireplace = st.selectbox("Is there a fireplace?:", ['Yes', 'No'], key="open_fire")
    pool = st.selectbox("Is there an equipped kitchen?:", ['Yes', 'No'], key="equipped_kitchen")
    pool = st.selectbox("Is the place furnished?:", ['Yes', 'No'], key="furnished")

    for spec in ["equipped_kitchen", "furnished","open_fire", "terrace","garden","swimming_pool"]:
        if st.session_state[spec] == "Yes":
            st.session_state.property_data[spec] = 1.0
        else :
            st.session_state[spec] = 0.0

    st.session_state.property_data["garden_surface"] = st.session_state["garden_surface"]
    st.session_state.property_data["terrace_surface"] = st.session_state["terrace_surface"]

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        back = st.button("⬅️", key="Back3", help="Previous")
        if back:
            st.session_state.page = "Step 2"
            st.rerun()

    with col3:
        next = st.button("➡️", key="Next3", help = "Next")
        if next:
            st.session_state.page = "Prediction"
            st.rerun()


def prediction_page(user_data: dict):
    st.title("Price prediction")

    # 1) Build the payload: start from defaults, then override with user choices
    payload = property.copy()          # global template at the top of your file
    payload.update(user_data or {})    # make sure session data wins

    st.subheader("Your inputs")
    st.json(payload)

    # 2) Call the API when the user clicks the button
    if st.button("Get prediction", key="predict_button", use_container_width=True):
        try:
            API_URL = "http://127.0.0.1:8000/predict"  # adjust if different

            response = requests.post(API_URL, json=payload, timeout=10)

            if response.status_code == 200:
                data = response.json()

                # Handle typical response formats
                prediction = None
                if isinstance(data, dict):
                    # Expected: {"prediction": 123456.78}
                    prediction = data.get("prediction")
                    # If API returns just a float under another key, fallback:
                    if prediction is None and len(data) == 1:
                        prediction = list(data.values())[0]
                else:
                    # e.g. [123456.78]
                    try:
                        prediction = float(data[0])
                    except Exception:
                        prediction = None

                if prediction is not None:
                    st.success(f"Estimated price: € {prediction:,.0f}")
                    st.session_state.last_prediction = float(prediction)
                else:
                    st.error(f"Unexpected response format from API: {data}")

            else:
                st.error(f"API error {response.status_code}: {response.text}")

        except Exception as e:
            st.error(f"Error while calling the API: {e}")

    # 3) Navigation: allow going back to adjust inputs
    if st.button("New prediction", key="new_prediction"):
        st.session_state.page = "Welcome"
        st.rerun()


# Main function to handle page flow
def main():
    # Check if session state is initialized, otherwise initialize it
    if 'page' not in st.session_state:
        st.session_state.page = "Welcome"
    
    # Navigate between pages based on the current session state
    if st.session_state.page == "Welcome":
        welcome_page()
    
    elif st.session_state.page == "Step 1":
        postal_code_page()
    
    elif st.session_state.page == "Step 2":
        general_page()

    elif st.session_state.page == "Step 3":
        extra_page()
    
    elif st.session_state.page == "Prediction":
        prediction_page(st.session_state.property_data)



if __name__ == "__main__":
    main()