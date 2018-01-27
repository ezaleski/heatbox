<?php

$m = new MongoClient();
$db = $m->selectDB("heatbox");
$music = new MongoCollection($db, "music");
$mode = new MongoCollection($db, "mode");
$score = new MongoCollection($db, "score");
$sounds = new MongoCollection($db, "sounds");
$intervals = new MongoCollection($db, "intervals");
$intervalsteps = new MongoCollection($db, "intervalsteps");
$interval_state = new MongoCollection($db, "interval_state");

$CLOCK_RUNMODE = 1;
$COUNTDOWN_RUNMODE = 2;
$INTERVAL_RUNMODE = 3;
$SCOREBOARD_RUNMODE = 4;
$SYSMENU_RUNMODE = 5;
$NONE_RUNMODE = 6;
$INTERVAL_RUNNING_RUNMODE = 9;


function getCurrentMode()
{
	global $mode;
	global $CLOCK_RUNMODE;
	global $COUNTDOWN_RUNMODE;
	global $INTERVAL_RUNMODE;
	global $INTERVAL_RUNNING_RUNMODE;
	global $SCOREBOARD_RUNMODE;
	global $SYSMENU_RUNMODE;
	global $NONE_RUNMODE;

	$cMode = 'UNKNOWN';
	$currentMode = $mode->findOne(array());
	if ($currentMode) {
		$m = $currentMode['current'];
		if ($m == $CLOCK_RUNMODE) {
			$cMode = 'CLOCK';
		}
		if ($m == $COUNTDOWN_RUNMODE) {
			$cMode = 'COUNTDOWN';
		}
		if ($m == $INTERVAL_RUNMODE) {
			$cMode = 'INTERVAL';
		}
		if ($m == $INTERVAL_RUNNING_RUNMODE) {
			$cMode = 'INTERVAL_RUNNING';
		}
		if ($m == $SCOREBOARD_RUNMODE) {
			$cMode = 'SCOREBOARD';
		}
		if ($m == $SYSMENU_RUNMODE) {
			$cMode = 'SYSTEM MENU';
		}
		if ($m == $NONE_RUNMODE) {
			$cMode = 'OFF';
		}
	}
	return $cMode;
}

function setCurrentMode($m)
{
	global $mode;

	$mode->remove(array());
	$mode->insert(array('current' => $m));
	return;
}
function resetScore()
{
	global $score;
	$doc = array("home" => 0, "away" => 0);
	$score->update(array(), array('$set' => $doc));
}
function updateScoreColor($homeFlag, $color)
{
	global $score;

	$whichColor = "awayColor";
	if ($homeFlag) {
		$whichColor = "homeColor";
	}
	$score->update(array(), array('$set' => array($whichColor => $color)));
}
function getScore()
{
	global $score;

	$current = $score->findOne(array());

	return $current;
}
function updateScoreSpecific($homeFlag, $amount)
{
	global $score;

	$current = $score->findOne(array());
	if ($current) {
		if ($homeFlag) {
			$skip = false;
			if ($current['home'] == 0 && $amount < 0) {
				$skip = true;
			}
			if (!$skip) {
				$score->update(array(), array('$set' => array('home' => $amount)));
			}
		}
		else {
			$skip = false;
			if ($current['away'] == 0 && $amount < 0) {
				$skip = true;
			}
			if (!$skip) {
				$score->update(array(), array('$set' => array('away' => $amount)));
			}
		}
	}
	else {
		if ($homeFlag) {
			$doc = array("home" => $amount, "away" => 0);
		}
		else {
			$doc = array("away" => $amount, "home" => 0);
		}
		$score->insert($doc);
	}
}
function updateScore($homeFlag, $amount)
{
	global $score;

	$current = $score->findOne(array());
	if ($current) {
		if ($homeFlag) {
			$skip = false;
			if ($current['home'] == 0 && $amount < 0) {
				$skip = true;
			}
			if (!$skip) {
				$score->update(array(), array('$inc' => array('home' => $amount)));
			}
		}
		else {
			$skip = false;
			if ($current['away'] == 0 && $amount < 0) {
				$skip = true;
			}
			if (!$skip) {
				$score->update(array(), array('$inc' => array('away' => $amount)));
			}
		}
	}
	else {
		if ($homeFlag) {
			$doc = array("home" => $amount, "away" => 0);
		}
		else {
			$doc = array("away" => $amount, "home" => 0);
		}
		$score->insert($doc);
	}
}
function deleteInterval($intervalId)
{
	global $intervals;

	$intervals->remove(array("intervalId" => $intervalId));

}
function getTimeFrom($t)
{
	list($mins,$secs) = explode(':',$t);
	$seconds = mktime(0,$mins,$secs) - mktime(0,0,0);
	return $seconds;
}
function updateIntervalState($intervalId, $state)
{
	global $interval_state;

	$interval_state->remove(array());

	$doc = array("intervalId" => $intervalId, "state" => $state);
	if ($state == "running") {
		$interval = getIntervalData($intervalId);
		$steps = array();
		$name = "";
		if (isset($interval["intervalData"]["name"])) {
			$name = $interval["intervalData"]["name"];
		}
		
		if (isset($interval["intervalData"]["steps"])) {
			$counter = 0;
			$accumTime = 0;
			foreach ($interval["intervalData"]["steps"] as $step) {
				$beforeStepDuration = 0;
				if ($step["beforeStep"] == "TIMER") {
					$beforeStepDuration = getTimeFrom($step["beforeStepTimer"]);
				}
				$stepDuration = getTimeFrom($step["step"]);
				$beforeStepStart = time() + $accumTime;
				$stepStart = $beforeStepStart + $beforeStepDuration;
				$stepEnd = $beforeStepStart + $stepDuration + $beforeStepDuration;
				$accumTime = $accumTime + ($stepEnd - $beforeStepStart);

				$step["beforeStartTime"] = $beforeStepStart;
				$step["startTime"] = $stepStart;
				$step["endTime"] = $stepEnd;
				$step["status"] = "waiting";
				if ($counter == 0) {
					$step["status"] = "before";
				}
				
				$steps[] = $step;
				$counter++;
			}
			$doc["name"] = $name;
			$doc["steps"] = $steps;
		}
	}
	$interval_state->insert($doc);
}
function updateInterval($intervalId, $intervalData)
{
	global $intervals;

	$current = $intervals->findOne(array("intervalId" => $intervalId));
	if ($current) {
		$current["intervalData"] = $intervalData;
		$intervals->save($current);
	}

}
function addInterval($intervalData)
{
	global $intervals;
	$intervalId = new MongoId()."";

	$intervals->insert(array("intervalId" => $intervalId, "intervalData" => $intervalData));

}

function getIntervalData($intervalId)
{
	global $intervals;
	$data = $intervals->findOne(array("intervalId" => $intervalId));
	return $data;

}
function getSounds()
{
	global $sounds;

	$ret = [];

	foreach ($sounds->find() as $sound) {
		$sound['id'] = "".$sound["_id"];
		unset($sound["_id"]);
		$ret[] = $sound;
	}
	return $ret;
}


?>
