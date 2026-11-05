import fastf1
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
os.makedirs("cache_dir", exist_ok=True)
fastf1.Cache.enable_cache('cache_dir')

def main():
  print("Welcome to f1 lap comparsion, here you'll be able to analyse two different laps from an f1 session and understand it's differences")
  event1, event2, year1, year2 = get_info()
  telemetry1, telemetry2, full_name1, full_name2, session_ident_1, session_ident_2, lap1_time, lap2_time = get_data(event1, event2, year1, year2)
  distance =compare_laps(telemetry1, telemetry2, full_name1, full_name2, session_ident_1, session_ident_2, lap1_time, lap2_time, year1, year2)
  


def get_info():
     
     while True:
      a = input("Do you wish to analyze two laps from the same event? (y/n) ").strip().lower()
      if a == "y":
       
        while True:
          try:
           year1 = input("In which year did that event take place (the fastf1 module only contains data from 2018 onwards so make sure to input a valid year) ").strip()
           year2 = year1
           

           if year1.isnumeric() and int(year1) >= 2018:
               calendar = fastf1.get_event_schedule(int(year1))
               event_names = calendar['EventName'].str.lower().values
               locations = calendar['Location'].str.lower().values
               countries = calendar['Country'].str.lower().values
               while True:
                   circuit = input("Please input the circuit in which the laps were made: " ).strip().lower()

                   if circuit in event_names or circuit in locations or circuit in countries:
                       return fastf1.get_event(int(year1), circuit), fastf1.get_event(int(year1), circuit), year1, year2
                   
                   else:
                       print("Invalid circuit name, please try again.")
                       continue
           else:
                print("Invalid year, try again.")
                continue
           
          except ValueError:
            print("Invalid input, please input an integer")
          

      elif a == "n":
         
         while True:
            try:
                year1 = input("In which year did the first lap take place? (the fastf1 module only contains data from 2018 onwards so make sure to input a valid year) ").strip()
                year2 = input("In which year did the second lap take place? (the fastf1 module only contains data from 2018 onwards so make sure to input a valid year) ").strip()
               
                if year1.isnumeric() and int(year1) >= 2018 and year2.isnumeric() and int(year2) >= 2018:
                    calendar1 = fastf1.get_event_schedule(int(year1))
                    event_names1 = calendar1['EventName'].str.lower().values
                    locations1 = calendar1['Location'].str.lower().values
                    countries1 = calendar1['Country'].str.lower().values
                    calendar2 = fastf1.get_event_schedule(int(year2))
                    event_names2 = calendar2['EventName'].str.lower().values
                    locations2 = calendar2['Location'].str.lower().values
                    countries2 = calendar2['Country'].str.lower().values
                    while True:
                        circuit = input("Please input the circuit in the laps were made: " ).strip().lower()
                        if (circuit in event_names1 or circuit in locations1 or circuit in countries1) and (circuit in event_names2 or circuit in locations2 or circuit in countries2):
                            return fastf1.get_event(int(year1), circuit), fastf1.get_event(int(year2), circuit), year1, year2
                        
                        else:
                            print("Invalid circuit name(s), please try again.")
                            continue
                else:
                    print("Invalid year(s), try again.")
                    continue

            except ValueError:
                print("Invalid input, please input an integer")
            

      else:
         print("Invalid input, please enter 'y' or 'n'.")
         continue

