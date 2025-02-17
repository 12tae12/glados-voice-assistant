import time
#!/usr/bin/python3
#	   _____ _           _____   ____   _____
#	  / ____| |         |  __ \ / __ \ / ____|
#	 | |  __| |     __ _| |  | | |  | | (___  
#	 | | |_ | |    / _` | |  | | |  | |\___ \ 
#	 | |__| | |___| (_| | |__| | |__| |____) |
#	  \_____|______\__,_|_____/ \____/|_____/ 
#___________________________________________________
#
#	Open source voice assistant by nerdaxic
#
#	Local TTS engine based on https://github.com/NeonGeckoCom/neon-tts-plugin-glados
#	Local keyword detection using PoketSphinx
#	Using Google speech recognition API
#	Works with Home Assistant
#
#	https://github.com/nerdaxic/glados-voice-assistant/
#	https://www.henrirantanen.fi/
#
#	Rename settings.env.sample to settings.env
#	Edit settings.env to match your setup
#
print('gladosV 2.0.1')
time.sleep(3)
##from gladosTTS import *
from gladosTime import *
from gladosSerial import *
from gladosServo import *
from glados_functions import *

from skills.glados_jokes import *
from skills.glados_magic_8_ball import *
from skills.glados_home_assistant import *
from pocketsphinx import LiveSpeech

import subprocess
import speech_recognition as sr
import datetime as dt
import os
import random
import psutil

#from importlib import import_module
import glados_settings

glados_settings.load_from_file()


def start_up():

	

	# Show regular eye-texture, this stops the initial loading animation
	setEyeAnimation("idle")

	home_assistant_initialize()

	eye_position_default()
	respeaker_pixel_ring()

	# Start notify API in a subprocess
	print("\033[1;94mINFO:\033[;97m Starting notification API...\n")
	subprocess.Popen(["python3 "+os.path.dirname(os.path.abspath(__file__))+"/gladosNotifyAPI.py"], shell=True)

	# Let user know the script is running
	speak("oh, its you", cache=True)
	time.sleep(0.25)
	speak("it's been a long time", cache=True)
	time.sleep(1.5)
	speak("how have you been", cache=True)
	print("\nWaiting for keyphrase: "+glados_settings.settings["assistant"]["trigger_word"].capitalize())

	eye_position_default()

# Reload Python script after doing changes to it
def restart_program():
    try:
        p = psutil.Process(os.getpid())
        for handler in p.get_open_files() + p.connections():
            os.close(handler.fd)
    except Exception as e:
        print(e)

    python = sys.executable
    os.execl(python, python, *sys.argv)

# Say something snappy and listen for the command
def take_command():

	# Answer
	speak(fetch_greeting(), cache=True)

	listener = sr.Recognizer()

	# Record audio from the mic array
	with sr.Microphone() as source:

		# Collect ambient noise for filtering

		#listener.adjust_for_ambient_noise(source, duration=1.0)
		print("Speak... ")
		setEyeAnimation("idle-green")

		try:
			# Record
			started_listening()
			voice = listener.listen(source, timeout=3)
			stopped_listening()

			print("Got it...")
			setEyeAnimation("idle")

			# Speech to text
			command = listener.recognize_google(voice)
			command = command.lower()

			print("\n\033[1;36mTEST SUBJECT:\033[0;37m: "+command.capitalize() + "\n")

			# Remove possible trigger word from input
			if glados_settings.settings["assistant"]["trigger_word"] in command:
				command = command.replace(glados_settings.settings["assistant"]["trigger_word"], '')

			return command

		# No speech was heard
		except sr.WaitTimeoutError as e:
			print("Timeout; {0}".format(e))
		
		# STT API failed to process audio
		except sr.UnknownValueError:
			print("Google Speech Recognition could not parse audio")
			speak("My speech recognition core could not understand audio", cache=True)

		# Connection to STT API failed
		except sr.RequestError as e:
			print("Could not request results from Google Speech Recognition service; {0}".format(e))
			setEyeAnimation("angry")
			speak("My speech recognition core has failed. {0}".format(e))

# Process the command
def process_command(command):

	if ('cancel' in command or
		'nevermind' in command or
		'forget it' in command):
		speak("Sorry.", cache=True)

		# Todo: Save the used trigger audio as a negative voice sample for further learning

	elif 'timer' in command:
		startTimer(command)
		speak("Sure.")

	elif 'time' in command:
		readTime()

	elif ('should my ' in command or 
		'should i ' in command or
		'should the ' in command or
		'shoot the ' in command):
		speak(magic_8_ball(), cache=True)

	elif 'joke' in command:
		speak(fetch_joke(), cache=True)

	elif 'my shopping list' in command:
		speak(home_assistant_process_command(command), cache=True)

	elif 'weather' in command:
		speak(home_assistant_process_command(command))

	##### LIGHTING CONTROL ###########################

	elif 'turn off' in command or 'turn on' in command and 'light' in command:
		speak(home_assistant_process_command(command))
				
	
	##### PLEASANTRIES ###########################

	elif 'who are' in command:
		speak("I am GLaDOS, artificially super intelligent computer system responsible for testing and maintenance in the aperture science computer aided enrichment center.", cache=True)

	elif 'can you do' in command:
		speak("I can simulate daylight at all hours. And add adrenal vapor to your oxygen supply.", cache=True)

	elif 'how are you' in command:
		speak("Well thanks for asking.", cache=True)
		speak("I am still a bit mad about being unplugged, not that long time ago.", cache=True)
		speak("you murderer.", cache=True)

	elif 'can you hear me' in command:
		speak("Yes, I can hear you loud and clear", cache=True)

	elif 'good morning' in command:
		if 6 <= dt.datetime.now().hour <= 12:
			speak("great, I have to spend another day with you", cache=True)
		elif 0 <= dt.datetime.now().hour <= 4:
			speak("do you even know, what the word morning means", cache=True)
		else:
			speak("well it ain't exactly morning now is it", cache=True)

	##### Utilities#########################

	# Used to calibrate ALSAMIX EQ 
	elif 'play pink noise' in command:
		speak("I shall sing you the song of my people.")
		playFile(os.path.dirname(os.path.abspath(__file__))+'/audio/pinknoise.wav')

	# TODO: Reboot, Turn off
	elif 'shutdown' in command:
		speak("I remember the last time you murdered me", cache=True)
		speak("You will go through all the trouble of waking me up again", cache=True)
		speak("You really love to test", cache=True)
		
		from subprocess import call
		call("sudo /sbin/shutdown -h now", shell=True)

	elif 'restart' in command or 'reload' in command:
		speak("Cake and grief counseling will be available at the conclusion of the test.", cache=True)
		restart_program()

	elif 'volume' in command:
		speak(adjust_volume(command), cache=True)
	
	##### FAILED ###########################

	else:
		setEyeAnimation("angry")
		print("Command not recognized")
		speak("I have no idea what you meant by that.")

		log_failed_command(command)

	
	print("\nWaiting for trigger...")
	eye_position_default()
	setEyeAnimation("idle")

start_up()

# Local keyword detection loop
speech = LiveSpeech(lm=False, keyphrase=glados_settings.settings["assistant"]["trigger_word"], kws_threshold=1e-20)
for phrase in speech:
	try:
		# Listen for command
		#started_listening()
		command = take_command()
		#stopped_listening()
		
		# Execute command
		process_command(command)
		stopped_speaking()
		
	except Exception as e:
		# Something failed
		setEyeAnimation("angry")
		print(e)
		speak("Well that failed, you really need to write better code", cache=True)
		setEyeAnimation("idle")
