<?php
function sendToHeatboc($cmd)
{
	$ch = curl_init("http://localhost:8000/$cmd");
	curl_setopt($ch, CURLOPT_HEADER, 0);
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

	$out = curl_exec($ch);
	curl_close($ch);
	return $out;
}
?>
