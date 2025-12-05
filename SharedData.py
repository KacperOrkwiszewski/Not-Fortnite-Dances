import threading

class SharedData():
    # static command codes
    LATERAL_RAISES_COMMAND = 1
    BARBELL_ROW_COMMAND = 2
    DUMBBELL_CURL_COMMAND = 3
    UNKNOWN_COMMAND = 4
    END_EXERCISE_COMMAND = 5
    EXIT_COMMAND = 6

    # signals
    event_command_for_controller_ready = threading.Event()
    event_command_handled_by_controller = threading.Event()
    renderer_is_processing = threading.Event()

    # shared data
    recordings_filenames = None  # filenames recordings of each exercise before video processing
    annotated_recordings_filenames = None  # filenames of completed reports from exercises (after renderer)
    video_data = None  # list of frame_data objects, the objects are created by video_processor and supplied with data by exercise_validator