def get_data(event1, event2, year1, year2):
   while True:
          
          
      
          session_identifiers = ['FP1', 'FP2', 'FP3', 'Q', 'S', 'SS', 'SQ', 'R']
          try: 
              session_ident_1, session_ident_2 = input("In what sessions did the laps take place? Your input should be in the from of 'session1 session2' ").upper().strip().split(" ")
          except ValueError:
              print("Invalid input, please input two session names separated by a space.")
              continue
          if session_ident_1 in session_identifiers and session_ident_2 in session_identifiers:
              session1 = event1.get_session(session_ident_1)
              session2 = event2.get_session(session_ident_2)
              break
    
          else:
              print("Invalid input, please input a valid session name.")
              continue
          
   # Telemetry is accessed below through Lap.get_telemetry(); request it explicitly.
   session1.load(telemetry=True, laps = True)
   session2.load(telemetry=True, laps = True)

   if year1 == year2:
    while True:
        
       
        driver1 = input("Please input the name of the driver that made first lap: (e.g. 'VER' for Max Verstappen) ").strip().upper()
       
        if driver1 in session1.results['Abbreviation'].values:
           lap1 = session1.laps.pick_drivers(driver1).pick_fastest()
           
           break
       
        else:
           print("Invalid input, please input a valid abbreviation (first three letters of the driver's last name).")
           continue
       
    while True:
       driver2 = input("Please input the name of the driver that made second lap: (e.g. 'VER' for Max Verstappen) ").strip().upper()
       
       if driver2 in session2.results['Abbreviation'].values:
           lap2 = session2.laps.pick_drivers(driver2).pick_fastest()
           break
       
       else:
           print("Invalid input, please input a valid abbreviation (first three letters of the driver's last name).")
           continue

   else:
        
        if input("Were both laps made by the same driver? (y/n) ").strip().lower() == "y":
            while True:
                driver1 = input("Please input the name of the driver that made both laps: (e.g. 'VER' for Max Verstappen) ").strip().upper()
                driver2 = driver1
                if driver1 in session1.results['Abbreviation'].values and driver1 in session2.results['Abbreviation'].values:
                    lap1 = session1.laps.pick_drivers(driver1).pick_fastest()
                    lap2 = session2.laps.pick_drivers(driver1).pick_fastest()
                    break
                else:
                    print("Invalid input, please input a valid abbreviation (first three letters of the driver's last name).")
                    continue

        else:
            while True:
                driver1 = input("Please input the name of the driver that made first lap: (e.g. 'VER' for Max Verstappen) ").strip().upper()
                if driver1 in session1.results['Abbreviation'].values:
                    lap1 = session1.laps.pick_drivers(driver1).pick_fastest()
                    break
                else:
                    print("Invalid input, please input a valid abbreviation (first three letters of the driver's last name).")
                    continue

            while True:
                driver2 = input("Please input the name of the driver that made second lap: (e.g. 'VER' for Max Verstappen) ").strip().upper()
                if driver2 in session2.results['Abbreviation'].values:
                    lap2 = session2.laps.pick_drivers(driver2).pick_fastest()
                    break
                else:
                    print("Invalid input, please input a valid abbreviation (first three letters of the driver's last name).")
                    continue
       
   full_name1 = session1.results.loc[session1.results['Abbreviation'] == driver1, 'FullName'].iloc[0]
   full_name2 = session2.results.loc[session2.results['Abbreviation'] == driver2, 'FullName'].iloc[0]

   telemetry1 = lap1.get_telemetry()
   telemetry2 = lap2.get_telemetry()

   

   lap1_time = lap1['LapTime']
   lap2_time = lap2['LapTime']
   return telemetry1, telemetry2, full_name1, full_name2, session_ident_1, session_ident_2, lap1_time, lap2_time

