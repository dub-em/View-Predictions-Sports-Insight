import pandas as pd
import psycopg2
from config import settings
import streamlit as st
from datetime import date, timedelta


def get_leagues():
    '''This function gets a list of all the leagues with "interesting" predictions'''

    #PostgreSQL database connection parameters
    connection_params = {
        "host": settings.database_hostname,
        "port": settings.database_port,
        "database": settings.database_name,
        "user": settings.database_user,
        "password": settings.database_password
    }

    #Connect to PostgreSQL
    connection = psycopg2.connect(**connection_params)
    cursor = connection.cursor()

    #Create the table in the database
    get_query = f"SELECT date, league FROM match_prediction"
    cursor.execute(get_query)

    rows = cursor.fetchall()
    #Commit and close connection
    cursor.close()
    connection.close()

    #Converting the data extracted to a DataFrame for analysis
    df = pd.DataFrame(rows, columns=['date', 'league'])
    df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d %H:%M:%S")

    yesterday = date.today() + timedelta(days=-1)
    today = date.today()
    tomorrow = date.today() + timedelta(days=1)
    today_df = df[(df['date'].dt.date == yesterday) | (df['date'].dt.date == today) | (df['date'].dt.date == tomorrow)]
    leagues = tuple(set(list(today_df['league'])))
    return leagues


def get_league_matches(league):
    '''This function gets a list of all the matches from all the leagues'''

    #PostgreSQL database connection parameters
    connection_params = {
        "host": settings.database_hostname,
        "port": settings.database_port,
        "database": settings.database_name,
        "user": settings.database_user,
        "password": settings.database_password
    }

    #Connect to PostgreSQL
    connection = psycopg2.connect(**connection_params)
    cursor = connection.cursor()

    #Create the table in the database
    get_query = f"SELECT date, hometeam, awayteam FROM match_prediction WHERE league = '{league}'"
    cursor.execute(get_query)

    rows = cursor.fetchall()
    #Commit and close connection
    cursor.close()
    connection.close()

    #Converting the data extracted to a DataFrame for analysis
    df = pd.DataFrame(rows, columns=['date','hometeam','awayteam'])
    df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d %H:%M:%S")

    yesterday = date.today() + timedelta(days=-1)
    today = date.today()
    tomorrow = date.today() + timedelta(days=1)
    today_df = df[(df['date'].dt.date == yesterday) | (df['date'].dt.date == today) | (df['date'].dt.date == tomorrow)]
    
    matches = []
    for i in range(today_df.shape[0]):
        matches.append(f"{list(today_df['date'])[i]}_{list(today_df['hometeam'])[i]}_{list(today_df['awayteam'])[i]}")
    matches = tuple(matches)
    matches
    return matches


def get_predictions(league, date, home_team, away_team):
    '''This function gets the predictions from the selected match'''

    #PostgreSQL database connection parameters
    connection_params = {
        "host": settings.database_hostname,
        "port": settings.database_port,
        "database": settings.database_name,
        "user": settings.database_user,
        "password": settings.database_password
    }

    #Connect to PostgreSQL
    connection = psycopg2.connect(**connection_params)
    cursor = connection.cursor()

    #Create the table in the database
    get_query = f"SELECT hometeam, awayteam, league, home_score_patterns, away_score_patterns, h2h_score_patterns, innerdetail_analysis FROM match_prediction WHERE league = '{league}' AND date = '{date}' AND hometeam = '{home_team}' AND awayteam = '{away_team}'"
    cursor.execute(get_query)

    rows = cursor.fetchall()
    #Commit and close connection
    cursor.close()
    connection.close()

    #Converting the data extracted to a DataFrame for analysis
    df = pd.DataFrame(rows, columns=['hometeam', 'awayteam', 'league', 'home_score_patterns', 'away_score_patterns', 'h2h_score_patterns', 'innerdetail_analysis'])
    return df


def get_refpredictions():
    '''This function gets all the predictions from the ref dataset'''

    #PostgreSQL database connection parameters
    connection_params = {
        "host": settings.database_hostname,
        "port": settings.database_port,
        "database": settings.database_name,
        "user": settings.database_user,
        "password": settings.database_password
    }

    #Connect to PostgreSQL
    connection = psycopg2.connect(**connection_params)
    cursor = connection.cursor()

    #Create the table in the database
    get_query = f"SELECT * FROM ref_match_pred"
    cursor.execute(get_query)

    rows = cursor.fetchall()
    #Commit and close connection
    cursor.close()
    connection.close()

    #Converting the data extracted to a DataFrame for analysis
    df = pd.DataFrame(rows, columns=['date', 'time', 'hometeam', 'awayteam', 'result', 'matchlink', 'league', 'refereelink', 'referee_matchistlink', 'referee_matchhistdetails', 'ref_patterns'])
    df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d %H:%M:%S")

    yesterday = date.today() + timedelta(days=-1)
    today = date.today()
    tomorrow = date.today() + timedelta(days=1)
    today_df = df[(df['date'].dt.date == yesterday) | (df['date'].dt.date == today) | (df['date'].dt.date == tomorrow)]
    
    return today_df


