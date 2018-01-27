<?php
require_once('header.php');
require_once('mongo.php');
$homeColor = "rgb(255, 0, 0)";
$awayColor = "rgb(0, 255, 0)";

$scoreObj = $score->findOne(array());
$homeScore = 0;
$awayScore = 0;
if ($scoreObj) {
	$homeScore = $scoreObj['home'];
	$awayScore = $scoreObj['away'];
	if (isset($scoreObj['homeColor'])) {
		$homeColor = 'rgb('.$scoreObj['homeColor'].')';
	}
	if (isset($scoreObj['awayColor'])) {
		$awayColor = 'rgb('.$scoreObj['awayColor'].')';
	}
}
?>
<script type="text/javascript">
function openMe(url)
{
	$.get(url, function( data ) {
		var homeScore = data.data["home"];
		var awayScore = data.data["away"];
		$("#homeScore").html(homeScore);
		$("#awayScore").html(awayScore);
	});
}
$( document ).ready(function() {
	$("#setButton").click(function() {
		sendIt("set");
	});
	$("#countDownButton").click(function() {
		sendIt("countDown");
	});
	$(".button").button();
	$("#homeUpButton").on('vclick', function () {
		openMe('api.php?action=homeUp&value=1');
	});
	$("#homeDownButton").on('vclick', function () {
		openMe('api.php?action=homeDown&value=1');
	});
	$("#awayUpButton").on('vclick', function () {
		openMe('api.php?action=awayUp&value=1');
	});
	$("#awayDownButton").on('vclick', function () {
		openMe('api.php?action=awayDown&value=1');
	});
	$("#resetButton").on('vclick', function () {
		openMe('api.php?action=resetScore&value=0');
	});
	$("#homeColor").spectrum({
	    preferredFormat: "rgb",
	    color: "<?php print $homeColor;?>",
	    change: function(color) {
			var rgb = Math.floor(color._r) + "," + Math.floor(color._g) + "," + Math.floor(color._b);
			openMe('api.php?action=homeColor&value=' + rgb);
		}
	});
	$("#awayColor").spectrum({
	    preferredFormat: "rgb",
	    color: "<?php print $awayColor;?>",
	    change: function(color) {
			var rgb = Math.floor(color._r) + "," + Math.floor(color._g) + "," + Math.floor(color._b);
			openMe('api.php?action=awayColor&value=' + rgb);
		}
	});
});
</script>
<div data-role="page">
	<div data-role="header">
	  <a href="index.php" class="ui-btn ui-btn-left ui-corner-all ui-shadow ui-icon-home ui-btn-icon-left">Home</a>
	  <h1>Scoreboard</h1>
	</div>
<?php require_once('mode.php'); ?>
	<div class="ui-grid-a" data-theme="b">
		<div class="ui-block-a">
			<center>
				<h2>HOME</h2>
				<div style="padding: 10px;">
					<a class="button" id=homeUpButton >Up</a></br></br>
				</div>
				<font style="font-size: 150;line-height: 1.0 !important;"><span id="homeScore"><?php print $homeScore;?></span></font><br>
				<div style="padding: 10px;">
					<a class="button" id=homeDownButton >Down</a>
				</div>
				<div style="padding: 10px;">
					<input type='none' id="homeColor" />
				</div>
			</center>
		</div>
		<div class="ui-block-b">
			<center>
				<h2>AWAY</h2>
				<div style="padding: 10px;">
					<a class="button" id=awayUpButton >Up</a></br></br>
				</div>
				<font style="font-size: 150;line-height: 1.0 !important;"><span id="awayScore"><?php print $awayScore;?></span></font><br>
				<div style="padding: 10px;">
					<a class="button" id=awayDownButton >Down</a>
				</div>
				<div style="padding: 10px;">
					<input type='none' id="awayColor" />
				</div>
			</center>
		</div>
	</div>
	<center>
	<div style="padding: 20px;">
		<a class="button" id=resetButton>RESET SCORE</a></br></br>
	</div>
	</center>
</div>
<div class="keyboard" style="height: 0">&nbsp;</div>
