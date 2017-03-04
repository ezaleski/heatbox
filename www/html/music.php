<?php
require_once('header.php');
require_once('mongo.php');
?>
<script type="text/javascript">
function openMe(url)
{
	$.get(url, function( data ) {
	});
}
$( document ).ready(function() {
	$("#setButton").click(function() {
		sendIt("set");
	});
	$("#countDownButton").click(function() {
		sendIt("countDown");
	});
	$("#musiclist").listview();
	$(".musicButton").button();
});
</script>
<div data-role="page">
	<div data-role="header">
	  <a href="index.php" class="ui-btn ui-btn-left ui-corner-all ui-shadow ui-icon-home ui-btn-icon-left">Home</a>
	  <h1>Music</h1>
	</div>
<?php require_once('mode.php'); ?>
	<div style="padding: 20px;">
		<a class="musicButton" id=playButton href="javascript:openMe('api.php?action=music&value=play');">Play</a>
		<a class="musicButton" id=stopButton href="javascript:openMe('api.php?action=music&value=stop');">Stop</a>
		<a class="musicButton" id=upButton href="javascript:openMe('api.php?action=music&value=volup');">Vol +</a>
		<a class="musicButton" id=downButton href="javascript:openMe('api.php?action=music&value=voldown');">Vol -</a>
		</br></br>
		<ul id="musiclist" data-role="listview" >
<?php
	$cursor = $music->find(array());
	foreach ($cursor as $doc) {
		$name = $doc['name'];
		$link = urlencode($doc['link']);
		?><li><a href="javascript:openMe('api.php?action=music&value=<?php echo $link; ?>');"><?php echo $name; ?></a></li><?php
	}
?>
		</ul>
	</div>
</div>
