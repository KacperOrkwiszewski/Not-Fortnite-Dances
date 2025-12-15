import speech_recognition as sr
from speech_recognition.exceptions import UnknownValueError
from PySide6.QtCore import QObject, Signal, Slot, QThread
from PySide6.QtWidgets import QApplication
import sys
from threading import Event
import pyttsx3
from voice_interface import state
from voice_interface import voice_utils as utils

class Voice(QThread):
  text_signal = Signal(str)

  def __init__(self):
    super().__init__()
    self.stop_recognizing = Event()
    self.state = state.State.START
    self.active = True

  def getNextState(self, command=None):

    if command == state.FINISH_EXCERCISE_CMD:
      return state.State.CHOOSE_EXCERCISE

    if command == state.FINISH_TRAINING_CMD:
      return state.State.CHOOSE_COMMAND

    return state.State(int(self.state) + 1)

  def say(self, text):
    sayer = pyttsx3.init()
    sayer.say(text)
    sayer.runAndWait()

  def run(self):
    recognizer = sr.Recognizer()
    with sr.Microphone() as voice_source:
      recognizer.adjust_for_ambient_noise(voice_source, duration=2)

      while not self.stop_recognizing.is_set():
        try:
          audio = recognizer.listen(voice_source, timeout=3)
          text = recognizer.recognize_google(audio, language="pl-PL")
        except UnknownValueError:
          continue
        except sr.WaitTimeoutError:
          print("Timeout. Deactivating")
          self.active = False
          continue

        if utils.string_similarity(text, [state.OK_TRAINER_CMD]) is not None:
          self.active = True
          self.text_signal.emit(state.OK_TRAINER_CMD)
          if self.state == state.State.START:
            self.state = self.getNextState()
          continue

        if not self.active:
          continue

        possible_commands = state.state_transitions.get(self.state)
        command = utils.string_similarity(text, possible_commands)
        if command is not None:
          self.text_signal.emit(command)
          self.state = self.getNextState(command)
        else:
          self.text_signal.emit(state.UNRECOGNIZED_CMD)
