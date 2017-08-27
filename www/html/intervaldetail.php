<?php
require_once('header.php');
require_once('mongo.php');
?>
<style>
.formDiv {
	padding-bottom: 10px;
}
td {
	padding: 10px;
}
#tabledata {
	padding-top: 20px;
}
table { 
    border-spacing: 0px;
    border-collapse: separate;
}
.formInput {
	background-color: #eeeeee;
	padding: 5px;
	margin-bottom: 5px;
}
.blur-filter {
    -webkit-filter: blur(2px);
    -moz-filter: blur(2px);
    -o-filter: blur(2px);
    -ms-filter: blur(2px);
    filter: blur(2px);
}
</style>
<script type="text/javascript">
var intervalId = '';
var isEdit = false;
var intervalObj = [];
var intervalName = "";
var numSteps = 0;
var editStepFlag = false;
var currentEditStep = -1;
<?php
if (isset($_GET["intervalId"])) {
	$intervalId = $_GET['intervalId'];
	print "intervalId = '".$intervalId."';\n";
	print "isEdit = true;\n";	
	$intervalData = getIntervalData($intervalId);
	$iData = $intervalData['intervalData'];
	print "intervalObj = ".json_encode($iData['steps']).";\n"; 
	print "intervalName = '".$iData['name']."';\n";
	print "numSteps = ".count($iData['steps']).";\n";
}
?>
function openMe(url)
{
	$.get(url, function( data ) {
	});
}


function blurBackground()
{
    $.mobile.pageContainer.pagecontainer( "getActivePage" ).not($("#stepDetail")).addClass( "blur-filter" );
}
function unblurBackground()
{
    $(".blur-filter").removeClass( "blur-filter" );
}
function addStep()
{
	beforeStep = $("#select-action-beginning").val()
	beforeStepSongId = ""
	beforeStepSong = ""
	beforeStepTimer = ""
	if (beforeStep == "PLAYSOUND") {
		beforeStepSongId = $("#select-sound-beginning option:selected").val();
		beforeStepSong = $("#select-sound-beginning option:selected").text();
	}
	if (beforeStep == "TIMER") {
		beforeStepTimer = $("#atBeginning").val();
	}
	step = $("#timerFor").val()
	if (step == "") {
		alert('You must provide a timer interval.');
		return;
	}
	afterStep = $("#select-action-end").val()
	afterStepSong = ""
	afterStepSongId = ""
	if (afterStep == "PLAYSOUND") {
		afterStepSongId = $("#select-sound-end option:selected").val();
		afterStepSong = $("#select-sound-end option:selected").text();
	}
	var o = {};
	o["beforeStep"] = beforeStep;
	o["beforeStepSongId"] = beforeStepSongId;
	o["beforeStepSong"] = beforeStepSong;
	o["beforeStepTimer"] = beforeStepTimer;
	o["step"] = step;
	o["afterStep"] = afterStep;
	o["afterStepSong"] = afterStepSong;
	o["afterStepSongId"] = afterStepSongId;
	if (editStepFlag) {
		editStepFlag = false;
		intervalObj[currentEditStep] = o;
	}
	else {
		intervalObj.push(o);
		numSteps++
	}
/*
	intervalObj[numSteps] = [];
	intervalObj[numSteps]["beforeStep"] = beforeStep;
	intervalObj[numSteps]["beforeStepSongId"] = beforeStepSongId;
	intervalObj[numSteps]["beforeStepSong"] = beforeStepSong;
	intervalObj[numSteps]["beforeStepTimer"] = beforeStepTimer;
	intervalObj[numSteps]["step"] = step;
	intervalObj[numSteps]["afterStep"] = afterStep;
	intervalObj[numSteps]["afterStepSong"] = afterStepSong;
	intervalObj[numSteps]["afterStepSongId"] = afterStepSongId;
	intervalObj[numSteps]["afterStepTimer"] = afterStepTimer;
*/
	$("#stepDetail").popup('close');
	renderTable();	
}
function renderTable()
{
	var table = $.makeTable(intervalObj);
	$("#tabledata").html(table);
	$(".intervalEditButton").button();
	$(".intervalButton").button();
}

