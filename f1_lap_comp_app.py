#Streamlit interface for the F1 lap comparison tool.

from __future__ import annotations

import os
from pathlib import Path

import fastf1
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

import f1_lap_comp as core


ROOT = Path(__file__).resolve().parent
CACHE_DIR = ROOT / "cache_dir"
os.makedirs(CACHE_DIR, exist_ok=True)
fastf1.Cache.enable_cache(str(CACHE_DIR))

SESSIONS = {
    "Practice 1": "FP1", "Practice 2": "FP2", "Practice 3": "FP3",
    "Qualifying": "Q", "Sprint": "S", "Sprint Shootout": "SS",
    "Sprint Qualifying": "SQ", "Race": "R",
}

st.set_page_config(page_title="F1 Lap Comparison", page_icon="🏎️", layout="wide")


@st.cache_data(show_spinner=False)
def get_schedule(year: int) -> pd.DataFrame:
    return fastf1.get_event_schedule(year, include_testing=False)


@st.cache_resource(show_spinner="Loading session and telemetry…")
def load_session(year: int, event_name: str, session_code: str):
    session = fastf1.get_session(year, event_name, session_code)
    session.load(telemetry=True, laps=True)
    return session


def session_picker(prefix: str, year: int, event_name: str, column):
    with column:
        st.subheader("Lap " + prefix)
        session_label = st.selectbox(f"Session ({prefix})", list(SESSIONS), key=f"{prefix}_session")
        return year, event_name, SESSIONS[session_label], session_label


def lap_picker(session, session_code: str, session_label: str, year: int, column, prefix: str):
    with column:
        drivers = session.results["Abbreviation"].dropna().astype(str).str.upper().drop_duplicates().tolist()
        if not drivers:
            st.warning("No drivers were found in this session.")
            return None, None
        driver = st.selectbox(f"Driver ({prefix})", drivers, key=f"{prefix}_driver")
        laps = session.laps.pick_drivers(driver)
        if session_code in ("Q", "SQ") and "Q" in laps.columns:
            segments = sorted(laps["Q"].dropna().unique(), key=int)
            if segments:
                segment_choices = ["All"] + [f"Q{int(q)}" for q in segments]
                segment = st.selectbox(f"Segmento ({prefix})", segment_choices, key=f"{prefix}_segment")
                if segment != "All":
                    laps = laps[laps["Q"] == int(segment[1:])]
        valid = laps[laps["LapTime"].notna()].copy()
        if valid.empty:
            st.warning(f"{driver} has no valid laps in this session/segment.")
            return None, None
        valid = valid.sort_values("LapNumber")
        fastest = valid["LapTime"].idxmin()
        labels = {}
        for idx, lap in valid.iterrows():
            lap_time = str(lap["LapTime"])
            q = lap.get("Q")
            q_text = f" · Q{int(q)}" if pd.notna(q) and session_code in ("Q", "SQ") else ""
            labels[idx] = f"Lap {int(lap['LapNumber'])}{q_text} · {lap_time}" + (" · fastest" if idx == fastest else "")
        selected = st.selectbox(f"Lap to compare ({prefix})", list(labels), index=list(labels).index(fastest), format_func=labels.get, key=f"{prefix}_lap")
        lap = valid.loc[selected]
        fullname = core._driver_full_name(session, driver)
        context = f"{session.event['EventName']} {year} · {session_label}"
        q = lap.get("Q")
        if session_code in ("Q", "SQ") and pd.notna(q):
            context += f" · Q{int(q)}"
        label = f"{fullname} · {context} · Lap {int(lap['LapNumber'])}"
        return lap.get_telemetry(), (label, lap["LapTime"])


