import pandas as pd
import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
from utilities import get_leagues, get_league_matches, view_pred, form, set_stage
 
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
    st.markdown('''
    Note (Prediction Colours and Sources):
                
    Colour - Red : Source - Home Team History 
                
    Colour - Orange : Source - Away Team History
                
    Colour - Green : Source - Head-to-Head History
                
    Colour - Lightblue : Source - Referee's History
    ''')
    add_vertical_space(1) 
    st.markdown(markdown_string)
    add_vertical_space(5)  
 
#streamlit run app.py
def main(league_list):
    st.header("View Predictions")

    if 'stage' not in st.session_state:
        st.session_state.stage = 0

    for league in league_list:
        leagues_matches = get_league_matches(league)
        form(leagues_matches, league)
            
    #Reset button
    st.button('Reset', on_click=set_stage, args=(0,))
 
if __name__ == '__main__':
    main(leagues)