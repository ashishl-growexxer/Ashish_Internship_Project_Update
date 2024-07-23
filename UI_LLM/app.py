from dotenv import load_dotenv
from snowflake.connector.pandas_tools import write_pandas
import snowflake.connector
import credentials
import pandas as pd
load_dotenv() ## load all the environemnt variables

import streamlit as st
import os
import google.generativeai as genai

## Configure Genai Key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

## Function To Load Google Gemini Model and provide queries as response
conn = snowflake.connector.connect(
    user= 'YOUR USERNAME',
    password='YOUR PASSOWRD',
    account='YOUR ACCOUNT',
    warehouse="YOUR_WAREHOUSE",
    database='YOURDATABASE',
    schema='YOURCHEMA',
    role='ROLE'
)
cur= conn.cursor()

def get_gemini_response(question,prompt):
    model=genai.GenerativeModel('gemini-pro')
    response=model.generate_content([prompt[0],question])
    print(response.parts[0].text)
    return response.parts[0].text
    

## Fucntion To retrieve query from the database
def read_sql_query(sql):
    cur.execute("USE WAREHOUSE COMPUTE_WH;")
    cur.execute(sql)
    datafetch= cur.fetchall()
    df =pd.DataFrame(datafetch)
    df.head()
    return df

## Define Your Prompt
prompt=[
    """
    You are an expert in converting English questions to SQL query!
    The SQL table has the name INTERNSHIPDATABASE.PROJECTSCHEMA.STOREFLIGHT and has the following columns: DATE_OF_BOOKING,DURATION ,TOTAL_STOPS, PRICE ,COMPANY,FLIGHT_ROUTE, TICKET_CLASS, DEPARTURE_LOCATION, ARRIVAL_LOCATION, JRNDATETIME, ARIVDATETIME, DAYSTILLJOURN 
    DATE_OF_BOOKING represents the date of flight Booking.JRNDATETIME, ARIVDATETIME represent Journey timestamp andarrival timestamp respectively.
    Total Stops - ['non-stop', '1-stop', '2+-stop']
    Company - ['SpiceJet ', 'Indigo ', 'GO FIRST ', 'Air India ', 'AirAsia ', 'Vistara ', 'AkasaAir ', 'AllianceAir ', 'StarAir ']
    Ticket_Class -['ECONOMY', 'PREMIUMECONOMY', 'BUSINESS', 'FIRST']
    DEPARTURE_LOCATION ['Delhi', 'Mumbai', 'Bangalore', 'Hyderabad', 'Kolkata', 'Chennai', 'Ahmedabad'],
    ARRIVAL_LOCATION ['Mumbai', 'Bangalore', 'Hyderabad', 'Kolkata', 'Chennai', 'Ahmedabad', 'Delhi']

    PRICE is an integer field,DURATION is is float value representing number of hours of journey.
    FLIGHT_ROUTE is another VARCHAR field with large number of categories. 
    DAYSTILLJOURN is Integer value of days between Date of Booking and journey date.
    There can be null values for any of these fields. Please make sure that code query does not consider null values in any categorical fields.
    \n\nFor example,\nExample 1 - How many entries of records are present?, 
    the SQL command will be something like this SELECT COUNT(*) FROM INTERNSHIPDATABASE.PROJECTSCHEMA.STOREFLIGHT ;
    \nExample 2 - Tell me approximate duration for flight traveling from Mumbai to Delhi?, 
    the SQL command will be something like this SELECT AVG(DURATION) FROM INTERNSHIPDATABASE.PROJECTSCHEMA.STOREFLIGHT
    WHERE DEPARTURE_LOCATION='Mumbai' AND ARRIVAL_LOCATION='Delhi'; 
    \nExample 3 - How does the time of day affect flight duration and price?,
    the sql command will be something like SELECT AVG(DURATION), AVG(PRICE) ,SUBSTR(JRNDATETIME, 12, 2) AS HOUR_OF_DAY FROM INTERNSHIPDATABASE.PROJECTSCHEMA.STOREFLIGHT WHERE DAYSTILLJOURN > 0 AND DURATION IS NOT NULL  AND PRICE IS NOT NULL GROUP BY HOUR_OF_DAY ORDER BY HOUR_OF_DAY;
    \nExample 4 - What is the price distribution for different companies?
    the sql command will be something like SELECT COMPANY,AVG(PRICE),MAX(PRICE),MIN(PRICE) FROM INTERNSHIPDATABASE.PROJECTSCHEMA.STOREFLIGHT WHERE COMPANY IS NOT NULL GROUP BY COMPANY 
    \nExample 5 - What is the average number of stops per flight?
    the sql command will be something like SELECT AVG(stops) AS avg_stops FROM (SELECT CASE WHEN TOTAL_STOPS = 'non-stop' THEN 0 WHEN TOTAL_STOPS = '1-stop' THEN 1 WHEN TOTAL_STOPS = '2+-stop' THEN 2 ELSE NULL END AS stops FROM INTERNSHIPDATABASE.PROJECTSCHEMA.STOREFLIGHT ) AS stops_table;
    \n
    the sql command will be something like SELECT ARRIVAL_LOCATION, AVG(stops) AS avg_stops, COUNT(*) AS total_flights FROM (SELECT ARRIVAL_LOCATION,CASE WHEN TOTAL_STOPS = 'non-stop' THEN 0 WHEN TOTAL_STOPS = '1-stop' THEN 1 WHEN TOTAL_STOPS = '2+-stop' THEN 2 -- Assuming '2+-stop' counts as 2 stops for calculation ELSE NULL END AS stops FROM STOREFLIGHT ) AS stops_table WHERE ARRIVAL_LOCATION IS NOT NULL GROUP BY ARRIVAL_LOCATION ORDER BY avg_stops DESC;
    These are just examples with specific cases. Please only give me SQL query and nothing More
    also the sql code should not have ``` in beginning or end and sql word in output
    """
]

