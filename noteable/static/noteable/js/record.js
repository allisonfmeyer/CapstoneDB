//webkitURL is deprecated but nevertheless
URL = window.URL || window.webkitURL;

var gumStream; 						//stream from getUserMedia()
var rec; 							//Recorder.js object
var input; 							//MediaStreamAudioSourceNode we'll be recording

// shim for AudioContext when it's not avb. 
var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext //audio context to help us record

var title = document.getElementById("title_input");
var tempo = document.getElementById("tempo_input");
var recordButton = document.getElementById("recordButton");
var stopButton = document.getElementById("stopButton");
var pauseButton = document.getElementById("pauseButton");

//add events to those 2 buttons
recordButton.addEventListener("click", startRecording);
stopButton.addEventListener("click", stopRecording);
pauseButton.addEventListener("click", pauseRecording);

function getCSRFToken() {
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++) {
        c = cookies[i].trim();
        if (c.startsWith("csrftoken=")) {
            return c.substring("csrftoken=".length, c.length);
        }
    }
    return "unknown";
}

function updateRecording(response) {
	//console.log(response)
	try {
		var latest = document.getElementById("latestRec");
		var latestTempo = document.getElementById("latestTempo");
		latest.innerHTML = "";
		latestTempo.innerHTML = "";
	}
	catch {
		var latest2 = document.getElementById("latestRec2");
		latest2.innerHTML = "";
		latest2 = $(latest2);
	}
	var recording = response[0]["fields"]["recording"];
	var url = response[1]["fields"]["title"];
	var new_title = response[0]["fields"]["title"];
	var new_tempo = response[0]["fields"]["tempo"];

	try {
		latest.innerHTML = "Latest Recording: <a href="+url+">"+new_title+"</a>";
		latestTempo.innerHTML = "<small>(Tempo: "+new_tempo+")</small>"
		// Reset form inputs
		title.value = ""
		tempo.value = 100
	}
	catch {
		latest2.html(`Latest Recording: <a href=${url}>${new_title}</a> <small>(Tempo: ${new_tempo})</small> <a class="btn btn=outline-secondary btn-sm" onclick="location.href='{% url 'results' %}'">Results</a>`);
	}
}

function upload(blob){
	
    var req = new XMLHttpRequest();
    req.onreadystatechange = function() {
        if (req.readyState != 4) return;
        if (req.status != 200) return;
        var response = JSON.parse(req.responseText);
        if (Array.isArray(response)) {
            updateRecording(response);
        } else {
            displayError(response.error);
        }
    }
    var data = new FormData();
    data.append('recording', blob, "latestRecording.wav");
    data.append('title', title.value);
    data.append('tempo', tempo.value);
    data.append("csrfmiddlewaretoken",getCSRFToken());
    req.open("POST", "/noteable/upload", true);
    req.send(data)
}

function startRecording() {
	// Only start recording if input a title
	if (title.value == '') {
		alert('Enter a title!');
		return
	}
	console.log("recordButton clicked");

	/*
		Simple constraints object, for more advanced audio features see
		https://addpipe.com/blog/audio-constraints-getusermedia/
	*/
    
    var constraints = { audio: true, video:false }

 	/*
    	Disable the record button until we get a success or fail from getUserMedia() 
	*/

	recordButton.disabled = true;
	stopButton.disabled = false;
	pauseButton.disabled = false

	/*
    	We're using the standard promise based getUserMedia() 
    	https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia
	*/

	navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
		console.log("getUserMedia() success, stream created, initializing Recorder.js ...");

		/*
			create an audio context after getUserMedia is called
			sampleRate might change after getUserMedia is called, like it does on macOS when recording through AirPods
			the sampleRate defaults to the one set in your OS for your playback device

		*/
		audioContext = new AudioContext();

		/*  assign to gumStream for later use  */
		gumStream = stream;
		
		/* use the stream */
		input = audioContext.createMediaStreamSource(stream);

		/* 
			Create the Recorder object and configure to record mono sound (1 channel)
			Recording 2 channels  will double the file size
		*/
		rec = new Recorder(input,{numChannels:1})

		//start the recording process
		rec.record()

		console.log("Recording started");

	}).catch(function(err) {
	  	//enable the record button if getUserMedia() fails
    	recordButton.disabled = false;
    	stopButton.disabled = true;
    	pauseButton.disabled = true
	});
}

function pauseRecording(){
	console.log("pauseButton clicked rec.recording=",rec.recording );
	if (rec.recording){
		//pause
		rec.stop();
		pauseButton.innerHTML="Resume";
	}else{
		//resume
		rec.record()
		pauseButton.innerHTML="Pause";

	}
}

function stopRecording() {
	console.log("stopButton clicked");

	//disable the stop button, enable the record too allow for new recordings
	stopButton.disabled = true;
	recordButton.disabled = false;
	pauseButton.disabled = true;

	//reset button just in case the recording is stopped while paused
	pauseButton.innerHTML="Pause";
	
	//tell the recorder to stop the recording
	rec.stop();

	//stop microphone access
	gumStream.getAudioTracks()[0].stop();

	//create the wav blob and pass it on to createDownloadLink
	rec.exportWAV(upload)
}