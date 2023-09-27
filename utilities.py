import pandas as pd
import psycopg2, json
from config import settings
import streamlit as st


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
    get_query = f"SELECT league FROM match_prediction"
    cursor.execute(get_query)

    rows = cursor.fetchall()
    #Commit and close connection
    cursor.close()
    connection.close()

    #Converting the data extracted to a DataFrame for analysis
    df = pd.DataFrame(rows, columns=['league'])
    leagues = tuple(set(list(df['league'])))
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
    matches = []
    for i in range(df.shape[0]):
        matches.append(f"{list(df['date'])[i]}_{list(df['hometeam'])[i]}_{list(df['awayteam'])[i]}")
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
    return df


def view_pred(league, selected_option):
    '''Takes the league and match and extracts the predictions. It also combines
    the teams prediction with the referee's prediction'''

    list_of_condition = selected_option.split('_')
    prediction = get_predictions(league, list_of_condition[0], list_of_condition[1], list_of_condition[2])
    try:
        ref_predictions = get_refpredictions()
    except:
        ref_predictions = pd.DataFrame([], columns=['date', 'time', 'hometeam', 'awayteam', 'result', 'matchlink', 'league', 'refereelink', 'referee_matchistlink', 'referee_matchhistdetails', 'ref_patterns'])

    corr_refpred = [] #Correspondng Referee Prediction for the same Match set up.

    if ref_predictions.shape[0] > 0:
        for j in range(ref_predictions.shape[0]):
            if (list(prediction['hometeam'])[0] in list(ref_predictions.iloc[j,:])[2]) & (list(prediction['awayteam'])[0] in list(ref_predictions.iloc[j,:])[3]) & (list(prediction['league'])[0] == list(ref_predictions.iloc[j,:])[6]):
                corr_refpred.append(list(ref_predictions.iloc[j,:])[10])
    
    if len(corr_refpred) > 0:
        prediction['ref_predictions'] = corr_refpred
        col_of_prediction = ['home_score_patterns', 'away_score_patterns', 'h2h_score_patterns', 'ref_predictions', 'innerdetail_analysis']
        for column in col_of_prediction:
            with st.expander(f"Predictions assiciated with {column}"):
                st.write('--'*20)
                predictions = list(prediction[column])[0]
                if column == 'innerdetail_analysis':
                    for key in list(predictions.keys()):
                        st.write(f"{key}: {predictions[key]}")
                else:
                    for key in list(predictions.keys()):
                        st.write(f"{predictions[key]}")
    else:
        col_of_prediction = ['home_score_patterns', 'away_score_patterns', 'h2h_score_patterns', 'innerdetail_analysis']
        for column in col_of_prediction:
            with st.expander(f"Predictions assiciated with {column}"):
                st.write('--'*20)
                predictions = list(prediction[column])[0]
                if column == 'innerdetail_analysis':
                    for key in list(predictions.keys()):
                        st.write(f"{key}: {predictions[key]}")
                else:
                    for key in list(predictions.keys()):
                        st.write(f"{predictions[key]}")

def set_stage(stage):
        st.session_state.stage = stage

def form(leagues_matches, league):
    with st.form(str(league)):
        st.write(f"{league}")

        #Creates a list of options with repesct to the available predictions
        selected_option = st.selectbox('Please select a Match.', leagues_matches)

        #Submit the selected option
        submitted = st.form_submit_button("Submit", on_click=set_stage, args=(1,))

    if submitted:
        view_pred(league, selected_option)