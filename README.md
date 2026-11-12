# F1 Lap Comparison Tool

Welcome to F1 Lap Comparison Tool, this project developed in python allows f1 enthusiasts and analysts to compare any two laps in the FastF1 library. It not only calculates the time gap beetween both laps, but also allows the user to analyse telemetry of each lap, using the previous to make a prediction for the cause of such gap.

## Resources and functionality

This project, as said above, enables the user through it's input to choose any lap available at the fast f1 library. Then after the laps desired have been selected the problem firstly plot's a graph with speed and time delta in function of distance, highlighting the intervals in which the speed difference was considerably big enough. After that the throttle input and brake input graphs are displayed, in these time delta and the intervals above mentioned are also present, in addition to vertical dotted lines which signal considerable difference of inputs, which the program estimates to be the cause of the speed differences.
