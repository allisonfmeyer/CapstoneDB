/**
  Called when button pressed to go to play page
  before a song is selected.
**/
function badPlayMusic() {
  alert("No song selected!");
  return 'logged_home_init'
}

/**
  Called when button pressed to save music
  before a song is selected.
**/
function badSaveMusic() {
  alert("No song selected!")
  return 'logged_home_init'
}

/** 
  This function adds new line characters to song string since 
  new line characters cause errors when passing from python
  -> html as variables
 **/
function addNewLines(song) {
  //return song.replace("|n", "|\n");
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
  stave = "%%staves {(OrigPiece) (PlayedPiece)} \n"
  v1 = "V:OrigPiece clef=treble \n" 
  v2 = "V:PlayedPiece clef=treble \n"
  k = "K: " + key + "\n";
  s = addNewLines(song);
  console.log(t + m + l + r + stave + v1 + v2 + k + s)
  return (t + m + l + r + stave + v1 + v2 + k + s);
}