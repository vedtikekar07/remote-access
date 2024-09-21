
# Import necessary libraries
from flask import Flask, jsonify, render_template_string , render_template , request
import requests
import Adafruit_DHT
import time
import RPi.GPIO as GPIO
from time import sleep
from gpiozero import AngularServo
import subprocess
import pigpio



# Initialize Flask app
app = Flask(__name__)

pi = pigpio.pi()
if not pi.connected:
    print("Error: Could not connect to pigpio daemon.")
    exit()

# ThinkSpeak API Keys
CHANNEL_ID = "2465224"
WRITE_API_KEY = "M5LVVIVDNDH0T7PW"

# Set up GPIO
GPIO.setmode(GPIO.BCM)
RELAY_PIN = 21
GPIO.setup(RELAY_PIN, GPIO.OUT, initial=GPIO.HIGH)  # Set initial state to HIGH

# Store previous temperature value
prev_temperature = None


# HTML content for Home Page (index)
home_page_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Remote Lab</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            background-color: #f0f0f0;
        }

        .container {
            max-width: 500px;
            margin: 0 auto;
            padding: 20px;
            background-color: #ffffff;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
            border-radius: 5px;
            margin-top: 50px;
        }

        h1, h2 {
            color: #333;
        }

        a {
            display: block;
            margin: 10px 0;
            padding: 10px;
            background-color: #007BFF;
            color: #fff;
            text-decoration: none;
            border-radius: 5px;
            transition: background-color 0.3s;
        }

        a:hover {
            background-color: #0056b3;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to the Remote Lab</h1>
        
        <!-- Lab List -->
        <h2>Lab List</h2>
        <a href="/computational_lab">Computational Power Lab</a>
        <a href="/temperature_lab">Temperature Remote Sensing Lab</a>
        <a href="/robotics-lab">Robotics Lab</a>
    </div>
</body>
</html>
"""

# HTML content for Computational Power Lab Page

computational_lab_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Computational Power Lab</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            background-color: #f0f0f0;
        }

        .container {
            max-width: 500px;
            margin: 0 auto;
            padding: 20px;
            background-color: #ffffff;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
            border-radius: 5px;
            margin-top: 50px;
        }

        h1, h2 {
            color: #333;
        }

        p {
            color: #555;
        }

        textarea {
            width: 100%;
            height: 200px;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
            margin-bottom: 10px;
        }

        button {
            background-color: #007BFF;
            color: #fff;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }

        #computationalOutput {
            margin-top: 10px;
            padding: 10px;
            background-color: #f9f9f9;
            border: 1px solid #ccc;
            border-radius: 5px;
        }

        #computationalExecutionTime {
            margin-top: 10px;
            color: #777;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Computational Power Lab</h1>
        <p>Perform computations and measure execution time:</p>
        <textarea id="computationalCode" placeholder="Enter Python code here"></textarea>
        <button onclick="executeComputationalCode()">Execute</button>
        <div id="computationalOutput"></div>
        <div id="computationalExecutionTime"></div>
    </div>
    
    <script>
        function executeComputationalCode() {
            const computationalCode = document.getElementById("computationalCode").value;

            fetch("/execute_computational", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ code: computationalCode }),
            })
            .then((response) => response.json())
            .then((data) => {
                document.getElementById("computationalOutput").innerText = data.output;
                document.getElementById("computationalExecutionTime").innerText = `Execution Time: ${data.execution_time}`;
            })
            .catch((error) => {
                console.error("Error:", error);
            });
        }
    </script>
</body>
</html>
"""


# HTML content for Temperature Remote Sensing Lab Page
temperature_lab_content = """
<!DOCTYPE html>
<html>

<head>
<script src='https://cdn.plot.ly/plotly-2.29.1.min.js'></script>
    <title>Temperature Remote Sensing Lab</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            text-align: center;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }

        .container {
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background-color: #fff;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
        }

        h1 {
            color: #333;
        }

        p {
            color: #555;
            margin-bottom: 20px;
        }
        button{
        margin-top:10px;
        margin-right:10px;
        margin-bottom:20px;
        height: 60px;
        width:90px;
        font-size:20px;
        background-color: #7E90FF;
        border-radius: 8px;
        border: 2px solid #7E90FF;
        }

        #temperatureReading {
            margin-top: 20px;
            padding: 20px;
            background-color: #f9f9f9;
            border: 1px solid #ccc;
            border-radius: 5px;
            font-size: 18px;
            color: #333;
        }
        a:link { 
  text-decoration: none; 
} 
a:visited { 
  text-decoration: none; 
} 
a:hover { 
  text-decoration: none; 
} 
a:active { 
  text-decoration: none; 
}

    </style>
</head>

<body>
    <div class="container">
        <h1>Remote Temperature Monitoring and control System</h1>
        <p>Real-time temperature and humidity:</p>
        <div id="temperatureReading"></div>
    </div>
    <div id='myDiv'></div>
    <button><a href="/control-page"> Relay Control</a></button>
    <script>
        var count = 0;
        var current_temp = 0;
        var current_temp_sliced = 0;
        var current_humid_sliced = 0;
        var current_temp_int = 0;
        var current_humid_int = 0;
        var threshold = 29;
var valueNumber = [];
var temp = [];
var humid = [];
var trace2 = {
   x: valueNumber,
   y: temp,
   type: 'scatter'
 };
 var trace1 = {
  x: valueNumber,
  y: humid,
  type: 'scatter'
};
  function plotGraph(){
   data = [trace2, trace1];
   Plotly.newPlot('myDiv', data);
 }
 
 function turnOnRelay() {
            fetch("/turn_on", { method: "POST" })
                .then(response => response.text())
                .then(data => {
                    // alert(data);
                    document.getElementById("relayState").innerText = "Current Relay State: On";
                })
                .catch(error => console.error("Error:", error));
        }

        function turnOffRelay() {
            fetch("/turn_off", { method: "POST" })
                .then(response => response.text())
                .then(data => {
                    // alert(data);
                    document.getElementById("relayState").innerText = "Current Relay State: Off";
                })
                .catch(error => console.error("Error:", error));
        }
 
 function getTemperatureReading() {
            fetch("/get_temperature")
                .then(response => response.json())
                .then(data => {
                    // Display previous temperature if current temperature is not defined
                    let temperature = data.temperature ? data.temperature : "{{ prev_temperature }}";
                     console.log(typeof(data.temperature));
                    current_temp = temperature;
                   console.log(current_temp);
                   current_temp_sliced = temperature.slice(0, 2);
                   current_humid_sliced = temperature.slice(18,20);
                   console.log(current_temp_sliced, current_humid_sliced);
                   current_temp_int = parseInt(current_temp, 10);
                   current_humid_int = parseInt(current_humid_sliced, 10);
                   console.log(current_temp_int, current_humid_int);
                    if(count<100)
                   {
                       count++;
                        valueNumber.push(count);
                        humid.push(current_humid_int);
                        temp.push(current_temp_int);
                }
                else{
                    temp.shift();
                    humid.shift();
                    humid.push(current_humid_int);
                    temp.push(current_temp_int);
                }
                    
                   plotGraph()
                   if(current_temp_int >= threshold)
                   {
                    turnOnRelay()    
                   }
                   else{
                   turnOffRelay()
                   }
                    document.getElementById("temperatureReading").innerText = `Temperature: ${temperature}`;
                })
                .catch(error => {
                    console.error("Error:", error);
                });
        }
        
        // Fetch temperature data every 5 seconds
        setInterval(getTemperatureReading, 5000);
       
    </script>
</body>

</html>

"""

# HTML content for the control page
control_page_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Relay Control</title>
    <style>
    body{
    font-family:'Arial', sans-serif;
    text-align: center;
    background-color:#f4f4f4;
    margin:0;
    padding:0;
    }
        .container{
        max-width: 600px;
        height: 200px;
        margin: 200px auto;
        padding: 20px;
        background-color: #fff;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
        border-radius: 8px
        }
        h1{
        color: #333;
        }
        button{
        margin-top:10px;
        margin-right:10px;
        margin-bottom:20px;
        height: 60px;
        width:90px;
        font-size:20px;
        background-color: #7E90FF;
        border-radius: 8px;
        border: 2px solid #7E90FF;
        }
        #relayState{
        font-size:20px;
        }
    </style>
    <script>
        function turnOnRelay() {
            fetch("/turn_on", { method: "POST" })
                .then(response => response.text())
                .then(data => {
                    alert(data);
                    document.getElementById("relayState").innerText = "Current Relay State: On";
                })
                .catch(error => console.error("Error:", error));
        }

        function turnOffRelay() {
            fetch("/turn_off", { method: "POST" })
                .then(response => response.text())
                .then(data => {
                    alert(data);
                    document.getElementById("relayState").innerText = "Current Relay State: Off";
                })
                .catch(error => console.error("Error:", error));
        }
    </script>
