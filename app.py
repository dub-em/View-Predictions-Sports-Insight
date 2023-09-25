import pandas as pd
import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
from utilities import get_leagues, get_league_matches, view_pred
 
# Sets a wider page layout for visualisation
st.set_page_config(layout="wide") 

# Sets up the available Leagues with prediction for the Sidebar display
markdown_string = '''Available Leagues with Prediction'''
leagues = get_leagues()
for league_name in leagues:
    markdown_string = markdown_string + f"\n- {league_name}"

# Sidebar contents
with st.sidebar:
    st.title('Sports Insights')
    add_vertical_space(2) 
    st.markdown('''
    ## About
    This app extracts the historic scores for teams in a given match setup, analyses this data and makes prediction:
    ''')
    add_vertical_space(2) 
    st.markdown(markdown_string)
    add_vertical_space(5)  
 
#streamlit run app.py
def main():
    '''Main function containing all the logic of the app. The conversation memory is defined,
    and used to trigger the GPT model.'''
    st.header("View Predictions")

    leagues_matches = get_league_matches()

    if 'stage' not in st.session_state:
        st.session_state.stage = 0

    def set_stage(stage):
        st.session_state.stage = stage
    
    with st.form("form_1"):
        st.write("Inside the form")

        #Creates a list of options with repesct to the available predictions
        selected_option = st.selectbox('Please select a League.', leagues_matches)

        #Submit the selected option
        submitted = st.form_submit_button("Submit", on_click=set_stage, args=(1,))

    if submitted:
        view_pred(selected_option)
            
    #Reset button
    st.button('Reset', on_click=set_stage, args=(0,))
 
if __name__ == '__main__':
    main()