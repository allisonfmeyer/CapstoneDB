from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.files.storage import FileSystemStorage
from django.contrib.staticfiles.templatetags.staticfiles import static

from noteable.forms import LoginForm, RegistrationForm, RecordForm, SheetForm
from noteable.models import Record, ABCSong, Sheet
from noteable.audio import main
import os, subprocess
from subprocess import PIPE

# NOT USING YET
def upload(request):
 
    customHeader = request.META['HTTP_MYCUSTOMHEADER']
 
    # obviously handle correct naming of the file and place it somewhere like media/uploads/
    uploadedFile = open("recording.ogg", "wb")
    # the actual file is in request.body
    uploadedFile.write(request.body)
    uploadedFile.close()
    # put additional logic like creating a model instance or something like this here
    return HttpResponse(escape(repr(request)))
    
def home_page_action(request):
	return render(request, 'noteable/home.html', {})

def login_action(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = LoginForm()
        return render(request, 'noteable/login.html', context)

    # Creates a bound form from the request POST parameters and makes the 
    # form available in the request context dictionary.
    form = LoginForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'noteable/login.html', context)

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    login(request, new_user)
    return redirect(reverse('home'))

def logout_action(request):
    logout(request)
    return redirect(reverse('login'))

def register_action(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = RegistrationForm()
        return render(request, 'noteable/register.html', context)

    # Creates a bound form from the request POST parameters and makes the 
    # form available in the request context dictionary.
    form = RegistrationForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'noteable/register.html', context)

    # At this point, the form data is valid.  Register and login the user.
    new_user = User.objects.create_user(username=form.cleaned_data['username'], 
                                        password=form.cleaned_data['password1'],
                                        email=form.cleaned_data['email'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])
    
    new_user.save()

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password1'])

    login(request, new_user)
    return redirect(reverse('home'))

# Hard coded model object for the sample song 'Twinkle Twinkle Little Star'
def twinkleModel():
    model = ABCSong()
    model.title = "Twinkle Twinkle Little Star"
    model.time_sig = "4/4"
    model.length = "1/4"
    model.key = "Dmaj"
    model.song = "D D A A|B B A2|G G F F|E E D2|n A A G G|F F E2|A A G G|F F E2|n D D A A|B B A2|G G F F|E E D2|]n"
    return model

# Hard coded model object for the sample song 'Lightly Row'
def lightlyRowModel():
    model = ABCSong()
    model.title = "Lightly Row"
    model.time_sig = "4/4"
    model.length = "1/4"
    model.key = "Amaj"
    model.song = "e c c2|d B B2|A B c d|e e e2|n e c c c|d B B B|A c e e|c c c2|n B B B B|B c d2|c c c c|c d e2|n e c c c|d B B B|A c e e|c c c2|]n"
    return model

# Hard coded model object for the sample song 'Song of the Wind'
def songOfTheWindModel():
    model = ABCSong()
    model.title = "Song of the Wind"
    model.time_sig = "2/4"
    model.length = "1/8"
    model.key = "Amaj"
    model.song = "AB cd|ee ee|fd af|e2 z2|n fd af|e2 z2|ed dd|dc cc|n cB BB|Ac e2|ed dd|dc cc|n cB BB|A2 z2|]n"
    return model

'''
  This function is solely called to render the initial logged in page, before
  a user has selected a song to play.
'''
def logged_home_action_init(request):
    if request.method == 'POST':
        form = SheetForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # Get uploaded pdf and send to Audiveris for mxl conversion
            sheet = Sheet.objects.latest('uploaded_at')
            pdf = sheet.sheet
            #subprocess.call('cd audiveris', shell=True)
            subprocess.call('gradle run -PcmdLineArgs="-batch,-export,-output,media/mxl,--,media/'+str(pdf)+'"', shell=True)
            return render(request, 'noteable/logged_home_init.html', { 'form': SheetForm()})
    else:
        form = SheetForm()
    #sheet = Sheet.objects.latest('uploaded_at')
    return render(request, 'noteable/logged_home_init.html', { 'form': form })


    return render(request, 'noteable/logged_home_init.html', {})

'''
  This function is called every time a different song is selected but before a user
  has decided to begin recording. The chosen song is passed in as a parameter, initializing
  the flow of selected song data between views.
'''
def logged_home_action(request, chosen_song):
    song = getSongObject(chosen_song)
    # Set session parameter to song once song is selected to access in other views
    request.session['song'] = chosen_song
    return render(request, 'noteable/logged_home.html', { 'song': song })

'''
  This function takes a string of the song name and returns
  the corresponding ABCSong Model Object. This is called between
  views because Objects cannot be assigned to session keys. Super
  useful for hard-coded sample songs.
'''
def getSongObject(chosen_song):
    if chosen_song == 'twinkle':
        return twinkleModel()
    elif chosen_song == 'lightlyRow':
        return lightlyRowModel()
    elif chosen_song == 'songOfTheWind':
        return songOfTheWindModel()
    return None

'''
  This function renders the play url page. It retrieves the chosen song by calling
  the session parameter, then either loads a blank form or saves a posted form
  to the db containing an uploaded song model.
'''
def play_action(request):
    song = getSongObject(request.session.get('song', None))
    if request.method == 'POST':
        form = RecordForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            record = Record.objects.latest('uploaded_at')
            return render(request, 'noteable/play.html', { 'form': RecordForm(), 'record': record, 'song': song })
    else:
        form = RecordForm()
    record = Record.objects.latest('uploaded_at')
    return render(request, 'noteable/play.html', { 'form': form, 'record': record, 'song': song })

