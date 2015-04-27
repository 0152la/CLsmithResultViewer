# CLsmithResultViewer
A GUI to be used with the .csv files obtained from CLsmith testing.

### Requirements
* Python 2.7
* Kivy library (on Ubuntu, install the **python-kivy** package)

### Usage
To run, execute **./showresults.py**.

The first window is the folder selection screen. Highlight the desired folder and click the **Select** button, then click **Okay** to confirm the selection.

A quick rundown of the comparison view window:
* A filter and platform have to be chosen before the entire view is visible.
* The filter removes results meeting certain conditions. For example, **None** filters nothing, **Matching** filters programs where the chosen platform has the same results as the majority, **MatchingPlat** filters programs where the chosen platform has the same result as the comparison platform.
* The name of the currently inspected program is in the text box at the top, with the number of lines in parantheses. A specific program can be investigate by typing in its name in this box.

### TODOs and issues
* **Output HTML** button is currently a dummy button.
* Possibly a textbox to select a specific program index, rather than only having to give the name.
