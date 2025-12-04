import threading

import moviepy


command_storage = None

event_command_for_controller = threading.Event()
event_command_handled = threading.Event()

# commands
ex1 = 1
ex2 = 2
ex3 = 3
unknown = 4
end_ex = 5
end_all = 6

# exercise codes
ex1_code = 1
ex2_code = 2
ex3_code = 3

# states
state1 = 0
state2 = 1
state3 = 2
state4 = 3
state5 = 4

class Controller:
    def __init__(self):

        self.current_state = None # the state in which the program is in example: during exercise, making a report, etc

        # stored data
        self.recordings = None # recordings of each exercise after video processor
        self.annotated_recordings = None # after validator
        self.reports = None # completed reports from exercises (after renderer)

        # components
        self.voice_interface = None # receives and sends voice commands
        self.counter = None # dictates exercise tempo
        self.video_processor = None # processes camera feed
        self.exercise_validator = None # gathers information about recorded exercise
        self.graphical_renderer = None # creates and saves video report about exercise
        self.graphical_ui = None # displays graphical user interface on a pc

    def run(self):
        choice = self.graphical_ui.run()
        # see doc, change settings, start

    def idle(self):
        # signal from audio interface or other: 'I have a command for the controller'
        event_command_for_controller.wait()
        command = command_storage.value
        if command == end_all:
            self.show_report()
            return self.end_program()
        if command == ex1:
            self.record_exercise(ex1_code)
        if command == ex2:
            self.record_exercise(ex2_code)
        if command == ex3:
            self.record_exercise(ex3_code)
        # command executed, you may proceed
        command_storage.handled = True
        event_command_handled.set()
        return self.idle()

    def record_exercise(self,exercise):
        self.counter.run()
        recording = self.video_processor.run(exercise)
        self.recordings.append(recording)
        self.create_report(recording)

    def create_report(self):
        for recording in self.recordings:
            annotated_recording = self.exercise_validator.run(self.recording)
        report = self.graphical_renderer.run(annotated_recording)
        self.reports.append(report)
        # save report
        frames = []
        for obj in report:
            frames.append(obj.frame)
        fps = 30
        clip = moviepy.ImageSequenceClip(frames, fps=fps)
        clip.write_videofile("output.mp4", codec="libx264")
        self.idle()

    def show_report(self):
        self.graphical_ui.show_report()
        return 0

    def end_program(self):
        return 0
