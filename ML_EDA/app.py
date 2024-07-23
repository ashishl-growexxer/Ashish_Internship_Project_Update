import numpy as np
from flask import Flask ,request,render_template
import pickle
from datetime import datetime

app = Flask(__name__)

# model = pickle.load(open("","rb"))

@app.route("/")

def Home():
    return render_template("index")

@app.route('/predict',methods =["POST"])


def predict():

    columns_keys=[x for x in request.form.keys()]
    # ['Date_of_Booking', 'Date_of_Journey', 'Duration', 'Total_Stops', 'Company', 'Ticket_Class', 'Departure_Time', 'Departure_Location', 'Arrival_Time', 'Arrival_Location']
    

    def convert_duration_to_hours(duration_str):
    # Extract hours and minutes from the string
        hours = 0
        minutes = 0
        
        if 'h' in duration_str:
            hours_part = duration_str.split('h')[0].strip()
            hours = int(hours_part)
            duration_str = duration_str.split('h')[1].strip()
        if 'm' in duration_str:
            minutes_part = duration_str.split('m')[0].strip()
            minutes = int(minutes_part)
        total_hours = hours + (minutes / 60.0)   
        return total_hours
        
    with open('04 ML and EDA/models/no_stops_ordinal_encoder.pkl', 'rb') as file:
        no_stops_odinal_encoder = pickle.load(file)
    with open('04 ML and EDA/models/ticket_ordinal_encoder.pkl', 'rb') as file:
        ticket_class_odinal_encoder = pickle.load(file)
    with open('04 ML and EDA/models/arrival_label_encoder.pkl', 'rb') as file:
        dept_loc_label_encoder = pickle.load(file)
    with open('04 ML and EDA/models/departure_label_encoder.pkl', 'rb') as file:
        arri_loc_label_encoder = pickle.load(file)
    with open('04 ML and EDA/models/departure_time_label_encoder.pkl', 'rb') as file:
        dept_time_label_encoder = pickle.load(file)
    with open('04 ML and EDA/models/minmax_scaler.pkl', 'rb') as file:
        minmax_scaler = pickle.load(file)
    with open('04 ML and EDA/models/RF_regressor.pkl', 'rb') as file:
        rf_regressor = pickle.load(file)


    Value_list = list(request.form.values())
    
    Duration = convert_duration_to_hours(Value_list[2]) # 1


    Total_Stops= no_stops_odinal_encoder.transform(np.array(Value_list[3]).reshape(-1, 1))[0][0] # 2
    Ticket_Class=  ticket_class_odinal_encoder.transform(np.array(Value_list[5]).reshape(-1, 1))[0][0] # 3
    

    Departure_Time =   Value_list[6]
    print(Departure_Time)

    Departure_Location = dept_loc_label_encoder.transform(np.array(Value_list[7]).reshape(-1, 1))[0] #4  
    Arrival_Location = arri_loc_label_encoder.transform(np.array(Value_list[9]).reshape(-1, 1))[0]   #5
    print(Departure_Location)
    print(Arrival_Location)

    DaysTillJourney = (datetime.strptime(Value_list[1], '%Y-%m-%d') - datetime.strptime(Value_list[0], '%Y-%m-%d') ).days #6

    
    def categorize_time_of_day(datetime):
        hour = datetime.hour
        if 0 <= hour < 6:
            return 'Early Morning'
        elif 6 <= hour < 12:
            return 'Morning'
        elif 12 <= hour < 18:
            return 'Mid Day'
        else:
            return 'Night'

    # Apply the function to the DateTime column
    TimeOfDeparture = dept_time_label_encoder.transform([categorize_time_of_day(datetime.strptime(Value_list[6],'%H:%M'))])

    Company = ""
    comp_list= ['Company_Air India ', 'Company_AirAsia ', 'Company_AkasaAir ','Company_AllianceAir ', 'Company_GO FIRST ', 'Company_Indigo ','Company_Missing', 'Company_SpiceJet ', 'Company_StarAir ','Company_Vistara ']
    comp_ohe = [0.0]*len(comp_list)

    if(Value_list[4]=='Missing'):
        Company = 'Company_Missing'
        comp_ohe[6]=1.0
    else:
        Company = 'Company_'+Value_list[4]+' '
    print(Company)
    for i in range(len(comp_list)):
        if comp_list[i]==Company:
            comp_ohe[i]=1.0
            break
    
    ans_list= [Duration,Total_Stops,Ticket_Class,Departure_Location,Arrival_Location,DaysTillJourney]+[comp_ohe,TimeOfDeparture]
   
    flattened_data = []

    for item in ans_list:
        if isinstance(item, list):
            flattened_data.extend(item)
        elif isinstance(item, np.ndarray):
            flattened_data.extend(item.flatten())
        else:
            flattened_data.append(item)

    print("Flattened 1D list:", flattened_data)
    X = minmax_scaler.transform(np.array(flattened_data).reshape(1, -1))
    y = rf_regressor.predict(X)[0]

    return render_template("index",prediction_price="Approximate Price for Trip will be Rs.{}".format(y))
                    

if __name__ == "__main__" :
    app.run(debug=True)
