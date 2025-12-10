import speech_recognition as sr
from speech_recognition.exceptions import UnknownValueError
from PySide6.QtCore import QObject, Signal, QRunnable, Slot, QThread
from threading import Event
import pyttsx3

class Voice(QObject):
  text_signal = Signal(str)

  def __init__(self):
    super().__init__()
    self.stop_recognizing = Event()

  def say(self, text):
    sayer = pyttsx3.init()
    sayer.say(text)
    sayer.runAndWait()

  def listen(self):
    recognizer = sr.Recognizer()
    with sr.Microphone() as voice_source:
      recognizer.adjust_for_ambient_noise(voice_source)

      while not self.stop_recognizing.is_set():
        try:
          audio = recognizer.listen(voice_source, timeout=3)
          text = recognizer.recognize_google(audio, language="pl-PL")
        except (UnknownValueError, sr.WaitTimeoutError):
          print("Couldn't catch that or timeout! - nothing to worry about, just continuing...")
          continue

        self.text_signal.emit(text)

# Simple test for listening
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

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
