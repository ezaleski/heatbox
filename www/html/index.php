<?php require_once('header.php'); ?>
<script type="text/javascript">
$( document ).ready(function() {
        $("#homescreen").listview();
});
</script>

<div data-role="page">
	<div data-role="header">
          <a href="index.php" class="ui-btn ui-btn-left ui-corner-all ui-shadow ui-icon-home ui-btn-icon-left">Home</a>
          <h1>Home</h1>
        </div>
<?php require_once('mode.php'); ?>
	<ul id="homescreen" data-role="listview">
		<li><a rel="external" href="display.php">Display</a></li>
		<li><a rel="external" href="manualentry.php">Manual Entry</a></li>
		<li><a rel="external" href="scoreboard.php">Scoreboard</a></li>
		<li><a rel="external" href="intervals.php">Intervals</a></li>
		<li><a rel="external" href="music.php">Music</a></li>
		<li><a rel="external" href="tools.php">Tools</a></li>
	</ul>
</div>

