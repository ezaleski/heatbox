<?php
require_once("mongo.php");
$action = $_GET['action'];
if (!isset($action)) {
	$action = $_POST['action'];
}
$value = $_GET['value'];
$sharedPipe = "/tmp/heatbox_pipe";
$scoreboardMode = 4;
$intervalMode = 9;

$ret = array('ret' => 1, 'message' => 'OK');

if ($action == "hotspotup") {
	$out = fopen($sharedPipe,"a");
	fwrite($out,"hotspotup,".$value."\n");
	fclose($out);
}
if ($action == "hotspotdown") {
	$out = fopen($sharedPipe,"a");
	fwrite($out,"hotspotdown,".$value."\n");
	fclose($out);
}
if ($action == "turnoff") {
	$out = fopen($sharedPipe,"a");
	fwrite($out,"turnoff,".$value."\n");
	fclose($out);
}
if ($action == "set") {
	$out = fopen($sharedPipe,"a");
	fwrite($out,"set,".$value."\n");
	fclose($out);
}
if ($action == "countDown") {
	$value2 = $_GET['value2'];
	$out = fopen($sharedPipe,"a");
	fwrite($out,"countDown,".$value.",".$value2."\n");
	fclose($out);
}
if ($action == "clear") {
	$out = fopen($sharedPipe,"a");
	fwrite($out,"clear,".$value."\n");
	fclose($out);
}
if ($action == "startclock") {
	$out = fopen($sharedPipe,"a");
	fwrite($out,"startclock,".$value."\n");
	fclose($out);
}
if ($action == "stopclock") {
	$out = fopen($sharedPipe,"a");
	fwrite($out,"stopclock,".$value."\n");
	fclose($out);
}
if ($action == "strandtest") {
	$out = fopen($sharedPipe,"a");
	fwrite($out,"strandtest,".$value."\n");
	fclose($out);
}
if ($action == "strandteststop") {
	$out = fopen($sharedPipe,"a");
	fwrite($out,"strandteststop,".$value."\n");
	fclose($out);
}
if ($action == "shutdown") {
	$out = fopen($sharedPipe,"a");
	fwrite($out,"shutdown,".$value."\n");
	fclose($out);
}
if ($action == "keypress") {
	$out = fopen($sharedPipe,"a");
	fwrite($out,"keypress,".$value."\n");
	fclose($out);
}
if ($action == "music") {
	$handled = false;
	if ($value == "stop") {
		shell_exec("/usr/bin/mpc stop");
		$handled = true;
	}
	if ($value == "play") {
		shell_exec("/usr/bin/mpc play");
		$handled = true;
	}
	if ($value == "volup") {
		system("/usr/bin/amixer set Speaker 5%+ 2>&1 > /dev/null");
		$handled = true;
	}
	if ($value == "voldown") {
		system("/usr/bin/amixer set Speaker 5%- 2>&1 > /dev/null");
		$handled = true;
	}
	if (!$handled) {
		shell_exec("/usr/bin/mpc clear");
		shell_exec("/usr/bin/mpc add '$value'");
		shell_exec("/usr/bin/mpc play");
	}
}
if ($action == "homeColor") {
	setCurrentMode($scoreboardMode);
	updateScoreColor(true, $value);
}
if ($action == "homeUp") {
	setCurrentMode($scoreboardMode);
	updateScore(true, intval($value));
	$ret['data'] = getScore();	
}
if ($action == "homeSpecific") {
	setCurrentMode($scoreboardMode);
	updateScoreSpecific(true, intval($value));
	$ret['data'] = getScore();	
}
if ($action == "homeDown") {
	setCurrentMode($scoreboardMode);
	updateScore(true, -intval($value));
	$ret['data'] = getScore();	
}
if ($action == "awayColor") {
	setCurrentMode($scoreboardMode);
	updateScoreColor(false, $value);
}
if ($action == "awaySpecific") {
	setCurrentMode($scoreboardMode);
	updateScoreSpecific(false, intval($value));
	$ret['data'] = getScore();	
}
if ($action == "awayUp") {
	setCurrentMode($scoreboardMode);
	updateScore(false, intval($value));
	$ret['data'] = getScore();	
}
if ($action == "awayDown") {
	setCurrentMode($scoreboardMode);
	updateScore(false, -intval($value));
	$ret['data'] = getScore();	
}
if ($action == "resetScore") {
	setCurrentMode($scoreboardMode);
	resetScore();
	$ret['data'] = getScore();	
}
if ($action == "startInterval") {
	setCurrentMode($intervalMode);
	$intervalId = $_GET['intervalId'];
	updateIntervalState($intervalId, "running");
}
if ($action == "getSounds") {
	$data = getSounds();
	$ret['data'] = $data;	
}
if ($action == "deleteInterval") {
	$intervalId = $_GET['intervalId'];
	if (isset($intervalId)) {
		deleteInterval($intervalId);
	}
}
if ($action == "saveInterval") {
	$data = $_POST['intervalData'];
	$obj = json_decode($data);

	if (isset($_POST['intervalId'])) {
		$intervalId = $_POST['intervalId'];
		updateInterval($intervalId, $obj);
	}
	else {
		addInterval($obj);
	}
	$ret['data'] = $obj;
}

header('Content-Type: application/json');
print json_encode($ret);
?>