def comparison_figures(telemetry1, telemetry2, label1, label2):
    d1 = telemetry1["Distance"].to_numpy(dtype=float)
    d2 = telemetry2["Distance"].to_numpy(dtype=float)
    d1, d2 = d1 - d1[0], d2 - d2[0]
    finish = min(d1[-1], d2[-1])
    distance = np.arange(0, finish, 1.0)
    idx1, idx2 = np.argsort(d1), np.argsort(d2)
    d1, u1 = np.unique(d1[idx1], return_index=True)
    d2, u2 = np.unique(d2[idx2], return_index=True)

    def interp(values, idx, unique, d):
        return np.interp(distance, d, np.asarray(values, dtype=float)[idx][unique])

    v1, v2 = interp(telemetry1["Speed"], idx1, u1, d1), interp(telemetry2["Speed"], idx2, u2, d2)
    t1 = (telemetry1["Time"] - telemetry1["Time"].iloc[0]).dt.total_seconds()
    t2 = (telemetry2["Time"] - telemetry2["Time"].iloc[0]).dt.total_seconds()
    delta_t = interp(t1, idx1, u1, d1) - interp(t2, idx2, u2, d2)
    throttle1, throttle2 = interp(telemetry1["Throttle"], idx1, u1, d1), interp(telemetry2["Throttle"], idx2, u2, d2)
    brake1, brake2 = interp(telemetry1["Brake"], idx1, u1, d1), interp(telemetry2["Brake"], idx2, u2, d2)

    delta_v = v1 - v2
    data = pd.DataFrame({"Distance": distance, "Delta_Speed": delta_v})
    data["Significant"] = data["Delta_Speed"].abs() >= 7.5
    data["Group"] = ((data["Significant"] != data["Significant"].shift()) | (np.sign(data["Delta_Speed"]) != np.sign(data["Delta_Speed"].shift()))).cumsum()
    intervals = data[data["Significant"]].groupby("Group").agg(Start=("Distance", "min"), End=("Distance", "max"), Mean=("Delta_Speed", "mean"))
    points = core.find_input_cause(intervals.rename(columns={"Mean": "Delta_Speed_Mean"}), distance, throttle1, throttle2, brake1, brake2)

    figures = []
    for signal1, signal2, ylabel, title, point_type in [
        (v1, v2, "Speed (km/h)", "Speed Comparison", None),
        (throttle1, throttle2, "Throttle (%)", "Throttle Comparison", "throttle"),
        (brake1, brake2, "Brake (0–1)", "Brake Comparison", "brake"),
    ]:
        fig, ax = plt.subplots(figsize=(12, 5))
        delta_ax = ax.twinx()
        for _, interval in intervals.iterrows():
            color = "green" if interval["Mean"] > 0 else "gold"
            ax.axvspan(interval["Start"], interval["End"], color=color, alpha=0.22)
        ax.plot(distance, signal1, color="blue", label=label1)
        ax.plot(distance, signal2, color="red", label=label2)
        delta_ax.plot(distance, np.where(delta_t > 0, delta_t, np.nan), "r--", label="Time delta")
        delta_ax.plot(distance, np.where(delta_t < 0, delta_t, np.nan), "b--")
        if point_type == "throttle":
            for pts, color in ((points[0], "green"), (points[1], "orange")):
                for point in pts:
                    ax.axvline(point, color=color, linestyle=":", alpha=.8)
        elif point_type == "brake":
            for pts, color in ((points[2], "green"), (points[3], "orange")):
                for point in pts:
                    ax.axvline(point, color=color, linestyle=":", alpha=.8)
        ax.set(xlabel="Distance (m)", ylabel=ylabel, title=title)
        delta_ax.set_ylabel("Time delta (s)")
        delta_ax.axhline(0, color="gray", linestyle=":")
        ax.grid(True, alpha=.25)
        lines = ax.get_lines() + delta_ax.get_lines()[:1]
        ax.legend(lines, [line.get_label() for line in lines], loc="upper right")
        fig.tight_layout()
        figures.append(fig)
    return figures


def main():
    st.title("🏎️ F1 Lap Comparison")
    st.caption("Compare telemetry from two laps across Formula 1 sessions.")
    left, right = st.columns(2)
    year1 = left.selectbox("Year (Lap 1)", range(2026, 2017, -1), key="1_year")
    year2 = right.selectbox("Year (Lap 2)", range(2026, 2017, -1), key="2_year")
    try:
        schedule1 = get_schedule(year1)
        schedule2 = get_schedule(year2)
        locations1 = set(schedule1["Location"].dropna())
        locations2 = set(schedule2["Location"].dropna())
        common_locations = sorted(locations1 & locations2)
    except Exception as exc:
        st.error(f"Could not load the event calendar: {exc}")
        return
    if not common_locations:
        st.error("No event is shared by the selected seasons. Choose different years.")
        return
    location = st.selectbox("Circuit (used for both laps)", common_locations, key="shared_event")
    event1 = schedule1.loc[schedule1["Location"] == location, "EventName"].iloc[0]
    event2 = schedule2.loc[schedule2["Location"] == location, "EventName"].iloc[0]
    config1 = session_picker("1", year1, event1, left)
    config2 = session_picker("2", year2, event2, right)
    if st.button("Load sessions", type="primary", use_container_width=True):
        try:
            with st.spinner("Loading FastF1 session data…"):
                st.session_state["session1"] = load_session(config1[0], config1[1], config1[2])
                st.session_state["session2"] = load_session(config2[0], config2[1], config2[2])
            st.session_state["config1"] = config1
            st.session_state["config2"] = config2
        except Exception as exc:
            st.error(f"Could not load the sessions: {exc}")
    if "session1" not in st.session_state or "session2" not in st.session_state:
        st.info("Choose the Grand Prix and sessions, then load them to select drivers and laps.")
        return
    if st.session_state.get("config1") != config1 or st.session_state.get("config2") != config2:
        st.info("The selected sessions have changed. Click **Load sessions** to refresh the data.")
        return
    pick1, pick2 = st.columns(2)
    result1 = lap_picker(st.session_state["session1"], config1[2], config1[3], config1[0], pick1, "1")
    result2 = lap_picker(st.session_state["session2"], config2[2], config2[3], config2[0], pick2, "2")
    if result1[0] is None or result2[0] is None:
        return
    if st.button("Compare laps", type="primary", use_container_width=True):
        try:
            label1, time1 = result1[1]
            label2, time2 = result2[1]
            seconds1, seconds2 = time1.total_seconds(), time2.total_seconds()
            st.subheader("Result")
            faster = label1 if seconds1 <= seconds2 else label2
            st.metric("Lap time difference", f"{abs(seconds1 - seconds2):.3f} s", f"Faster: {faster}")
            st.caption("A negative time delta means Lap 1 was ahead; a positive value means Lap 2 was ahead. Shaded areas mark speed differences of at least 7.5 km/h.")
            for fig in comparison_figures(result1[0], result2[0], label1, label2):
                st.pyplot(fig, use_container_width=True)
                plt.close(fig)
        except Exception as exc:
            st.error(f"Could not compare these laps: {exc}")


if __name__ == "__main__":
    main()
