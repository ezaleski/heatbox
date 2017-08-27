<?php
require_once('header.php');
require_once('mongo.php');
?>
<script type="text/javascript">
function openMe(url)
{
	$.get(url, function( data ) {
		window.location.href="intervals.php";
	});
}
$( document ).ready(function() {
	$(".ui-dialog").hide();
	$("#intervallist").listview();
	$(".intervalButton").button();
	$(".intervalExecuteButton").button();
	$(".intervalEditButton").button();
	$(".intervalExecuteButton").click(function() {
		id = $(this).attr("id");
		openMe("api.php?action=startInterval&intervalId=" + id);
	});
	$(".intervalEditButton").click(function() {
		id = $(this).attr("id");
		window.location.href="intervaldetail.php?intervalId=" + id;
	});
	$( document ).on( "swipeleft swiperight", "#intervallist li", function( event ) {
                var listitem = $( this ),
                    // These are the classnames used for the CSS transition
                    dir = event.type === "swipeleft" ? "left" : "right",
                    // Check if the browser supports the transform (3D) CSS transition
                    transition = $.support.cssTransform3d ? dir : false;
                    confirmAndDelete( listitem, transition );
            });
});
function confirmAndDelete( listitem, transition ) {
	areYouSure("Delete this item ?", listitem.attr('intervalName'), "YES", function() {
		url = 'api.php?action=deleteInterval&intervalId=' + listitem.attr('intervalId');
		$.get(url, function( data ) {
			window.location.reload();
		});
	});
}
function areYouSure(text1, text2, button, callback) {
	$("#sure .sure-1").text(text1);
	$("#sure .sure-2").text(text2);
	$("#sure .sure-do").unbind("click");
	$("#sure .sure-dont").unbind("click");
	$("#sure .sure-do").text(button).on("click", function() {
		callback();
		$(".ui-dialog").hide();
		$(this).off("click.sure");
	});
	$("#sure .sure-dont").text("No").on("click", function() {
		$(".ui-dialog").hide();
	});
	$("#sure").dialog();
	$(".ui-dialog").show();
}

</script>
<div data-role="page">
	<div data-role="header">
	  <a href="index.php" class="ui-btn ui-btn-left ui-corner-all ui-shadow ui-icon-home ui-btn-icon-left">Home</a>
	  <h1>Intervals</h1>
	</div>
<?php require_once('mode.php'); ?>
	<div style="padding: 20px;">
		<a class="intervalButton" data-ajax="false" id=newButton href="intervaldetail.php?action=add">Add New Interval +</a>
		</br></br>
		<ul id="intervallist" data-role="listview" >
<?php
	$cursor = $intervals->find(array());
	foreach ($cursor as $doc) {
		$name = $doc['intervalData']['name'];
		$id = urlencode($doc['intervalId']);
		?><li intervalId="<?php print $id; ?>" intervalName="<?php print $name;?>"><font size=5><?php echo $name; ?></font><span style="float: right;" align=right><a class=intervalExecuteButton id="<?php echo $id; ?>">Start</a>&nbsp;&nbsp;&nbsp;<a class=intervalEditButton id="<?php echo $id; ?>">Edit</a></span></li><?php
	}
?>
		</ul>
	</div>
	<div data-role="dialog" style="display: none;" id="sure" data-title="Are you sure?">
	  <div data-role="content">
	    <h3 class="sure-1">???</h3>
	    <p class="sure-2">???</p>
	    <button  class="sure-do" data-role="button" data-theme="b" data-rel="back">Yes</button>
	    <button  class="sure-dont" data-role="button" data-theme="b" data-rel="back">No</button>
	  </div>
	</div>
</div>
