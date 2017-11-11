#!/usr/bin/php
<?php

require_once('./websockets.php');

class echoServer extends WebSocketServer {
    
  protected function process ($user, $message) {
	if ($message == "getDisplay") {
		$x = file_get_contents("/tmp/display.txt");
		$this->send($user,"display,".$x);
	}
	if ($message == "getLCD") {
		$x = file_get_contents("/tmp/lcd.txt");
		$this->send($user,"lcd,".$x);
	}
  }
  
  protected function connected ($user) {
    // Do nothing: This is just an echo server, there's no need to track the user.
    // However, if we did care about the users, we would probably have a cookie to
    // parse at this step, would be looking them up in permanent storage, etc.
  }
  
  protected function closed ($user) {
    // Do nothing: This is where cleanup would go, in case the user had any sort of
    // open files or other objects associated with them.  This runs after the socket 
    // has been closed, so there is no need to clean up the socket itself here.
  }
}

$echo = new echoServer("0.0.0.0","9000");

try {
  $echo->run();
}
catch (Exception $e) {
  $echo->stdout($e->getMessage());
}
