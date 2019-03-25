var selectedSong = "";

var twinkle = "T: Twinkle Twinkle Little Star\n" +
      "M: 4/4\n" +
      "L: 1/4\n" +
      "R: \n" +
      "K: Dmaj\n" +
      "D D A A|B B A2|G G F F|E E D2|\n" +
      "A A G G|F F E2|A A G G|F F E2|\n" +
      "D D A A|B B A2|G G F F|E E D2|]\n";

var lightlyrow = "T: Lightly Row\n" +
      "M: 4/4\n" +
      "L: 1/4\n" +
      "R: \n" +
      "K: Amaj\n" +
      "e c c2|d B B2|A B c d|e e e2|\n" +
      "e c c c|d B B B|A c e e|c c c2|\n" +
      "B B B B|B c d2|c c c c|c d e2|\n" +
      "e c c c|d B B B|A c e e|c c c2|]\n";

var songOfTheWind = "T: Song of the Wind\n" +
      "M: 2/4\n" +
      "L: 1/8\n" +
      "R: \n" +
      "K: Amaj\n" +
      "AB cd|ee ee|fd af|e2 z2|\n" +
      "fd af|e2 z2|ed dd|dc cc|\n" +
      "cB BB|Ac e2|ed dd|dc cc|\n" +
      "cB BB|A2 z2|]\n";

function loadMusic(song) {
  selectedSong = song;
  return false;
}

function playMusic() {
  if (selectedSong == "") {
    alert("No song selected!");
    return 'logged_home'
  }
  else {
    window.name=selectedSong;
    return 'play'
  }
}

function saveMusic() {
  if (selectedSong == "") {
    alert("No song selected!")
  }
}

function record() {
  document.getElementById('recordButton').value = "Stop";
  alert("Alert!");
  alert(document.getElementById('recordButton').value);
}