def compare_laps(telemetry1, telemetry2, full_name1, full_name2, session_ident1, session_ident2, lap1_time, lap2_time, year1, year2):
    sessions = {"R": "Race", "Q": "Qualifying", "FP1": "Free Practice 1", "FP2": "Free Practice 2", "FP3": "Free Practice 3", "S": "Sprint", "SS": "Sprint Shootout", "SQ": "Sprint Qualifying"}

    # Create a distance scale to compare both laps. The scale will be the minimum distance of both laps, with a step of 1 meter. This allows us to compare both laps at the same distance points, even if they have different lengths.
    distance = np.arange(0, min(telemetry1['Distance'].max(), telemetry2['Distance'].max()), 1)

    # Store the speed of both laps at each distance point in array above.
    v1 = np.interp(distance, telemetry1['Distance'], telemetry1['Speed'])
    v2 = np.interp(distance, telemetry2['Distance'], telemetry2['Speed'])

    # Store the throttle inputs of both driver of both laps at each distance point inarray above.
    throttle1 = np.interp(distance, telemetry1["Distance"], telemetry1["Throttle"])
    throttle2 = np.interp(distance, telemetry2["Distance"], telemetry2["Throttle"])

    # Store the throttle inputs of both driver of both laps at each distance point inarray above.
    brake1 = np.interp(distance, telemetry1["Distance"], telemetry1["Brake"])
    brake2 = np.interp(distance, telemetry2["Distance"], telemetry2["Brake"])

    # Calculate the difference in speed between both laps at each distance point. A positive value means that lap 1 is faster than lap 2, and a negative value means that lap 2 is faster than lap 1.
    delta_v = v1 - v2
    ref = 7.5
    data = pd.DataFrame({'Distance' : distance, 'Delta_Speed' : delta_v})
    
    # Create a new column in the dataframe which contains all the intervals where the speed diference beetween both laps is significant.
    data["Significant_Delta_Speed"] = (data["Delta_Speed"].abs() >= ref)
    data["Intervals"] = (
        (data["Significant_Delta_Speed"] != data["Significant_Delta_Speed"].shift())
        | (np.sign(data["Delta_Speed"]) != np.sign(data["Delta_Speed"].shift()))
    ).cumsum()
    intervals = data[data["Significant_Delta_Speed"]].groupby("Intervals").agg(Start = ("Distance", "min"), End = ("Distance", "max"), Delta_Speed_Mean = ("Delta_Speed", "mean"), Delta_Speed_Max = ("Delta_Speed", lambda x: x.abs().max()))

    # Calculate delta t beetween both laps at each point in the distance scale.
    time1 = np.interp(distance, telemetry1["Distance"], telemetry1["Time"].dt.total_seconds())
    time2 = np.interp(distance, telemetry2["Distance"], telemetry2["Time"].dt.total_seconds())  
    delta_t = time1 - time2

    # Estimating the cause of time loss
    significant_points_throttle1, significant_points_throttle2, significant_points_brake1, significant_points_brake2 = find_input_cause(intervals, distance, throttle1, throttle2, brake1, brake2, full_name1, full_name2)

    lap1_seconds = lap1_time.total_seconds()
    lap2_seconds = lap2_time.total_seconds()
    
    print(f"Lap {full_name1} {sessions[session_ident1]} vs Lap {full_name2} {sessions[session_ident2]}")
    if lap1_time < lap2_time:
        print(f"Lap of {full_name1} in {sessions[session_ident1]} {year1} was faster than Lap {full_name2} in {sessions[session_ident2]} {year2} by {(lap2_seconds - lap1_seconds):.3f} seconds")
    elif lap1_time > lap2_time:
        print(f"Lap of {full_name2} in {sessions[session_ident2]} {year2} was faster than Lap {full_name1} in {sessions[session_ident1]} {year1} by {(lap1_seconds - lap2_seconds):.3f} seconds")
    else:
        print(f"{full_name1} and {full_name2} posted an identical lap time of {lap1_time}")

    print(f"Negative time delta on the graphs means that {full_name1} in {sessions[session_ident1]} {year1} was faster than {full_name2} in {sessions[session_ident2]} {year2}, and positive time delta means the opposite.")
    #Speed graph
    plot_comparsion(distance, delta_t, v1, v2,full_name1, full_name2, "Speed (km/h)", "Speed comparsion", session_ident1, session_ident2, sessions, intervals, year1, year2, significant_points_throttle1 = None, significant_points_throttle2 = None, significant_points_brake1 = None, significant_points_brake2 = None)

    #Throttle input graph
    plot_comparsion(distance, delta_t, throttle1, throttle2,full_name1, full_name2, "Throttle input (%)", "Throttle input comparsion", session_ident1, session_ident2, sessions, intervals, year1, year2, significant_points_throttle1, significant_points_throttle2, significant_points_brake1, significant_points_brake2)

    #Brake input graph
    plot_comparsion(distance, delta_t, brake1, brake2,full_name1, full_name2, "Brake input (0-1)", "Brake input comparsion", session_ident1, session_ident2, sessions, intervals, year1, year2, significant_points_throttle1, significant_points_throttle2, significant_points_brake1, significant_points_brake2)

