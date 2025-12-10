import speech_recognition as sr
from speech_recognition.exceptions import UnknownValueError
from PySide6.QtCore import QObject, Signal, Slot, QThread
from PySide6.QtWidgets import QApplication
import sys
from threading import Event
import pyttsx3
from state import *
import voice_utils as utils

class Voice(QObject):
  text_signal = Signal(str)

  def __init__(self):
    super().__init__()
    self.stop_recognizing = Event()
    self.state = State.START
    self.active = True

  def getNextState(self):
    return State(int(self.state) + 1)

  def say(self, text):
    sayer = pyttsx3.init()
    sayer.say(text)
    sayer.runAndWait()

  def listen(self):
    recognizer = sr.Recognizer()
    with sr.Microphone() as voice_source:
      recognizer.adjust_for_ambient_noise(voice_source, duration=2)

      while not self.stop_recognizing.is_set():
        try:
          audio = recognizer.listen(voice_source, timeout=3)
          text = recognizer.recognize_google(audio, language="pl-PL")
        except UnknownValueError:
          print("Couldn't catch that!")
          continue
        except sr.WaitTimeoutError:
          print("Timeout. Deactivating")
          self.active = False
          continue

        if utils.string_similarity(text, [OK_TRAINER_CMD]) is not None:
          self.active = True
          self.text_signal.emit(OK_TRAINER_CMD)
          if self.state == State.START:
            self.state = self.getNextState()
          continue

        if not self.active:
          continue

        possible_commands = state_transitions.get(self.state)
        command = utils.string_similarity(text, possible_commands)
        if command is not None:
          self.text_signal.emit(command)
          self.state = self.getNextState()
        else:
          self.text_signal.emit(UNRECOGNIZED_CMD)

# Simple test for listening
if __name__ == "__main__":

    @Slot(str)
    def handle_recognized_text(text):
      print(text)
      voice.say(text)
      if text.lower() == 'stop':
        voice.stop_recognizing.set()
        thread.quit()
        app.quit()

    app = QApplication(sys.argv)

    thread = QThread()
    voice = Voice()

    voice.moveToThread(thread)
    thread.started.connect(voice.listen)
    voice.text_signal.connect(handle_recognized_text)
    thread.start()

    print("Say something now.")
    sys.exit(app.exec())