def view_pred(league, selected_option):
    '''Takes the league and match and extracts the predictions. It also combines
    the teams prediction with the referee's prediction'''

    list_of_condition = selected_option.split('_')
    prediction = get_predictions(league, list_of_condition[0], list_of_condition[1], list_of_condition[2])
    #print(prediction.shape[0])
    try:
        ref_predictions = get_refpredictions()
    except:
        ref_predictions = pd.DataFrame([], columns=['date', 'time', 'hometeam', 'awayteam', 'result', 'matchlink', 'league', 'refereelink', 'referee_matchistlink', 'referee_matchhistdetails', 'ref_patterns'])

    #print(ref_predictions.shape[0])
    corr_refpred = [] #Correspondng Referee Prediction for the same Match set up.

    if ref_predictions.shape[0] > 0:
        for i in range(prediction.shape[0]):
            for j in range(ref_predictions.shape[0]):
                if (list(prediction['hometeam'])[i] in list(ref_predictions['hometeam'])[j]) & (list(prediction['awayteam'])[i] in list(ref_predictions['awayteam'])[j]) & (list(prediction['league'])[i] == list(ref_predictions['league'])[j]):
                    corr_refpred.append(list(ref_predictions['ref_patterns'])[j])
                    
        
    #print(len(corr_refpred))
    col_of_prediction = ['home_score_patterns', 'away_score_patterns', 'h2h_score_patterns']

    if len(corr_refpred) > 0:
        prediction['ref_predictions'] = corr_refpred
        col_of_prediction = ['home_score_patterns', 'away_score_patterns', 'h2h_score_patterns', 'ref_predictions']
    
    scores_dict = {}
    #print(col_of_prediction)
    for column in col_of_prediction:
        if 'NoneType' not in str(type(list(prediction[column])[0])):
            #print(type(list(prediction[column])[0]))
            for key in (list(prediction[column])[0]).keys():
                if (list(prediction[column])[0])[key][-5:] not in list(scores_dict.keys()):
                    scores_dict[str((list(prediction[column])[0])[key][-5:])] = [str((list(prediction[column])[0])[key][:-7])]
                else:
                    scores_dict[str((list(prediction[column])[0])[key][-5:])].append(str((list(prediction[column])[0])[key][:-7]))

    data = {'Category': list(scores_dict.keys()),
            'Value': [len(scores_dict[key]) for key in list(scores_dict.keys())]}

    # Create a DataFrame from the data
    plot_df = pd.DataFrame(data)

    with st.expander(f"Frequency of Predictions"):
        st.write('--'*20)
        # Display the data as a bar chart
        st.bar_chart(plot_df.set_index('Category')['Value'])

    for key in list(scores_dict.keys()):
        with st.expander(f"Prediction: {key}"):
            st.write('--'*20)
            for source in scores_dict[key]:
                if 'home' in source:
                    st.write(f'<span style="color: red;">{source}</span>', unsafe_allow_html=True)
                elif 'away' in source:
                    st.write(f'<span style="color: orange;">{source}</span>', unsafe_allow_html=True)
                elif 'head-to-head' in source:
                    st.write(f'<span style="color: green;">{source}</span>', unsafe_allow_html=True)
                elif 'ref' in source:
                    st.write(f'<span style="color: blue;">{source}</span>', unsafe_allow_html=True)
                else:
                    st.write(f'{source}')

    with st.expander(f"Inner Details Analysis"):
        st.write('--'*20)
        inner_detail = list(prediction['innerdetail_analysis'])[0]
        for key in list(inner_detail.keys()):
            st.write(f"{key}: {inner_detail[key]}")

def set_stage(stage):
        st.session_state.stage = stage

def form(leagues_matches, league):
    with st.form(str(league)):
        #Creates a link for each form so that each form can be easily navigated to from the sidebar.
        league_link = str(league).replace(' ','_')
        st.markdown(f"<a name='_{league_link}'></a>", unsafe_allow_html=True)
        
        st.write(f"{league}")

        #Creates a list of options with repesct to the available predictions
        selected_option = st.selectbox('Please select a Match.', leagues_matches)

        #Submit the selected option
        submitted = st.form_submit_button("Submit", on_click=set_stage, args=(1,))

    if submitted:
        view_pred(league, selected_option)