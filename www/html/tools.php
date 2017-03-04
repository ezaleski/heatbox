<?php
require_once('header.php');
?>
<script type="text/javascript">
function openMe(url)
{
	$.get(url, function( data ) {
	});
}
$( document ).ready(function() {
	$("#toollist").listview();
	$(".toolButton").button();
});
</script>
<div data-role="page">
	<div data-role="header">
          <a href="index.php" class="ui-btn ui-btn-left ui-corner-all ui-shadow ui-icon-home ui-btn-icon-left">Home</a>
          <h1>Tools</h1>
        </div>
	<div style="padding: 20px;">
		<ul id="toollist" data-role="listview" >
			<li data-role="list-divider">Misc</li>
			<li><a href="javascript:openMe('api.php?action=strandtest&value=1');">Strandtest</a></li>
			<li><a href="javascript:openMe('api.php?action=strandteststop&value=1');">Strandtest Stop</a></li>
			<li><a href="javascript:openMe('api.php?action=clear&value=1');">Clear</a></li>
			<li><a href="javascript:openMe('api.php?action=startclock&value=1');">Start Clock</a></li>
			<li><a href="javascript:openMe('api.php?action=stopclock&value=1');">Stop Clock</a></li>
			<li><a href="javascript:openMe('api.php?action=hotspotup&value=1');">HotSpot Up</a></li>
			<li><a href="javascript:openMe('api.php?action=hotspotdown&value=1');">HotSpot Down</a></li>
			<li data-role="list-divider">Shutdown</li>
			<li><a href="javascript:openMe('api.php?action=turnoff&value=1');">Turn Off</a></li>
			<li><a href="javascript:openMe('api.php?action=shutdown&value=1');">Shutdown</a></li>
		</ul>
	</div>
</div>
