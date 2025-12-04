import pyttsx3

engine=pyttsx3.init()
print('')
engine.setProperty('rate', 170)
engine.setProperty('volume', 1.0)
engine.say('poland mountain')
engine.runAndWait()

