import _thread as thread
import utime as time
import picounicorn

"""
    Example for starting and ending threads on the Raspberry Pico with the press of a button.
    
    The main thread is started automatically and waits for input while neither button A or B
    is pressed. When button A is pressed it will attempt to start a new thread which will
    itself start executing the function do_something independently. When button B is pressed
    the global flag end_worker_thread is set to True by the main thread. When a worker thread
    is started it will check that flag before the next execution of the do_something function
    and call exit on itself.
    
    The print function has been made thread save to avoid strange line breaks.
    
    As on my Pico a pimoroni unicorn hat (16x7 RGB LED hat with 4 buttons) is installed I use
    its buttons. You could simply exchange that part to match your setup.
    
    Sample console output with the -> input:
    
    -> pressed button A
    mainthread attempting to start worker thread
    worker thread - started
    worker thread - lock is not locked - doing something
    worker thread - lock is not locked - doing something
    worker thread - lock is not locked - doing something
    -> pressed button A again
    mainthread attempting to start worker thread
    <class 'OSError'>: max amount of worker threads already running
    worker thread - lock is not locked - doing something
    worker thread - lock is not locked - doing something
    worker thread - lock is not locked - doing something
    -> pressed button B
    mainthread - signaling worker thread to exit
    mainthread - lock released
"""

end_worker_thread = False # used to signal worker thread to exit
lock = thread.allocate_lock() # used for thread save printing

def sleep(delay = 1):
    time.sleep(delay)


def do_something(): # only worker thread will be using this method
    while not end_worker_thread:
        thread_save_print('worker thread - lock is not locked - doing something')
        sleep()
    thread.exit() # ending current thread (worker thread) if lock is locked
  
  
def start_worker_thread(): # only main thread will be using this method
    try: # making sure we are not starting too many threads as the pico only has 2 cores
        thread.start_new_thread(do_something, ())
        thread_save_print('worker thread - started')
    except OSError as exception:
        thread_save_print(f'{type(exception)}: max amount of worker threads already running')
    sleep()
    
def thread_save_print(text):
    lock.acquire()
    print(text)
    lock.release()


picounicorn.init()
while True:
    while not picounicorn.is_pressed(picounicorn.BUTTON_A) \
          and not picounicorn.is_pressed(picounicorn.BUTTON_B):
#         print('mainthread sleeping') # commented out to prevent spamming console
        sleep(0.1) # sleep time should be kept low to react when a button is pressed
    if picounicorn.is_pressed(picounicorn.BUTTON_A):
        print('mainthread attempting to start worker thread')
        start_worker_thread()
    if picounicorn.is_pressed(picounicorn.BUTTON_B):
        thread_save_print('mainthread - signaling worker thread to exit')
        end_worker_thread = True
        sleep(1.1)
        """
            Waiting long enough to make sure the worker thread got the signal
            you will have to adjust that to your use or reset the flag at a more
            useful place - I just kept it simple for the example
        """
        end_worker_thread = False
        thread_save_print('mainthread - lock released')