def convert_laptime(laptime):
    # Convert laptime from seconds to a string in the format of "minutes:seconds.milliseconds"
    minutes = int(laptime // 60)
    seconds = int(laptime % 60)
    milliseconds = int((laptime - minutes * 60 - seconds) * 1000)
    return f"{minutes}:{seconds:02d}.{milliseconds:03d}"

# Estimating the cause of time loss
def find_input_cause(intervals, distance, throttle1, throttle2, brake1, brake2, full_name1, full_name2, throttle_ref = 10, brake_ref = 0.1):

   
    significant_points_throttle1 = []
    significant_points_throttle2 = []
    significant_points_brake1 = []
    significant_points_brake2 = []
    found_cause = False

    for _, interval in intervals.iterrows():

        for i in range(int(interval["Start"]), -1, -1):
            delta_brake = brake1[i] - brake2[i]
            delta_throttle = throttle1[i] - throttle2[i]
            

            if abs(delta_brake) >= brake_ref:
                
                # Driver 2 braked later than driver 1, being therefore faster.
                if delta_brake > 0:
                    significant_points_brake2.append(distance[i])


                # Driver 1 braked later than driver 2, being therefore faster.
                else:
                    significant_points_brake1.append(distance[i])

                found_cause = True
                break

            if abs(delta_throttle) >= throttle_ref:
                

                if delta_throttle > 0:
                    significant_points_throttle1.append(distance[i])                  

                else:
                    significant_points_throttle2.append(distance[i])

                found_cause = True
                break

    return significant_points_throttle1, significant_points_throttle2, significant_points_brake1, significant_points_brake2


def plot_comparsion(distance, delta_t, signal1, signal2, full_name1, full_name2, signal_label, title, session_indent1, session_indent2, sessions, intervals, year1, year2, significant_points_throttle1 = None, significant_points_throttle2 = None, significant_points_brake1 = None, significant_points_brake2 = None):
    # Generalising each graph to create
    
    fig,  ax_signal = plt.subplots(figsize=(12,6))
    ax_delta = ax_signal.twinx()
    labels = set()
    shaded_areas = []
    shaded_labels = []
    for _ , interval in intervals.iterrows():
            if interval["Delta_Speed_Mean"] > 0:
                color = "green"
                label = f"{full_name1} in {sessions[session_indent1].capitalize()} {year1} was faster than {full_name2} in {sessions[session_indent2].capitalize()} {year2}"
            else:
                color = "yellow"
                label = f"{full_name2} in {sessions[session_indent2].capitalize()} {year2} was faster than {full_name1} in {sessions[session_indent1].capitalize()} {year1}"

            if label in labels:
                label = "_nolegend_"
            else:
                labels.add(label)

            shaded_area = ax_signal.axvspan(xmin=interval["Start"],xmax=interval["End"],color=color,alpha=0.3,label=label)
            if label != "_nolegend_":
                shaded_areas.append(shaded_area)
                shaded_labels.append(label)

    line1, = ax_signal.plot(distance, signal1, label = f"{full_name1} in {sessions[session_indent1]} {year1}", color = "blue")
    line2, = ax_signal.plot(distance, signal2, label = f"{full_name2} in {sessions[session_indent2]} {year2}", color = "red")

    #Marking significant points of throttle and brake inputs on the graph, if they exist.
    inputs_legend = []
    signal_type = signal_label.casefold()

    if "throttle" in signal_type:
        point_groups = [(significant_points_throttle1, "green", f"{full_name1} in {sessions[session_indent1]} {year1} accelerated more than {full_name2} in {sessions[session_indent2]} {year2}"),(significant_points_throttle2, "orange", f"{full_name2} in {sessions[session_indent2]} {year2} accelerated more than {full_name1} in {sessions[session_indent1]} {year1}")]

    elif "brake" in signal_type:
        point_groups = [(significant_points_brake1, "green", f"{full_name1} in {sessions[session_indent1]} {year1} braked less than {full_name2} in {sessions[session_indent2]} {year2}"),(significant_points_brake2, "orange", f"{full_name2} in {sessions[session_indent2]} {year2} braked less than {full_name1} in {sessions[session_indent1]} {year1}"),]

    else:
        point_groups = []

    for points, color, driver_legend  in point_groups:
        if points is None or len(points) == 0:
            continue

        first_line = None

        for point in points:
            line = ax_signal.axvline(x=point, color=color, linestyle = ":", label = driver_legend)

            if first_line is None:
                first_line = line

        inputs_legend.append(first_line)

    # Defining the color of 'line_delta' based on which driver is ahead.
    red_delta = np.where(delta_t > 0, delta_t, np.nan)
    blue_delta = np.where(delta_t < 0, delta_t, np.nan)

    line_delta, = ax_delta.plot(distance, red_delta, label=f"Time delta between {full_name1} in {sessions[session_indent1]} {year1} and {full_name2} in {sessions[session_indent2]} {year2}",color="red",linestyle="--",)
    ax_delta.plot(distance,blue_delta,color="blue",linestyle="--",label="_nolegend_",)
   
    ax_signal.set_xlabel("Distance (m)")
    ax_signal.set_ylabel(signal_label)
    ax_delta.set_ylabel("Delta t (s)")
    ax_delta.set_ylim(-3.5,3.5)
    ax_delta.axhline(0, color = "gray", linestyle = ":")
    ax_signal.set_title(title)
    ax_signal.grid(True)
    visuals = [line1, line2, line_delta, *shaded_areas, *inputs_legend]
    legend_labels = [line1.get_label(), line2.get_label(), line_delta.get_label(), *shaded_labels, *[line.get_label() for line in inputs_legend]]
    ax_signal.legend(visuals, legend_labels)
    fig.tight_layout()
    plt.show()
    

if __name__ == "__main__":
    main()
