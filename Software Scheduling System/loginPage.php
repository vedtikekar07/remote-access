<?php
include 'config.php';
$msg = "";
if (isset($_POST['submit'])) {
    $email = mysqli_real_escape_string($conn, $_POST['email']);
    $currentDate = date('Y-m-d');
    date_default_timezone_set('Asia/Kolkata');
    $currentTime = date('H:i');
    echo $currentTime;
    $sql = "SELECT * FROM booking WHERE email='{$email}'";
    $result = mysqli_query($conn, $sql);
    $row = mysqli_fetch_array($result, MYSQLI_ASSOC);

    if($row){
        if($email === $row["email"]){
            // Get the date and time from the database
            $dbDate = $row["date"];
            $dbTime = $row["timeslot"];

            if($dbDate === $currentDate){
                // Split the time range into start and end times
                list($startTime, $endTime) = explode("-", $dbTime);
                echo $startTime;
                echo $endTime;

                // Check if the current time is within the time range
                if($currentTime >= $startTime && $currentTime <= $endTime){
                    header("Location:  https://pratham5685.github.io/remote-lab-access/");
                }else{
                    $msg = "<div class='alert alert-danger'>Current time is not within the booked timeslot.</div>";
                } 
            }else{
                $msg = "<div class='alert alert-danger'>Date do not match.</div>";
            }
        }
    }else{
        $msg = "<div class='alert alert-danger'>Email do not match.</div>";
    }
}
?>

<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
    <link rel="stylesheet" href="style.css">
    <meta name="keywords"
        content="Login Form" />
    <!-- //Meta tag Keywords -->
    <link href="//fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap" rel="stylesheet">
    <!--/Style-CSS -->
    <!-- <link rel="stylesheet" href="css/style.css" type="text/css" media="all" /> -->
    <!--//Style-CSS -->
    <script src="https://kit.fontawesome.com/af562a2a63.js" crossorigin="anonymous"></script>
    <style>
            .back_button{
                position: absolute;
                top: 5%;
                left:5%;
            }
        </style>
</head>
<body>
<section class="w3l-mockup-form">
    <div class="back_button">
        <span><a href="index.php"><button type="button" id="btn" class="btn btn-success">Back</button></a></span>
    </div>
    <div class="container">
        <div class="workinghny-form-grid">
            <div class="main-mockup">
                <div class="content-wthree">
                    <?php echo $msg; ?>
                    <form action="loginPage.php" method="POST">
                        <label for="uname"><b>Email</b></label>
                        <input type="text" placeholder="Enter Email" name="email" required>
                        <button name="submit" type="submit" value="login">Login</button>  
                    </form>
                </div>
            </div>
        </div>
    </div>
</section>
