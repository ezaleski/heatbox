<?php

$m = new MongoClient();
$db = $m->selectDB("heatbox");
$music = new MongoCollection($db, "music");
$mode = new MongoCollection($db, "mode");
$score = new MongoCollection($db, "score");

$CLOCK_RUNMODE = 1;
$COUNTDOWN_RUNMODE = 2;
$INTERVAL_RUNMODE = 3;
$SCOREBOARD_RUNMODE = 4;
$SYSMENU_RUNMODE = 5;
$NONE_RUNMODE = 6;


function getCurrentMode()
{
	global $mode;
	global $CLOCK_RUNMODE;
	global $COUNTDOWN_RUNMODE;
	global $INTERVAL_RUNMODE;
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


?>
