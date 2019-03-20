<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="utf-8">
	<meta http-equiv="x-ua-compatible" content="ie=edge">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<link rel="icon" href="favicon.ico" type="image/x-icon"/>
	<title>abcjs: Basic Demo</title>
	<script src="{% static 'noteable/abcjs_basic_5.6.7-min.js' %}" type="text/javascript"></script>
	<script type="text/javascript">
		var abc = "T: Cooley's\n" +
			"M: 4/4\n" +
			"L: 1/8\n" +
			"R: reel\n" +
			"K: Emin\n" +
			"|:D2|EB{c}BA B2 EB|~B2 AB dBAG|FDAD BDAD|FDAD dAFD|\n" +
			"EBBA B2 EB|B2 AB defg|afe^c dBAF|DEFD E2:|\n" +
			"|:gf|eB B2 efge|eB B2 gedB|A2 FA DAFA|A2 FA defg|\n" +
			"eB B2 eBgB|eB B2 defg|afe^c dBAF|DEFD E2:|";

		function load() {
			ABCJS.renderAbc("paper", abc);
		}

	</script>
</head>
<body onload="load()">

<div id="paper"></div>
</body>
</html>