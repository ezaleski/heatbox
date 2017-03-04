<?php
require_once('header.php');
?>
<script type="text/javascript">
function sendIt(action)
{
	var val = $("#twochar").val();
	$.getJSON( "api.php?action=" + action + "&value=" + val, function( data ) {
		//alert(JSON.stringify(data));
	});
}
function sendIt2(action)
{
	var val = $("#minutes").val();
	var val2 = $("#seconds").val();
	$.getJSON( "api.php?action=" + action + "&value=" + val + "&value2=" + val2, function( data ) {
		//alert(JSON.stringify(data));
	});
}
$( document ).ready(function() {
	$("#setButton").click(function() {
		sendIt("set");
	});
	$("#countDownButton").click(function() {
		sendIt2("countDown");
	});
});
</script>
<div data-role="page">
	<div data-role="header">
          <a href="index.php" class="ui-btn ui-btn-left ui-corner-all ui-shadow ui-icon-home ui-btn-icon-left">Home</a>
          <h1>Manual Entry</h1>
        </div>
<?php require_once('mode.php'); ?>
	<div style="padding: 20px;">
		<div data-role="fieldcontain" class="ui-hide-label">
			<label for="twochar">2 Character Value:</label>
			<input type="text" name="twochar" id="twochar" value="" placeholder="2 Character Value" data-theme="a"/><br>
			<input id="setButton" type="button" value="Set" data-theme="a">
			<br>
			<br>
			<input type="text" id="minutes" value="" placeholder="Minutes" data-theme="a"/>&nbsp;&nbsp;
			<input type="text" id="seconds" value="" placeholder="Seconds" data-theme="a"/><br>

			<input id="countDownButton" type="button" value="Count Down" data-theme="a">
		</div>
	</div>
</div>