''' 
  This function recreates a song string, creating chords out of any discrepancies
  between song strings. It also creates an array of classes corresponding to
  discrepencies, to be passed to the css to style the notes in a red color.
'''
def compareSongs(song1, song2):
    curr_line = 0
    curr_meas = 0
    curr_note = -1
    note_values = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
    # ABCJs notation: _ for flat, ^ for sharp, = for natural
    accidentals = ['_', '^', '=']
    result_song = ""
    wrong_classes = []
    song2_index = 0
    for index in range(len(song1)):
        # Set line, measure, and note for currently evaluated note
        if song1[index].upper() in note_values:
            curr_note += 1
        elif song1[index] == "|":
            curr_meas += 1
            curr_note = -1
        elif song1[index] == "n":
            curr_line += 1
            curr_meas = 0
        # Don't crash if song2 is missing notes
        if song2_index <= len(song2)-1:
            # Build up the new song, creating chords for missed notes to display both
            if song1[index] == song2[song2_index]:
                result_song += song1[index]
                song2_index += 1
            else:
                if song1[index].upper() in note_values:
                    # Mismatched notes without accidentals
                    if song2[song2_index].upper() in note_values:
                        result_song += "[" + song1[index] + song2[song2_index] + "]"
                        curr_class = '.abcjs-l'+str(curr_line)+'.abcjs-m'+str(curr_meas)+'.abcjs-n'+str(curr_note)
                        wrong_classes.append(curr_class)
                        song2_index += 1
                    # Accidental in note on recorded song
                    elif song2[song2_index] in accidentals:
                        result_song += "[" + song1[index] + song2[song2_index] + song2[song2_index+1] + "]"
                        curr_class = '.abcjs-l'+str(curr_line)+'.abcjs-m'+str(curr_meas)+'.abcjs-n'+str(curr_note)
                        wrong_classes.append(curr_class)
                        song2_index += 2
                    # Song 2 ran out of notes but still needs to reach end of string
                    else:
                        result_song += song1[index]
                        curr_class = '.abcjs-l'+str(curr_line)+'.abcjs-m'+str(curr_meas)+'.abcjs-n'+str(curr_note)
                        wrong_classes.append(curr_class)
                        song2_index += 1
                else:
                    result_song += song1[index]
        # Mark all notes incorrect if song2 runs out early
        else:
            result_song += song1[index]
            if song1[index].upper() in note_values:
                curr_class = '.abcjs-l'+str(curr_line)+'.abcjs-m'+str(curr_meas)+'.abcjs-n'+str(curr_note)
                wrong_classes.append(curr_class)
    return (result_song, wrong_classes)

'''
  This function returns the color to be used to style the percent based
  on good, medium, or bad performance on a song.
'''
def percentage_color(percentage):
    if percentage >= 90:
        return "green"
    elif percentage >= 70:
        return "#FFD700"
    else:
        return "red"

''' 
  This function calculates the correctness percentage
  by analyzing the number of wrong_classes previously
  calculated in comparison to the total number of notes in a song.
'''
def percentage(song, wrong_classes):
    # Strips all whitespace, barlines, numbers, accids, and newline chars
    song = song.replace(" ", "")
    song = song.replace("|", "")
    song = song.replace("n", "")
    song = song.replace("_", "")
    song = song.replace("^", "")
    song = song.replace("=", "")
    # Strips all digits
    song = ''.join([i for i in song if not i.isdigit()])
    # Count number of chords
    num_chords = song.count("[")
    # Strip chord and end of song indicator
    song = song.replace("[", "")
    song = song.replace("]", "")
    total_notes = len(song) - num_chords
    return round(100*(1-len(wrong_classes)/total_notes))

'''
  This function is called to load the results page. Coordinates with back end
  functions to analyze discrepancies between the two songs, create an object
  string that can be sent to be displayed in js, and assigns necessary color
  according to percent correctness.
'''
def results_action(request):
    sheet_song = getSongObject(request.session.get('song', None))
    record = Record.objects.latest('uploaded_at')
    audio_song = main(record.recording, record.tempo, sheet_song.time_sig, debug=False)

    #Examples for demo!
    # 8 wrong notes (ok)
    #audio_song = "F F c c|B B c2|G G F F|G E D2|n A c G G|F F E2|A A B G|F F E2|n D D A A|B B A2|G G F F|E E D2|]n"
    #13 wrong notes (bad)
    #audio_song = "D D A A|B B A2|G G F F|E E D2|n A A G G|F F E2|A A G G|F F E2|n F F c c|d d c2|B B A A|G G D2|]n"

    # Update song to include any discrepencies between recording and sheet music as chords
    (result_song, wrong_classes) = compareSongs(sheet_song.song, audio_song)
    sheet_song.song = result_song

    perc = percentage(result_song, wrong_classes)
    perc_color = percentage_color(perc)
    return render(request, 'noteable/results.html', 
        { 'record': record, 'result_song': sheet_song, 'percentage': perc, 'perc_color': perc_color, 
        'classes': wrong_classes })

def account_action(request):
    return render(request, 'noteable/account.html', {})