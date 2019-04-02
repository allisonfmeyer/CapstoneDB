var selectedSong = "";

var twinkle = "T: Twinkle Twinkle Little Star\n" +
      "M: 4/4\n" +
      "L: 1/4\n" +
      "R: \n" +
      "K: Dmaj\n" +
      "#D D A A|B B A2|G G F F|E E D2|\n" +
      "A A G G|F F E2|A A G G|F F E2|\n" +
      "D D A A|B B A2|G G F F|E E D2|]\n";

var lightlyrow = "T: Lightly Row\n" +
      "M: 4/4\n" +
      "L: 1/4\n" +
      "R: \n" +
      "K: Amaj\n" +
      "#e c c2|d B B2|A B c d|e e e2|\n" +
      "e c c c|d B B B|A c e e|c c c2|\n" +
      "B B B B|B c d2|c c c c|c d e2|\n" +
      "e c c c|d B B B|A c e e|c c c2|]\n";

var songOfTheWind = "T: Song of the Wind\n" +
      "M: 2/4\n" +
      "L: 1/8\n" +
      "R: \n" +
      "K: Amaj\n" +
      "#AB cd|ee ee|fd af|e2 z2|\n" +
      "fd af|e2 z2|ed dd|dc cc|\n" +
      "cB BB|Ac e2|ed dd|dc cc|\n" +
      "cB BB|A2 z2|]\n";

function loadMusic(song) {
  alert(song);
  return 'home'
  //selectedSong = song;
  //return false;
}

/**
  Called when button pressed to go to play page.
  Checks to ensure piece of music is selected.
**/
function badPlayMusic() {
  alert("No song selected!");
  return 'logged_home_init'
  /**
  if (selectedSong == "") {
    alert("No song selected!");
    return 'logged_home'
  }
  else {
    window.name=selectedSong;
    return 'play'
  }**/
}

function saveMusic() {
  if (selectedSong == "") {
    alert("No song selected!")
  }
}

/**
  Call to results page
**/
function getResults() {
  window.name=selectedSong;
  return 'results'
}

function compareSongs(song1, song2) {
  s1 = song1.substring(song1.indexOf("#")+1);
  s2 = song2.substring(song2.indexOf("#")+1);
  alert("s1: " + s1);
  alert("s2: " + s2);
  return false;
}

/** 
  This function adds new line characters to song string since 
  new line characters cause errors when passing from python
  -> html as variables
 **/
function addNewLines(song) {
  return song.replace(/n/g, "\n");
}

/**
  This function takes in the different parts of the python ABCSong
  model and turn them into a js-readable string. It also adds the
  new-line characters to the song to create proper breaks in music.
**/
function makeABCString(title, time_sig, length, key, song) {
  t = "T: " + title + "\n";
  m = "M: " + time_sig + "\n";
  l = "L: " + length + "\n";
  r = "R: \n";
  k = "K: " + key + "\n";
  s = addNewLines(song);
  return t + m + l + r + k + s;
}