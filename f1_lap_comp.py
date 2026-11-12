import fastf1
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
os.makedirs("cache_dir", exist_ok=True)
fastf1.Cache.enable_cache('cache_dir')

def main():
  print("Welcome to the F1 lap comparison tool. Here, you can analyze two laps from an F1 session and understand their differences.")
  event1, event2, year1, year2 = get_info()
  telemetry1, telemetry2, lap1_label, lap2_label, lap1_time, lap2_time = get_data(event1, event2, year1, year2)
  compare_laps(telemetry1, telemetry2, lap1_label, lap2_label, lap1_time, lap2_time)
  


def get_info():
     
     while True:
      a = input("Do you want to analyze two laps from the same event? (y/n) ").strip().lower()
      if a == "y":
       
        while True:
          try:
           year1 = input("In which year did the event take place? FastF1 data is available from 2018 onward. ").strip()
           year2 = year1
           

           if year1.isnumeric() and int(year1) >= 2018:
               calendar = fastf1.get_event_schedule(int(year1))
               event_names = calendar['EventName'].str.lower().values
               locations = calendar['Location'].str.lower().values
               countries = calendar['Country'].str.lower().values
               while True:
                   circuit = input("Enter the circuit or event name where the laps were set (avoid country names, as a country may host multiple Grands Prix): ").strip().lower()

                   if circuit in event_names or circuit in locations or circuit in countries:
                       return fastf1.get_event(int(year1), circuit), fastf1.get_event(int(year1), circuit), year1, year2
                   
                   else:
                       print("Invalid circuit or event name. Please try again.")
                       continue
           else:
                print("Invalid year. Please try again.")
                continue
           
          except ValueError:
            print("Invalid input. Please enter a year as a number.")
          

      elif a == "n":
         
         while True:
            try:
                year1 = input("In which year did the first lap take place? FastF1 data is available from 2018 onward. ").strip()
                year2 = input("In which year did the second lap take place? FastF1 data is available from 2018 onward. ").strip()
               
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
                        circuit = input("Enter the circuit or event name where the laps were set (avoid country names, as a country may host multiple Grands Prix): ").strip().lower()
                        if (circuit in event_names1 or circuit in locations1 or circuit in countries1) and (circuit in event_names2 or circuit in locations2 or circuit in countries2):
                            return fastf1.get_event(int(year1), circuit), fastf1.get_event(int(year2), circuit), year1, year2
                        
                        else:
                            print("Invalid circuit or event name. Please try again.")
                            continue
                else:
                    print("Invalid year or years. Please try again.")
                    continue

            except ValueError:
                print("Invalid input. Please enter a year as a number.")
            

      else:
         print("Invalid input. Please enter 'y' or 'n'.")
         continue

def _session_context(session, session_code, year):
    event_name = str(session.event["EventName"])
    session_name = {
        "R": "Race", "Q": "Qualifying", "FP1": "Free Practice 1",
        "FP2": "Free Practice 2", "FP3": "Free Practice 3",
        "S": "Sprint", "SS": "Sprint Shootout", "SQ": "Sprint Qualifying",
    }[session_code]
    return f"{event_name} {year}, {session_name}"


def _driver_full_name(session, driver):
    names = session.results.loc[
        session.results["Abbreviation"].astype(str).str.upper() == driver,
        "FullName",
    ]
    return str(names.iloc[0]) if not names.empty else driver


def _lap_label(session, lap, driver, session_code, year, is_fastest=False, qualifying_segment=None):
    driver_name = _driver_full_name(session, driver)
    context = _session_context(session, session_code, year)
    segment = lap.get("Q")
    if session_code in ("Q", "SQ"):
        label_segment = qualifying_segment if is_fastest else segment
        if label_segment is not None and pd.notna(label_segment):
            context += f" Q{int(label_segment)}"
        lap_description = "fastest lap" if is_fastest else f"selected lap ({lap['LapTime']})"
        return f"{driver_name} | {context} | {lap_description}"

    if session_code in ("FP1", "FP2", "FP3"):
        lap_description = (
            f"fastest {session_code}"
            if is_fastest
            else f"selected {session_code} lap ({lap['LapTime']})"
        )
        return f"{driver_name} | {context} | {lap_description}"

    lap_number = int(lap["LapNumber"])
    lap_description = f"Lap {lap_number} (fastest)" if is_fastest else f"Lap {lap_number}"
    return f"{driver_name} | {context} | {lap_description}"