function addStepOpen()
{
	editStepFlag = false;
	$("#addStep").text("Add Step");	
	$("#stepDetail").popup('open');
}
function editStep(stepNumber)
{
	editStepFlag = true;
	currentEditStep = stepNumber;

	var o = intervalObj[stepNumber];
	$("#select-action-beginning").val(o['beforeStep']);
	$("#select-action-beginning").change();
	$("#select-sound-beginning").val(o['beforeStepSongId']);
	$("#atBeginning").val(o['beforeStepTimer']);

	$("#timerFor").val(o['step']);

	$("#select-action-end").val(o['afterStep']);
	$("#select-action-end").change();
	$("#select-sound-end").val(o['afterStepSongId']);

	$("#addStep").text("Edit Step");	
	$("#stepDetail").popup('open');
}
function moveUp(stepNumber)
{
	if (intervalObj[stepNumber-1]) {
		var o = intervalObj[stepNumber-1];
		var o2 = intervalObj[stepNumber];
		intervalObj[stepNumber-1] = o2;
		intervalObj[stepNumber] = o;
	}
	renderTable();
}
function moveDown(stepNumber)
{
	if (intervalObj[stepNumber+1]) {
		var o = intervalObj[stepNumber+1];
		var o2 = intervalObj[stepNumber];
		intervalObj[stepNumber+1] = o2;
		intervalObj[stepNumber] = o;
	}
	renderTable();
}
$.makeTable = function (mydata) {
    var table = $('<table width=100% border=1>');
    var tblHeader = "<tr>";
    tblHeader += "<td>Before Step</td>";
    tblHeader += "<td>Timer</td>";
    tblHeader += "<td>After Step</td>";
    tblHeader += "<td></td>";
    tblHeader += "</tr>";
    $(tblHeader).appendTo(table);
    var stepNumber = 0;
    $.each(mydata, function (index, value) {
        var TableRow = "<tr>";
	var bs = value["beforeStep"];
	if (value["beforeStepSong"] != "") {
		bs = bs + " - " + value["beforeStepSong"];
	}
	if (value["beforeStepTimer"] != "") {
		bs = bs + " - " + value["beforeStepTimer"];
	}
	var as = value["afterStep"];
	if (value["afterStepSong"] != "") {
		as = as + " - " + value["afterStepSong"];
	}
	TableRow += "<td>" + bs + "</td>";
	TableRow += "<td>" + value["step"] + "</td>";
	TableRow += "<td>" + as + "</td>";
	TableRow += "<td>";
	TableRow += "<a href='javascript:editStep(" + stepNumber + ");' class='intervalEditButton'>Edit</a>";
	TableRow += "<a href='javascript:moveUp(" + stepNumber + ");' class='intervalButton'>Move Up</a>";
	TableRow += "<a href='javascript:moveDown(" + stepNumber + ");' class='intervalButton'>Move Down</a>";
	TableRow += "</td>";
        TableRow += "</tr>";
	stepNumber++;
        $(table).append(TableRow);
    });
    return ($(table));
};

$( document ).ready(function() {
	$("#intervalsteplist").listview();
	$(".intervalButton").button();
	$(".intervalStepButton").button();
	$("#stepDetail").popup();
	$(".timeInput").mask("99:99");

	$("#soundSelectorDivBeginning").hide();	
	$("#countdownTimerDivBeginning").hide();	
	$("#soundSelectorDivEnd").hide();	
	$("#countdownTimerDivEnd").hide();	
	$("#saveButton").click(function() {
		var intervalName = $("#intervalName").val();
		if (intervalName == "") {
			alert('You must provide an interval name');
			return;
		}
		if (Object.keys(intervalObj).length <= 0) {
			alert('You have to add at least one step');
			return;
		}	
		var iObj = {'name' : intervalName, 'steps' : intervalObj};
		dataString = JSON.stringify(iObj);

		var postData = {action: "saveInterval", intervalData:dataString};
		if (intervalId != '') {
			postData['intervalId'] = intervalId;
		}
		$.ajax({
			    type: "POST",
			    dataType: "json",
			    url: "api.php",
			    data: postData,
			    success: function(data){
				window.location.href = "intervals.php";
			    },
			    error: function(e){
				console.log(e.message);
			    }
		    });
	});
	$("#addStep").click(function() {
		addStep();
	});

	$(document).on("popupafteropen", "#stepDetail",function( event, ui ) {
		blurBackground();
	});  
	$(document).on("popupafterclose", "#stepDetail",function( event, ui ) {
		unblurBackground();
	});  
	$('select').on('change', function() {
		if (this.id == "select-action-beginning") {
			val = this.value;
			if (val == "NONE") {
				$("#soundSelectorDivBeginning").hide();	
				$("#countdownTimerDivBeginning").hide();	
			}
			if (val == "DISPLAYINTERVALSLEFT") {
				$("#soundSelectorDivBeginning").hide();	
				$("#countdownTimerDivBeginning").hide();	
			}
			if (val == "PLAYSOUND") {
				$("#soundSelectorDivBeginning").show();	
				$("#countdownTimerDivBeginning").hide();	
			}
			if (val == "TIMER") {
				$("#soundSelectorDivBeginning").hide();	
				$("#countdownTimerDivBeginning").show();	
			}
		}
		if (this.id == "select-action-end") {
			val = this.value;
			if (val == "NONE") {
				$("#soundSelectorDivEnd").hide();	
				$("#countdownTimerDivEnd").hide();	
			}
			if (val == "DISPLAYINTERVALSLEFT") {
				$("#soundSelectorDivBeginning").hide();	
				$("#countdownTimerDivBeginning").hide();	
			}
			if (val == "PLAYSOUND") {
				$("#soundSelectorDivEnd").show();	
				$("#countdownTimerDivEnd").hide();	
			}
		}
	});
	if (intervalId != '') {
		$("#intervalName").val(intervalName);
		renderTable();
	}
});
</script>
<div data-role="page">
	<div data-role="header">
	  <a href="index.php" class="ui-btn ui-btn-left ui-corner-all ui-shadow ui-icon-home ui-btn-icon-left">Home</a>
	  <h1>Add/Edit Interval</h1>
	</div>