</head>
<body>
<div class="container">
    <h1>Relay Control</h1>
    <button onclick="turnOnRelay()">Turn On</button>
    <button onclick="turnOffRelay()">Turn Off</button><br>
    <div id="relayState">Current Relay State: Off</div>
</div>
</body>
</html>
"""


robotics_lab_content =  '''
 <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Servo Control</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }

        .container {
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background-color: #fff;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
        }

        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 20px;
        }

        form {
            margin-bottom: 20px;
        }

        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }

        input[type="number"] {
            width: calc(100% - 22px); /* Adjusted width to account for padding */
            padding: 10px;
            margin-bottom: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
            box-sizing: border-box;
        }

        input[type="hidden"] {
            display: none;
        }

        button[type="submit"] {
            width: 100%; /* Button width set to 100% */
            background-color: #007BFF;
            color: #fff;
            padding: 10px 0; /* Adjusted padding for better alignment */
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }

        button[type="submit"]:hover {
            background-color: #0056b3;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Remote Robot Control</h1>
        <form action="/move" method="post">
            <label for="bottom_left">Bottom Left Motor:</label>
            <input type="number" name="angle" id="bottom_left" placeholder="Enter angle">
            <input type="hidden" name="motor" value="bottom_left">
            <button type="submit">Run</button>
        </form>
        <form action="/move" method="post">
            <label for="bottom_right">Bottom Right Motor:</label>
            <input type="number" name="angle" id="bottom_right" placeholder="Enter angle">
            <input type="hidden" name="motor" value="bottom_right">
            <button type="submit">Run</button>
        </form>
        <form action="/move" method="post">
            <label for="top_left">Top Left Motor:</label>
            <input type="number" name="angle" id="top_left" placeholder="Enter angle">
            <input type="hidden" name="motor" value="top_left">
            <button type="submit">Run</button>
        </form>
        <form action="/move" method="post">
            <label for="top_right">Top Right Motor:</label>
            <input type="number" name="angle" id="top_right" placeholder="Enter angle">
            <input type="hidden" name="motor" value="top_right">
            <button type="submit">Run</button>
        </form>
    </div>
</body>
</html>
    '''


# Define routes

@app.route("/")
def index():
    return render_template_string(home_page_content)


#Lab 1 
# Computational Power Lab Page
@app.route("/computational_lab")
def computational_lab():
    return render_template_string(computational_lab_content)

@app.route("/execute_computational", methods=["POST"])
def execute_computational_code():
    try:
        data = request.get_json()
        computational_code = data["code"]

        # Execute the computational code
        start_time = time.time()
        result = subprocess.check_output(["python3", "-c", computational_code], stderr=subprocess.STDOUT, text=True)
        end_time = time.time()

        execution_time = end_time - start_time

        return jsonify({"output": result.strip(), "execution_time": f"{execution_time:.5f} seconds"})
    except Exception as e:
        return jsonify({"error": str(e)})
    

# Lab 2 - Remote Temperature sensing Lab


# Home Page (index)
@app.route("/temperature_lab")
def templab():
    return render_template_string(temperature_lab_content, prev_temperature=prev_temperature)


@app.route("/control-page")
def control_page():
    return render_template_string(control_page_content)   

# Simulate Temperature Reading
# Simulate Temperature Reading and Send Data to ThingSpeak
@app.route("/get_temperature", methods=["GET"])
def get_temperature_reading():
    global prev_temperature
    # Read real-time temperature from DHT sensor
    DHT_SENSOR = Adafruit_DHT.DHT11
    DHT_PIN = 4
    humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
    
    if humidity is not None and temperature is not None:
        temperature_reading = f"{temperature:.1f}°C, Humidity: {humidity:.1f}%"
        prev_temperature = temperature_reading
        
        # Send data to ThingSpeak
        try:
            url = f"https://api.thingspeak.com/update?api_key=M5LVVIVDNDH0T7PW&field1={temperature}&field2={humidity}"
            response = requests.get(url)
            if response.status_code == 200:
                print("Data sent to ThingSpeak successfully!")
            else:
                print("Failed to send data to ThingSpeak:", response.text)
        except Exception as e:
            print("Error sending data to ThingSpeak:", str(e))
        
        return jsonify({"temperature": temperature_reading})
    else:
        if prev_temperature is not None:
            return jsonify({"temperature": prev_temperature})
        else:
            return jsonify({"error": "Sensor failure. Check wiring."})



# Route to turn on the relay
@app.route("/turn_on", methods=["POST"])
def turn_on():
    GPIO.output(RELAY_PIN, GPIO.LOW)  # Set pin to LOW to turn on the relay
    return "Relay turned on."

# Route to turn off the relay
@app.route("/turn_off", methods=["POST"])
def turn_off():
    GPIO.output(RELAY_PIN, GPIO.HIGH)  # Set pin to HIGH to turn off the relay
    return "Relay turned off."





#----------------- Lab 3 -------------------#

@app.route("/robotics-lab")
def roboticslab():
    return render_template_string(robotics_lab_content)


# Define servo pins and pulse width range
servo_pins = {
    'bottom_left': 18,
    'bottom_right': 17,
    'top_left': 22,
    'top_right': 23
}
servo_min = 500
servo_max = 2500

# Function to move the specified servo motor to the desired angle
def move_servo(pin, angle):
    if angle < -90:
        angle = -90
    elif angle > 90:
        angle = 90
    pulse_width = int(servo_min + (servo_max - servo_min) * (angle + 90) / 180)
    pi.set_servo_pulsewidth(pin, pulse_width)
    sleep(1)  # Adjust sleep duration as needed
    pi.set_servo_pulsewidth(pin, 0)  # Turn off signal after movement

# Route to move the servo motors
@app.route('/move', methods=['POST'])
def move():
    try:
        motor = request.form['motor']
        angle = int(request.form['angle'])
        
        if motor in servo_pins:
            pin = servo_pins[motor]
            move_servo(pin, angle)
            return f'Moved {motor} motor to angle {angle}', 200
        else:
            return 'Invalid motor', 400
    except Exception as e:
        return f'Error: {e}', 500


# Run the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)