def _select_lap(session, driver, session_code, year, comparison_label=None):
    laps = session.laps.pick_drivers(driver)
    driver_name = _driver_full_name(session, driver)
    context = _session_context(session, session_code, year)
    comparison_context = f" Compare with {comparison_label}." if comparison_label else ""
    selected_segment = None

    if session_code in ("Q", "SQ") and "Q" in laps.columns:
        available = sorted(laps["Q"].dropna().unique(), key=lambda value: int(value))
        if available:
            print(f"Available qualifying segments for {driver_name} in {context}: " + ", ".join(f"Q{int(value)}" for value in available))
            while True:
                choice = input(f"Analyze all of {context} for {driver_name}, or choose one segment (Q1, Q2, etc.)? Enter ALL or a segment.{comparison_context} ").strip().upper()
                if choice in ("ALL", "A"):
                    break
                if choice.startswith("Q"):
                    choice = choice[1:]
                try:
                    segment = int(choice)
                except ValueError:
                    segment = None
                if segment in [int(value) for value in available]:
                    laps = laps[laps["Q"] == segment]
                    selected_segment = segment
                    context += f" (Q{segment})"
                    break
                print("Enter ALL or choose one of the available qualifying segments.")

    valid_laps = laps[laps["LapTime"].notna()]
    if valid_laps.empty:
        raise ValueError(f"{driver_name} has no valid laps in {context} with the selected options.")

    fastest = valid_laps.pick_fastest()
    fastest_label = _lap_label(
        session, fastest, driver, session_code, year,
        is_fastest=True, qualifying_segment=selected_segment,
    )
    while True:
        choice = input(
            f"Use this lap: {fastest_label}?{comparison_context} (y/n) "
        ).strip().lower()
        if choice in ("y", "n"):
            break
        print("Enter 'y' or 'n'.")
    if choice == "y":
        return fastest, True, selected_segment

    sorted_laps = valid_laps.sort_values("LapNumber")
    uses_option_numbers = session_code in ("Q", "SQ", "FP1", "FP2", "FP3")
    if uses_option_numbers:
        print(f"Available laps for {driver_name} in {context}.{comparison_context}")
        for option, (_, available_lap) in enumerate(sorted_laps.iterrows(), start=1):
            segment = available_lap.get("Q")
            segment_label = f" (Q{int(segment)})" if session_code in ("Q", "SQ") and pd.notna(segment) else ""
            print(f"  Option {option}{segment_label}: {available_lap['LapTime']}")
    else:
        available_numbers = sorted(valid_laps["LapNumber"].dropna().astype(int).unique())
        if not available_numbers:
            raise ValueError(f"{driver_name} has valid lap times but no lap numbers in {context}.")
        first_lap_number = available_numbers[0]
        last_lap_number = available_numbers[-1]
        print(
            f"Available lap numbers for {driver_name} in {context}: "
            f"{first_lap_number} to {last_lap_number}.{comparison_context}"
        )
    while True:
        try:
            if uses_option_numbers:
                selected = int(input(f"Choose an option number from the list.{comparison_context} ").strip())
                if 1 <= selected <= len(sorted_laps):
                    selected_lap = sorted_laps.iloc[[selected - 1]]
                    return selected_lap.iloc[0], selected_lap.iloc[0]["LapTime"] == fastest["LapTime"], selected_segment
            else:
                selected = int(input(f"Choose a lap number from {first_lap_number} to {last_lap_number}.{comparison_context} ").strip())
                selected_lap = valid_laps[valid_laps["LapNumber"] == selected]
                if not selected_lap.empty:
                    return selected_lap.iloc[0], selected_lap.iloc[0]["LapTime"] == fastest["LapTime"], selected_segment
        except ValueError:
            pass
        if uses_option_numbers:
            print(f"That option is not available. Choose one from the list above.{comparison_context}")
        else:
            print(f"That lap number is not available. Choose a number from {first_lap_number} to {last_lap_number}.{comparison_context}")


