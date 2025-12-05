import threading
import SharedData as sd

class Controller:
    def __init__(self):
        
        # components
        self.voice_interface = None # receives and validates voice commands sending appropriate signals to appropriate component
        self.counter = None # dictates exercise tempo with voice ques, counts times between sets
        self.video_processor = None # processes camera feed from 2 cameras, saves the video and produces DataFrame objects
        self.graphical_renderer = None # reads video from file, annotates each frame with feedback based on completed DataFrame objects, saves modified frames as video
        self.graphical_ui = None # displays graphical user interface on a pc

        # existing components, not included in controller
        # exercise_validator, owner -> video processor
        # gathers information about recorded exercise, completes DataFrame objects

    def run(self):
        self.graphical_ui.run_start() # starts the visual user interface
        self.voice_interface.run() # voice interface in dormant state until signalled by graphical ui
        self.idle()

    def idle(self):
        # signal from audio interface or other: 'I have a command for the controller'
        while True:
            sd.SharedData.event_command_for_controller_ready.wait()
            sd.SharedData.event_command_for_controller_ready.clear()
            command = self.voice_interface.command_storage.value # the command is stored in the voice interface class
            if command == sd.SharedData.EXIT_COMMAND:
                self.graphical_renderer.run() # when renderer is finished it sends a signal to gui
                sd.SharedData.renderer_is_processing.set() # notify gui that renderer has started processing the video
                return None
            if command == sd.SharedData.LATERAL_RAISES_COMMAND:
                self.start_exercise(sd.SharedData.LATERAL_RAISES_COMMAND)
            elif command == sd.SharedData.BARBELL_ROW_COMMAND:
                self.start_exercise(sd.SharedData.BARBELL_ROW_COMMAND)
            elif command == sd.SharedData.DUMBBELL_CURL_COMMAND:
                self.start_exercise(sd.SharedData.DUMBBELL_CURL_COMMAND)
            # command executed, you may proceed
            sd.SharedData.event_command_handled_by_controller.set()

    def start_exercise(self, exercise):
        self.counter.run() # start dictating tempo
        self.video_processor.run(exercise) # start processing camera feed, create DataFrame objects
        # video processor runs video validator after each repetition
        # go back to idle

