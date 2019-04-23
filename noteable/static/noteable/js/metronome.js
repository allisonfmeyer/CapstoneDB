window.AudioContext = window.AudioContext || window.webkitAudioContext;
var context = new AudioContext();
var timer, noteCount, counting, accentPitch = 380, offBeatPitch = 200;
var delta = 0;
var curTime = 0.0;

var recordButton = document.getElementById("recordButton");
var stopButton = document.getElementById("stopButton");
var pauseButton = document.getElementById("pauseButton");
var title = document.getElementById("title_input");

//add events to those 2 buttons
recordButton.addEventListener("click", startRecording);
stopButton.addEventListener("click", stopRecording);
pauseButton.addEventListener("click", pauseRecording);

// Load up dots on pageload
$("document").ready(function() {
$("#ts-top").trigger("change");
$("header").fitText(1, { maxFontSize: "46px" });
});


/*
Scheduling Help by: https://www.html5rocks.com/en/tutorials/audio/scheduling/
*/
function schedule() {
while(curTime < context.currentTime + 0.1) {
  playNote(curTime);
  updateTime();
}
timer = window.setTimeout(schedule, 0.1);
}

function updateTime() {
curTime += 60.0 / parseInt($("#tempo_input").val(), 10);
noteCount++;
}

/* Play note on a delayed interval of t */
function playNote(t) {
    var note = context.createOscillator();

    if(noteCount == parseInt($("#ts-top").val(), 10) )
      noteCount = 0;

    if( $(".counter .dot").eq(noteCount).hasClass("active") )
      note.frequency.value = accentPitch;
    else
      note.frequency.value = offBeatPitch;

    note.start(t);
    note.stop(t + 0.05);

    $(".counter .dot").attr("style", "");

    $(".counter .dot").eq(noteCount).css({
      transform: "translateY(-10px)",
      background: "#F75454"
    });
}

/* Activate dots for accents */
$(document).on("click", ".counter .dot", function() {
  $(this).toggleClass("active");
});

$(".options-btn").click(function() {
$(".options").toggleClass("options-active");
});

/* Add dots when time signature is changed */
$("#ts-top, .ts-bottom").on("change", function() {
  var _counter = $(".counter");
  _counter.html("");

  for(var i = 0; i < parseInt($("#ts-top").val(), 10); i++)
  {
    var temp = document.createElement("div");
    temp.className = "dot";

    if(i === 0)
      temp.className += " active";

    _counter.append( temp );
  }
});

function startRecording() {
  if (title.value == '') {
    return
  }
  curTime = context.currentTime;
  noteCount = parseInt($("#ts-top").val(), 10);
  schedule();
}

function pauseRecording() {
  if (pauseButton.innerHTML == "Resume"){
    //pause
    counting = false;
    window.clearInterval(timer);
    $(".counter .dot").attr("style", "");
  }
  else{
    //resume
    curTime = context.currentTime;
    noteCount = parseInt($("#ts-top").val(), 10);
    schedule();
  }
}

function stopRecording() {
  counting = false;
  window.clearInterval(timer);
  $(".counter .dot").attr("style", "");
}