def get_data(event1, event2, year1, year2):
    session_identifiers = ['FP1', 'FP2', 'FP3', 'Q', 'S', 'SS', 'SQ', 'R']
    event_context1 = f"{event1['EventName']} {year1}"
    event_context2 = f"{event2['EventName']} {year2}"
    while True:
        try:
            session_ident_1, session_ident_2 = input(
                f"Enter the two session codes, in order, for {event_context1} and {event_context2} (for example, 'Q R'): "
            ).upper().split()
        except ValueError:
            print("Invalid input. Enter exactly two session codes separated by a space.")
            continue
        if session_ident_1 in session_identifiers and session_ident_2 in session_identifiers:
            session1 = event1.get_session(session_ident_1)
            session2 = event2.get_session(session_ident_2)
            break
        print(f"Invalid session codes. Enter valid codes for {event_context1} and {event_context2}.")

    session1.load(telemetry=True, laps=True)
    session2.load(telemetry=True, laps=True)

    context1 = _session_context(session1, session_ident_1, year1)
    context2 = _session_context(session2, session_ident_2, year2)
    same_driver = input(f"Were both laps set by the same driver ({context1} and {context2})? (y/n) ").strip().lower()
    while same_driver not in ("y", "n"):
        same_driver = input("Please enter 'y' or 'n': ").strip().lower()

    def choose_driver(session, prompt):
        valid = session.results['Abbreviation'].dropna().astype(str).str.upper().tolist()
        while True:
            driver = input(prompt).strip().upper()
            if driver in valid:
                return driver
            print("Invalid driver abbreviation. Please try again.")

    if same_driver == "y":
        while True:
            driver1 = choose_driver(session1, f"Enter the driver's abbreviation for both laps ({context1} and {context2}): ")
            session2_drivers = session2.results["Abbreviation"].dropna().astype(str).str.upper().tolist()
            if driver1 in session2_drivers:
                driver2 = driver1
                break
            print("That driver is not present in both sessions. Please try again.")
    else:
        driver1 = choose_driver(session1, f"Enter the abbreviation of the driver for the first lap ({context1}): ")
        driver2 = choose_driver(session2, f"Enter the abbreviation of the driver for the second lap ({context2}): ")

    while True:
        try:
            lap1, lap1_is_fastest, lap1_segment = _select_lap(session1, driver1, session_ident_1, year1)
            lap1_label = _lap_label(session1, lap1, driver1, session_ident_1, year1, lap1_is_fastest, lap1_segment)
            print(f"First lap selected: {lap1_label}")
            break
        except ValueError as error:
            print(error)
            driver1 = choose_driver(session1, f"Enter another driver abbreviation for the first lap ({context1}): ")
    print(f"Select the second lap to compare with {lap1_label}.")
    while True:
        try:
            lap2, lap2_is_fastest, lap2_segment = _select_lap(session2, driver2, session_ident_2, year2, comparison_label=lap1_label)
            lap2_label = _lap_label(session2, lap2, driver2, session_ident_2, year2, lap2_is_fastest, lap2_segment)
            print(f"Second lap selected: {lap2_label}")
            break
        except ValueError as error:
            print(error)
            driver2 = choose_driver(session2, f"Enter another driver abbreviation for the second lap ({context2}): ")

    telemetry1 = lap1.get_telemetry()
    telemetry2 = lap2.get_telemetry()
    return telemetry1, telemetry2, lap1_label, lap2_label, lap1["LapTime"], lap2["LapTime"]