## Streamlit App

st.set_page_config(page_title="I can Retrieve Any SQL query")
st.header("Gemini App To Retrieve SQL Data")

question=st.text_input("Input: ",key="input")
submit=st.button("Ask the question")

strintro ="""The flight data set provides comprehensive details about various flights, including booking information, flight duration, pricing, stops, and routes. This data is primarily focused on flights within India and contains crucial information that can be used for detailed analysis and insights. Below is a brief description of each column present in the dataset:

    DATE_OF_BOOKING: This column captures the date when the flight booking was made.
    DURATION: The total duration of the flight in number of hours in float type
    TOTAL_STOPS: Represents the number of stops during the flight, with possible values including 'non-stop', '1-stop', and '2+-stop'.
    PRICE: The cost of the flight ticket, denoted in Indian Rupees.
    COMPANY: The airline company operating the flight given in data are 'SpiceJet', 'Indigo', 'GO FIRST', 'Air India', 'AirAsia', 'Missing', 'Vistara', 'AkasaAir', 'AllianceAir', 'StarAir'
    FLIGHT_ROUTE: The route taken by the flight, specifying the path from the departure location to the arrival location. Around 200 different routes
    TICKET_CLASS: The class of the ticket, such as economy, business, etc. 
    DEPARTURE_LOCATION: The location from which the flight departs.
    ARRIVAL_LOCATION: The destination or arrival location of the flight.
    JRNDATETIME: The exact date and time when the journey starts.
    DAYSTILLJOURN: The number of days between the booking date and the journey date.
    ARIVDATETIME: The exact date and time when the flight arrives at its destination."""
# if submit is clicked

st.write(strintro)

if submit:
    st.write(question)
    response=get_gemini_response(question,prompt)
    st.write(response)
    response= read_sql_query(response)
    st.subheader("The Response is")
    print(response)
    st.write(response)
