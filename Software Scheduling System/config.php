<?php
//if any connection error trying chaninging localhost to localhost:8080
$conn = mysqli_connect("localhost","root", "", "booking_calender");

if (!$conn){
    echo "Connection failed";
}