def compare_laps(telemetry1, telemetry2, lap1_label, lap2_label, lap1_time, lap2_time):
    # Create a distance scale in 1-meter increments, limited to the shorter lap.
    d1 = telemetry1["Distance"].to_numpy(dtype=float)
    d2 = telemetry2["Distance"].to_numpy(dtype=float)

    d1 = d1 - d1[0]
    d2 = d2 - d2[0]

    finish_distance = min(d1[-1], d2[-1])
    distance = np.arange(0, finish_distance, 1.0)

    idx1 = np.argsort(d1)
    idx2 = np.argsort(d2)

    d1, unique1 = np.unique(d1[idx1], return_index=True)
    d2, unique2 = np.unique(d2[idx2], return_index=True)

    # Interpolate both laps' telemetry onto the shared distance scale.
    def interp_by_distance(values, idx, unique_idx, d):
        y = np.asarray(values, dtype=float)[idx][unique_idx]
        return np.interp(distance, d, y)

    # Store each lap's speed at every point on the distance scale.
    v1 = interp_by_distance(telemetry1['Speed'], idx1, unique1, d1)
    v2 = interp_by_distance(telemetry2['Speed'], idx2, unique2, d2)

    # Store each driver's throttle input at every point on the distance scale.
    throttle1 = interp_by_distance(telemetry1["Throttle"], idx1, unique1, d1)
    throttle2 = interp_by_distance(telemetry2["Throttle"], idx2, unique2, d2)

    # Store each driver's brake input at every point on the distance scale.
    brake1 = interp_by_distance(telemetry1["Brake"], idx1, unique1, d1)
    brake2 = interp_by_distance(telemetry2["Brake"], idx2, unique2, d2)

    # Positive speed differences mean lap 1 is faster; negative differences mean lap 2 is faster.
    delta_v = v1 - v2
    ref = 7.5
    data = pd.DataFrame({'Distance' : distance, 'Delta_Speed' : delta_v})

    # Mark intervals where the speed difference between the laps is significant.
    data["Significant_Delta_Speed"] = (data["Delta_Speed"].abs() >= ref)
    data["Intervals"] = (
        (data["Significant_Delta_Speed"] != data["Significant_Delta_Speed"].shift())
        | (np.sign(data["Delta_Speed"]) != np.sign(data["Delta_Speed"].shift()))
    ).cumsum()
    intervals = data[data["Significant_Delta_Speed"]].groupby("Intervals").agg(Start = ("Distance", "min"), End = ("Distance", "max"), Delta_Speed_Mean = ("Delta_Speed", "mean"))

    # Calculate the time delta between the laps at each point on the distance scale.
    t1 = (telemetry1["Time"] - telemetry1["Time"].iloc[0]).dt.total_seconds().to_numpy()
    t2 = (telemetry2["Time"] - telemetry2["Time"].iloc[0]).dt.total_seconds().to_numpy()
    time1 = interp_by_distance(t1, idx1, unique1, d1)
    time2 = interp_by_distance(t2, idx2, unique2, d2)
    delta_t = time1 - time2

    # Estimate the cause of time loss.
    significant_points_throttle1, significant_points_throttle2, significant_points_brake1, significant_points_brake2 = find_input_cause(intervals, distance, throttle1, throttle2, brake1, brake2)

    lap1_seconds = lap1_time.total_seconds()
    lap2_seconds = lap2_time.total_seconds()
    
    print(f"Comparing {lap1_label} with {lap2_label}.")
    if lap1_time < lap2_time:
        print(f"{lap1_label} was faster by {(lap2_seconds - lap1_seconds):.3f} seconds.")
    elif lap1_time > lap2_time:
        print(f"{lap2_label} was faster by {(lap1_seconds - lap2_seconds):.3f} seconds.")
    else:
        print(f"The selected laps have identical times: {lap1_time}.")

    print(f"A negative time delta means {lap1_label} was ahead; a positive time delta means {lap2_label} was ahead.")
    # Speed graph.
    plot_comparsion(distance, delta_t, v1, v2, lap1_label, lap2_label, "Speed (km/h)", "Speed comparison", intervals)

    # Throttle input graph.
    plot_comparsion(distance, delta_t, throttle1, throttle2, lap1_label, lap2_label, "Throttle input (%)", "Throttle input comparison", intervals, significant_points_throttle1, significant_points_throttle2, significant_points_brake1, significant_points_brake2)

    # Brake input graph.
    plot_comparsion(distance, delta_t, brake1, brake2, lap1_label, lap2_label, "Brake input (0-1)", "Brake input comparison", intervals, significant_points_throttle1, significant_points_throttle2, significant_points_brake1, significant_points_brake2)

