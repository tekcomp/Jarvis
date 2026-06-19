import queue
import threading

audio_queue = queue.Queue()
text_queue = queue.Queue()
stop_speaking = threading.Event()