<?php require_once('mode.php'); ?>
	<div style="padding: 20px;">
		<div align=right>
		<a href="#saveMe" id="saveButton" class="intervalStepButton">Save</a>
		</div>
		<div>
			Name : <input type=text id=intervalName>
		</div>
		<div>
			Steps : <a href="javascript:addStepOpen()" id="intervalStepAddButton" data-rel="popup" data-position-to="window" class="intervalStepButton" data-transition="pop">Add Step +</a>
		</div>
		<div id="tabledata">
		</div>
		<ul id="intervalsteplist" data-role="listview" >
<?php
	$cursor = $intervalsteps->find(array());
	foreach ($cursor as $doc) {
		$name = $doc['name'];
		$id = urlencode($doc['_id']);
		?><li><?php echo $name; ?><div align=right><a class=intervalExecuteButton id="<?php echo $id; ?>">Start</a>&nbsp;&nbsp;&nbsp;<a class=intervalEditButton id="<?php echo $id; ?>">Edit</a></li><?php
	}
?>
		</ul>
	</div>
</div>
<div data-role="popup" id="stepDetail" data-theme="a" class="ui-corner-all" data-overlay-theme="a" title="Enter Interval Step Info" data-dismissible="false">
<a href="#" data-rel="back" data-role="button" data-theme="b" data-icon="delete" data-iconpos="notext" class="ui-btn-right ui-icon-delete ui-nosvg"><div style="background: white;border-radius: 50%;padding: 5px;border-color: black;border-style: solid;"><img src="images/icons-png/delete-black.png"></div></a>
    <form>
	<div style="padding:10px 20px;">
	<div class="ui-field-contain formDiv">
	    <b>At Beginning:</b>
		<select class="intervalSelect ui-select ui-btn" name="select-action-beginning" id="select-action-beginning">
			<option value="NONE">Do Nothing</option>
			<option value="PLAYSOUND">Play a sound</option>
			<option value="DISPLAYINTERVALSLEFT">Display Intervals Left</option>
			<option value="TIMER">Countdown Timer</option>
		</select>
		<div id="soundSelectorDivBeginning" style="display:block;">
			<select class="intervalSelect ui-select ui-btn" name="select-sound-beginning" id="select-sound-beginning">
				<?php
					foreach (getSounds() as $sound) {
				?>
						<option value="<?php echo $sound["id"];?>"><?php echo $sound["name"];?></option>
				<?php
					}
				?>
			</select>
		</div>
		<div id="countdownTimerDivBeginning" style="display:none;">
		<input class="formInput timeInput" type="text" id="atBeginning" value="" placeholder="MM:SS" data-theme="a"><br>
		</div>
	</div>
	<div class="ui-field-contain formDiv">
	    <b>Timer For:</b>
	    <input class="formInput timeInput" type="text" id="timerFor" value="" placeholder="MM:SS" data-theme="a"><br>
	</div>
	<div class="ui-field-contain formDiv">
	    <b>At End:</b>
		<select class="intervalSelect ui-select ui-btn" name="select-action-end" id="select-action-end">
			<option value="NONE">Do Nothing</option>
			<option value="PLAYSOUND">Play a sound</option>
			<option value="DISPLAYINTERVALSLEFT">Display Intervals Left</option>
		</select>
		<div id="soundSelectorDivEnd" style="display:block;">
			<select class="intervalSelect ui-select ui-btn" name="select-sound-end" id="select-sound-end">
				<?php
					foreach (getSounds() as $sound) {
				?>
						<option value="<?php echo $sound["id"];?>"><?php echo $sound["name"];?></option>
				<?php
					}
				?>
			</select>
		</div>
	</div>
	<br>
        <a href="#" class="intervalButton" id="addStep">Add Step</a>
    </form>
</div>
