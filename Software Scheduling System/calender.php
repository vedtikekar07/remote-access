<?php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

function build_calender($month, $year){

    $mysqli = new mysqli("sql308.infinityfree.com","if0_36221294", "XdhQn78NXjxQ4NC", "if0_36221294_booking_calender");
    // $stmt = $mysqli->prepare('select * from calender where MONTH(date) = ? AND YEAR(date) = ?');
    // $stmt->bind_param('ss', $month, $year);
    // $bookings = array();
    // if($stmt->execute()){
    //     $result = $stmt->get_result();
    //     if($result -> num_rows>0){
    //         while($row = $result->fetch_assoc()){
    //             $bookings[] = $row['date'];
    //         }
    //         $stmt->close();
    //     }  
    // }

    //creating an array containing names of all days in a week
    $daysOfWeek = array('Sunday','Monday','Tuesday', 'Wednesday','Thursday','Friday','Saturday');

    //getting 1st day of the month (argument of this function)
    $firstDayOfMonth = mktime(0,0,0,$month,1,$year);

    //number of days in a month
    $numberDays = date('t',$firstDayOfMonth);

    //info abt the 1st day of this month
    $dateComponents = getdate($firstDayOfMonth);

    $monthName = $dateComponents['month'];
    $dayOfWeek = $dateComponents['wday'];

    // getting current date
    $dateToday = date('Y-m-d');

    //HTML table
    // $calender = "<table class='table table-bordered'>";
    
    $prev_month = date('m', mktime(0,0,0,$month-1,1,$year));
    $prev_year = date('Y', mktime(0,0,0,$month-1,1,$year));
    $next_month = date('m', mktime(0,0,0,$month+1,1,$year));
    $next_year = date('Y', mktime(0,0,0,$month+1,1,$year));
    $calender ="<center><h2>$monthName $year</h2>";

    $calender.="<a class='btn btn-primary btn-xs' href='?month=".$prev_month."&year=$prev_year'>Prev Month</a>";
    $calender.="<a class='btn btn=primary btn-xs' href='?month=".date('m')."&year=".date('Y')."'>Current Month</a>";
    $calender.="<a class='btn btn-primary btn-xs' href='?month=".$next_month."&year=$next_year'>Next Month</a></center>";
    $calender.="<br><table class='table table-bordered'>";
    $calender.="<tr>";
    foreach($daysOfWeek as $day){
        $calender.= "<th class='header'>$day</th>";
    }

    $calender.="</tr><tr>";
    $currentDay =1;
    if($dayOfWeek > 0){
        for($k = 0; $k < $dayOfWeek; $k++){
            $calender.="<td class='empty'></td>";
        }
    }
    $month = str_pad($month, 2, "0", STR_PAD_LEFT);
    while($currentDay <= $numberDays){
        if($dayOfWeek == 7){
            $dayOfWeek = 0;
            $calender.= "</tr><tr>";
        }

        $currentDayRel = str_pad($currentDay, 2, "0", STR_PAD_LEFT);
        $date = "$year-$month-$currentDayRel";
        $dayName = strtolower(date("l", strtotime($date)));
        $eventNum = 0;
        $today = $date==date('Y-m-d') ? 'today' : '';
        // if($dayName=='saturday'){
        //     $calender.="<td><h4>$currentDay</h4> <button class='btn btn-danger btn-xs'>Holiday</button>";
        // }else
        if($date<date('Y-m-d')){
            $calender.="<td><h4>$currentDay</h4> <button class='btn btn-danger btn-xs'>N/A</button>";
        }
        else{
            $totalbookings = checkSlot($mysqli, $date);
            if($totalbookings==18){
                $calender.= "<td class='$today'><h4>$currentDay</h4><a href='#' class='btn btn-danger btn-xs'>Already booked</a></td>";
            }else{
                $calender.= "<td class='$today'><h4>$currentDay</h4><a href='book.php?date=".$date."' class='btn btn-success btn-xs'>BOOK</a></td>";
            }
            
        }

        $currentDay++;
        $dayOfWeek++;
    }

    if($dayOfWeek < 7){
        $remainingDays = 7 - $dayOfWeek;
        for($i = 0; $i< $remainingDays; $i++){
            $calender.="<td class='empty'></td>";
        }
    }
    $calender.= "</tr></table>";
    return $calender;
 
}
function checkSlot($mysqli, $date){
    $stmt = $mysqli->prepare('select * from booking where date = ?');
    $stmt->bind_param('s', $date);
    $totalbookings = 0;
    if($stmt->execute()){
        $result = $stmt->get_result();
        if($result -> num_rows>0){
            while($row = $result->fetch_assoc()){
                $totalbookings++;
            }
            $stmt->close();
        } 
    } 
    return $totalbookings;
}
?>

<html>
    <head>
        <meta name="viewport" content = "width=device-width, initial-scale=1.0">
        <link rel = "stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.0/css/bootstrap.min.css">
        <link rel="stylesheet" href="calender.css">
    
    </head>
    <body>
        <div class = "container">
            <div class = "row">
                <div class="col-md-12">
                <div class="back_button">
                        <span><a href="index.php"><button type="button" id="btn" class="btn btn-success">Back</button></a></span>
                    </div>
                    <?php
                        $dateComponents = getdate();
                        if(isset($_GET['month']) && isset($_GET['year'])){
                            $month = $_GET['month'];
                            $year = $_GET['year'];
                        }else{
                            $month = $dateComponents['mon'];
                            $year = $dateComponents['year'];
                        }
                        echo build_calender($month, $year);
                    ?>
                </div>
                
            </div>
        </div>
    </body>
</html>
    
