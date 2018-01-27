<?php
require_once('header.php');
?>
<style>
pre {
	font-size: 30px;
}
</style>
<script type="text/javascript" src="segment-display.js"></script>
<script type="text/javascript">
var display = new SegmentDisplay("display");
display.pattern         = "##:##";
display.cornerType      = 2;
display.displayType     = 7;
display.displayAngle    = 9;
display.digitHeight     = 20;
display.digitWidth      = 12;
display.digitDistance   = 2;
display.segmentWidth    = 3;
display.segmentDistance = 0.5;
display.colorOn         = "rgba(0, 0, 0, 0.9)";
display.colorOff        = "rgba(0, 0, 0, 0.1)";


function animate() {
	var time    = new Date();
	var hours   = time.getHours();
	var minutes = time.getMinutes();
	var seconds = time.getSeconds();
	var value   = ((minutes < 10) ? '0' : '') + minutes
		    + ':' + ((seconds < 10) ? '0' : '') + seconds;
	var value = "AB:DC";
	if (socket) {
		socket.send("getDisplay"); 
		socket.send("getLCD"); 
	}

	window.setTimeout('animate()', 1000);
}
function updateDisplay(val) {
	display.setValue(val);
}
function updateLCD(val) {
	$("#lcd").html("<center><pre>" + val + "</pre></center>");
}

var socket;

function init() {
	var host = "ws://192.168.1.51:9000/echobot"; // SET THIS TO YOUR SERVER
	try {
		socket = new WebSocket(host);
		log('WebSocket - status '+socket.readyState);
		socket.onopen    = function(msg) { 
							   log("Welcome - status "+this.readyState); 
						   };
		socket.onmessage = function(msg) { 
			if (msg.data.indexOf("display,") === 0) {
				updateDisplay(msg.data.replace("display,", ""));
			}
			if (msg.data.indexOf("lcd,") === 0) {
				updateLCD(msg.data.replace("lcd,", ""));
			}
						   };
		socket.onclose   = function(msg) { 
							   log("Disconnected - status "+this.readyState); 
						   };
	}
	catch(ex){ 
		log(ex); 
	}
	$("#msg").focus();
}

function send(){
	var msg;
	msg = $("#msg").val();
	if(!msg) { 
		alert("Message can not be empty"); 
		return; 
	}
	//txt.value="";
	//txt.focus();
	try { 
		socket.send(msg); 
		log('Sent: '+msg); 
	} catch(ex) { 
		log(ex); 
	}
}
function quit(){
	if (socket != null) {
		log("Goodbye!");
		socket.close();
		socket=null;
	}
}

function reconnect() {
	quit();
	init();
}

// Utilities
function log(msg){ $("#log").innerHTML+="<br>"+msg; }
function onkey(event){ if(event.keyCode==13){ send(); } }

function openMe(url)
{
        $.get(url, function( data ) {
                window.location.reload();
        });
}

$(document).ready(function() {
	animate();
	reconnect();
	$(".button").button();
	$("#pauseInterval").on('vclick', function () {
                openMe('api.php?action=keypress&value=5');
        });
});
</script>
<div data-role="page">
	<div data-role="header">
          <a href="index.php" class="ui-btn ui-btn-left ui-corner-all ui-shadow ui-icon-home ui-btn-icon-left">Home</a>
          <h1>Display</h1>
        </div>
<?php require_once('mode.php'); ?>
	<div style="padding: 20px;">
		<center><canvas id="display" width="320" height="150"></canvas></center>
	</div>
	<div style="padding: 20px;">
		<center><div id="lcd" style="background-color:#ebebeb;width: 325;height: 130;border: 1px solid black;"></div></center>
	</div>
	<div style="padding: 20px;">
                <center><a class="button" id=pauseInterval>Pause Interval</a></center>
        </div>
</div>
