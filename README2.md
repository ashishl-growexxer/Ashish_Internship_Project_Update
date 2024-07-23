Project Plan 
Indian Airline Fare Prediction is Internship Project is an Data Science Project comprising of multiple parts. Indian Airline Flight Prediction is based on Real time streaming data on Indian Airline data which is stored in snowflake using Data ETL pipelines. The Data is preprocessed and used in Machine learning . Furthermore an LLM is used to query data and write responses to interact with users in natural language. Lastly a dashboard Is created to visualize hidden trends and patterns in data. 

1. Mission Objectives
   
    • Develop a real-time data pipeline for flights data .
    • Implement machine learning models for data insights.
    • Create a user-friendly interface for natural language querying of data.
    • Prepare Visualizations illustrating trends and hidden patterns in data.

How to Implement the project
Data Ingestion and TL
1. Install kafka on the device and run commands shown in nn_final_code/01 Kafka Start
2. Give csv path and run nn_final_Code/02 kafka Producer
3. Give right IAM access key and secret access key in nn_final_code/spark s3 deployer.
4. Give appropriate paths and location to lambda and paste code written in "nn Final_Code/01 Lambda S3 trigger Glue.py"
5. Add file_name parameter,and appropriate snowflake credentials in Glue Job and add code mentioned in "nn Final_Code/02 Glue to Snowflake.py"
6. Run all files sequentially

Machine Learning
1. Configure files paths in "04 ML and EDA/InternshipProject(1).ipynb" and run all of them sequentially
2. Create an EC2 in AWS and develop a virtual enviroment as mentioned in documentation.
3. Alter paths mentioned in app.py and deploy it.
4. Run it with python3 app.py

UI interaction
1. Generate an gemini pro API key.
2. Follow steps mentioned in https://youtu.be/wFdFLWc-W4k?si=y7E6qE0B57Ry2yTT from LLM text to sql in Kris naik.
3. Add snowflake connection and credentials for same
4. Alter the prompt and change it as shown in nn_final_code/app.py
5. Run by streamlit run app.py  

Data Visualisation .
1. make Snowflake connection in Power Bi desktop
2. create dashboard as you see fit.
    
