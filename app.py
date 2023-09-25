import pandas as pd
import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
from config import settings
from utilities import get_leagues, get_league_matches, view_pred
 
# Sidebar contents
with st.sidebar:
    st.title('AI Email Writer')
    st.markdown('''
    ## About
    This app takes in user's detail and preference and creates a user-tailored sales email using:
    - [Streamlit](https://streamlit.io/)
    - [OpenAI](https://platform.openai.com/docs/models) LLM model
 
    ''')
    add_vertical_space(5)
    
 
#streamlit run app.py

def main():
    '''Main function containing all the logic of the app. The conversation memory is defined,
    and used to trigger the GPT model.'''

    st.header("View Predictions")

    leagues = get_leagues()

    if 'stage' not in st.session_state:
        st.session_state.stage = 0

    def set_stage(stage, league_name=None, match=None):
        st.session_state.stage = stage
        st.session_state.league = league_name
        st.session_state.match = match
    
    with st.form("form_1"):
         st.write("Inside the form")

         league_option = st.selectbox('Please select a League.', leagues)

         # Every form must have a submit button.
         st.form_submit_button("Submit", on_click=set_stage, args=(1, f"{league_option}",))

    if st.session_state.stage > 0:

        st.write(st.session_state.league)
        matches = get_league_matches(st.session_state.league)
        
        with st.form("form_2"):
            st.write("Inside the form")

            match_option = st.selectbox('Please select a League.', matches)

            submitted = st.form_submit_button("Submit", on_click=set_stage, args=(2, f"{st.session_state.league}", f"{match_option}",))
        
        if submitted:
            view_pred(st.session_state.league, match_option)  
            
    st.button('Reset', on_click=set_stage, args=(0,))
 
if __name__ == '__main__':
    main()