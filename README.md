# IOT-Assignment1 Functions


# config.json
Use to allocate min and max temp and humitdity

# monitorAndNotify.py
Get the current Temp and Humidity and trigger a warning if those go out of bounds of the max and min temp and humidity allocated. Can be run in the background with a CronJob. The current temp and humidity is logged in as a table via sqlite.

# createReport.py
Creates a report (via sqlite) based on comparing your min and max temp and humidity with the recorded temp and humidity from the table data of temps and humidity time stamped. Within the range shows GOOD, otherwise out of range shows BAD.

# gbluetooth.py
Uses Bluetooth to detect devices (that are paired) and send a message when temp or humidity goes out of bounds.

# analytics.py
Converts our data into two different graphs. 
One is a histogram of temperatures via MAT. 
The other makes a box-plot using Seaborn.