# Estimate the cause of time loss.
def find_input_cause(intervals, distance, throttle1, throttle2, brake1, brake2, throttle_ref = 10, brake_ref = 0.1, persistence = 5):

    significant_points_throttle1 = []
    significant_points_throttle2 = []
    significant_points_brake1 = []
    significant_points_brake2 = []

    # Make sure there are intervals to analyze before proceeding.
    if len(distance) == 0:
        return significant_points_throttle1, significant_points_throttle2, significant_points_brake1, significant_points_brake2

    delta_throttle = np.asarray(throttle1) - np.asarray(throttle2)
    delta_brake = np.asarray(brake1) - np.asarray(brake2)
    # Define a minimum number of points to consider a significant difference, based on the persistence parameter.
    min_points = max (1, int(persistence))

    #Auxiliary function to find significant points in the input signals.
    def find_offset(difference, threshold, start):
        significant = np.abs(difference[:start + 1]) >= threshold
        i = start

        while i >= 0:
            if not significant[i]:
                i -= 1
                continue

            run_end = i

            while i >= 0 and significant[i]:
                i -= 1

            run_start = i + 1
            run_length = run_end - run_start + 1

            if run_length >= min_points:
                return run_start

        return None

    for _, interval in intervals.iterrows():
        start = min(len(distance) - 1, int(interval["Start"] - 1))

        if start < 0:
            continue

        brake_start = find_offset(delta_brake, brake_ref, start)
        throttle_start = find_offset(delta_throttle, throttle_ref, start)

        #Storing all significant points.
        candidates = []

        if brake_start is not None:
            candidates.append((brake_start, "brake"))

        if throttle_start is not None:
            candidates.append((throttle_start, "throttle"))

        if not candidates:
            continue

        index, input_type = max(candidates, key=lambda x: x[0])

        if input_type == "brake":
            if delta_brake[index] > 0:
                significant_points_brake1.append(distance[index])
            else:
                significant_points_brake2.append(distance[index])

        elif input_type == "throttle":
            if delta_throttle[index] > 0:
                significant_points_throttle1.append(distance[index])
            else:
                significant_points_throttle2.append(distance[index])

    return significant_points_throttle1, significant_points_throttle2, significant_points_brake1, significant_points_brake2


def plot_comparsion(distance, delta_t, signal1, signal2, lap1_label, lap2_label, signal_label, title, intervals, significant_points_throttle1 = None, significant_points_throttle2 = None, significant_points_brake1 = None, significant_points_brake2 = None):
    # Create a graph for each telemetry signal.
    
    fig,  ax_signal = plt.subplots(figsize=(12,6))
    ax_delta = ax_signal.twinx()
    labels = set()
    shaded_areas = []
    shaded_labels = []
    for _ , interval in intervals.iterrows():
            if interval["Delta_Speed_Mean"] > 0:
                color = "green"
                label = f"{lap1_label} was faster than {lap2_label}"
            else:
                color = "yellow"
                label = f"{lap2_label} was faster than {lap1_label}"

            if label in labels:
                label = "_nolegend_"
            else:
                labels.add(label)

            shaded_area = ax_signal.axvspan(xmin=interval["Start"],xmax=interval["End"],color=color,alpha=0.3,label=label)
            if label != "_nolegend_":
                shaded_areas.append(shaded_area)
                shaded_labels.append(label)

    line1, = ax_signal.plot(distance, signal1, label=lap1_label, color="blue")
    line2, = ax_signal.plot(distance, signal2, label=lap2_label, color="red")

    # Mark significant throttle and brake input points, when present.
    inputs_legend = []
    signal_type = signal_label.casefold()

    if "throttle" in signal_type:
        point_groups = [(significant_points_throttle1, "green", f"{lap1_label} used more throttle than {lap2_label}"),(significant_points_throttle2, "orange", f"{lap2_label} used more throttle than {lap1_label}")]

    elif "brake" in signal_type:
        point_groups = [(significant_points_brake1, "green", f"{lap1_label} applied more brake than {lap2_label}"),(significant_points_brake2, "orange", f"{lap2_label} applied more brake than {lap1_label}")]

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

    # Color the time delta according to which driver is ahead.
    red_delta = np.where(delta_t > 0, delta_t, np.nan)
    blue_delta = np.where(delta_t < 0, delta_t, np.nan)

    line_delta, = ax_delta.plot(distance, red_delta, label=f"Time delta: {lap1_label} vs {lap2_label}",color="red",linestyle="--",)
    ax_delta.plot(distance,blue_delta,color="blue",linestyle="--",label="_nolegend_",)
   
    ax_signal.set_xlabel("Distance (m)")
    ax_signal.set_ylabel(signal_label)
    ax_delta.set_ylabel("Delta t (s)")
    #ax_delta.set_ylim(-3.5,3.5)
    ax_delta.axhline(0, color = "gray", linestyle = ":")
    ax_signal.set_title(title)
    ax_signal.grid(True)
    visuals = [line1, line2, line_delta, *shaded_areas, *inputs_legend]
    legend_labels = [line1.get_label(), line2.get_label(), line_delta.get_label(), *shaded_labels, *[line.get_label() for line in inputs_legend]]
    fig.legend(visuals,legend_labels,loc="lower center",bbox_to_anchor=(0.5, 0.02),fontsize="medium",)
    fig.tight_layout(rect=(0, 0.32, 1, 1))
    plt.show()
    

if __name__ == "__main__":
    main()
