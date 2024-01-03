 #!/usr/bin/env python
# coding: utf-8

# In[1]:


import os, json
import numpy as np
from psychopy import visual, event, monitors, misc, prefs
prefs.hardware["audioLib"] = ["PTB"]
from psychopy import sound, core
from speller import Keyboard

# Participant 3 randomized frequency order ['60', '120', '40', '30', '80', '240', '48']

# BLOCK 1
code="mgold_61_6521"
STREAM = True
SCREEN = 1
SCREEN_SIZE = (1920, 1080) # Mac: (1792, 1120), LabPC: (1920, 1080)
SCREEN_WIDTH = 53.0  # Mac: (34,5), LabPC: 53.0
SCREEN_DISTANCE = 60.0
SCREEN_COLOR = (0, 0, 0)
FR = 240  # screen frame rate
PR1 = 60  # codes presentation rate

STT_WIDTH = 2.2
STT_HEIGHT = 2.2
TEXT_FIELD_HEIGHT = 3.0
KEY_WIDTH = 3.0
KEY_HEIGHT = 3.0
KEY_SPACE = 0.5
KEY_COLORS = ["black", "white", "green", "blue"]
KEYS = [
    ["A", "B", "C", "D", "E", "F", "G", "H"], 
    ["I", "J", "K", "L", "M", "N", "O", "P"], 
    ["Q", "R", "S", "T", "U", "V", "W", "X"], 
    ["Y", "Z", "underscore", "dot", "question", "exclamation", "smaller", "hash"]]

KEYS_randomized_target = [16,0,4,1,11,3,8,21,28,10,6,2,17,15,29,14,25,5,27,9,7,13,31,22,12,26,18,19,20,30,24,23]
KEYS_randomized_targetkey = ['Q', 'A', 'E', 'B', 'L', 'D', 'I', 'V', 'question', 'K', 'G', 'C', 'R', 'P', 'exclamation', 'O', 'Z', 'F', 'dot', 'J', 'H', 'N', 'hash', 'W', 'M', 'underscore', 'S', 'T', 'U', 'smaller', 'Y', 'X']     
        
CUE_TIME = 0.8
TRIAL_TIME = 4.2
FEEDBACK_TIME = 0.5
ITI_TIME = 0.5

# Initialize keyboard
keyboard = Keyboard(size=SCREEN_SIZE, width=SCREEN_WIDTH, distance=SCREEN_DISTANCE, screen=SCREEN, window_color=SCREEN_COLOR, stream=STREAM)
ppd = keyboard.get_pixels_per_degree()

# Add stimulus timing tracker at left top of the screen
x_pos = -SCREEN_SIZE[0] / 2 + STT_WIDTH / 2 * ppd
y_pos = SCREEN_SIZE[1] / 2 - STT_HEIGHT / 2 * ppd
images = ["images/black.png", "images/white.png"]
    
keyboard.add_key("stt", (STT_WIDTH * ppd, STT_HEIGHT * ppd), (x_pos, y_pos), images)

# Add text field at the top of the screen
x_pos = STT_WIDTH * ppd
y_pos = SCREEN_SIZE[1] / 2 - TEXT_FIELD_HEIGHT * ppd / 2
keyboard.add_text_field("text", "", (SCREEN_SIZE[0] - STT_WIDTH * ppd, TEXT_FIELD_HEIGHT * ppd), (x_pos, y_pos), (0, 0, 0), (-1, -1, -1))

# Add the keys
for y in range(len(KEYS)):
    for x in range(len(KEYS[y])):
        x_pos = (x - len(KEYS[y]) / 2 + 0.5) * (KEY_WIDTH + KEY_SPACE) * ppd
        y_pos = -(y - len(KEYS) / 2) * (KEY_HEIGHT + KEY_SPACE) * ppd - TEXT_FIELD_HEIGHT * ppd
        images = [f"images/{KEYS[y][x]}_{color}.png" for color in KEY_COLORS]
        keyboard.add_key(KEYS[y][x], (KEY_WIDTH * ppd, KEY_HEIGHT * ppd), (x_pos, y_pos), images)

codes = dict()
tmp = np.load(f"codes/{code}.npz")["codes"]

def experiment(PR,FR,tmp,codes,KEYS,keyboard,KEYS_randomized_target,KEYS_randomized_targetkey,CUE_TIME):
    # Upsample to framerate
    tmp = np.repeat(tmp, int(FR / PR), axis=0)

    # Repeat to trial time
    tmp = np.tile(tmp, (2, 1))  # modulated codes

    # Add to speller
    codes = dict()
    i = 0
    for row in KEYS:
        for key in row:
            codes[key] = tmp[:, i].tolist()
            i += 1
    codes["stt"] = [1,1] + [0] * int(5 * keyboard.get_framerate())

    # Set highlights
    highlights = dict()
    for row in KEYS:
        for key in row:
            highlights[key] = [0]
    highlights["stt"] = [0]
    keyboard.log(["visual", "param", "codes", json.dumps(codes)])

    # Wait for start
    keyboard.set_field_text("text", "Press button to start Next Block.")
    print("Press button to start.")
    event.waitKeys()
    keyboard.set_field_text("text", "")
    print("Starting.")

    # Start experiment
    keyboard.log(marker=["visual", "cmd", "start_experiment", ""])
    keyboard.set_field_text("text", "Starting...")
    keyboard.run(highlights, 5.0)
    keyboard.set_field_text("text", "")

    # Loop trials
    text = ""
    for i_trial in range(len(KEYS_randomized_targetkey)):

        # Set target
        target =  KEYS_randomized_target[i_trial]
        target_key =  KEYS_randomized_targetkey[i_trial]
        print(f"{1 + i_trial:03d}/{KEYS_randomized_targetkey}\t{target_key}\t{target}")
        keyboard.log(["visual", "param", "code", json.dumps(code)])
        keyboard.log(["visual", "param", "target", json.dumps(target)])
        keyboard.log(["visual", "param", "key", json.dumps(target_key)])
        
        # Cue
        highlights[target_key] = [-2]
        keyboard.run(highlights, CUE_TIME, 
            start_marker=["visual", "cmd", "start_cue", json.dumps(1+i_trial)], 
            stop_marker=["visual", "cmd", "stop_cue", json.dumps(1+i_trial)])
        highlights[target_key] = [0]

        # Trial
        keyboard.run(codes, TRIAL_TIME, 
            start_marker=["visual", "cmd", "start_trial", json.dumps(1+i_trial)], 
            stop_marker=["visual", "cmd", "stop_trial", json.dumps(1+i_trial)])
        
experiment(PR1,FR,tmp,code,KEYS,keyboard,KEYS_randomized_target,KEYS_randomized_targetkey,CUE_TIME)
        
# Wait to continue
keyboard.log(marker=["visual", "cmd", "stop_run", ""])
keyboard.set_field_text("text", "Waiting for researcher to continue Block 2")
print("Waiting for researcher to continue")        
event.waitKeys() 

# BLOCK-2 
PR2 = 120  # codes presentation rate
experiment(PR2,FR,tmp,code,KEYS,keyboard,KEYS_randomized_target,KEYS_randomized_targetkey,CUE_TIME)
        
# Wait to continue
keyboard.log(marker=["visual", "cmd", "stop_run", ""])
keyboard.set_field_text("text", "Waiting for researcher to continue Block 3")
print("Waiting for researcher to continue")        
event.waitKeys() 

# BLOCK-3
PR3 = 40  # codes presentation rate
experiment(PR3,FR,tmp,code,KEYS,keyboard,KEYS_randomized_target,KEYS_randomized_targetkey,CUE_TIME)

# Wait to continue
keyboard.log(marker=["visual", "cmd", "stop_run", ""])
keyboard.set_field_text("text", "Waiting for researcher to continue Block 4")
print("Waiting for researcher to continue")        
event.waitKeys() 

# BLOCK-4
PR4 = 30  # codes presentation rate
experiment(PR4,FR,tmp,code,KEYS,keyboard,KEYS_randomized_target,KEYS_randomized_targetkey,CUE_TIME)

# Wait to continue
keyboard.log(marker=["visual", "cmd", "stop_run", ""])
keyboard.set_field_text("text", "Waiting for researcher to continue Block 5")
print("Waiting for researcher to continue")        
event.waitKeys() 

# BLOCK-5
PR5 = 80  # codes presentation rate
experiment(PR5,FR,tmp,code,KEYS,keyboard,KEYS_randomized_target,KEYS_randomized_targetkey,CUE_TIME)
        
# Wait to continue
keyboard.log(marker=["visual", "cmd", "stop_run", ""])
keyboard.set_field_text("text", "Waiting for researcher to continue Block 6")
print("Waiting for researcher to continue")        
event.waitKeys() 

# BLOCK-6
PR6 = 240  # codes presentation rate
experiment(PR6,FR,tmp,code,KEYS,keyboard,KEYS_randomized_target,KEYS_randomized_targetkey,CUE_TIME)

# Wait to continue
keyboard.log(marker=["visual", "cmd", "stop_run", ""])
keyboard.set_field_text("text", "Waiting for researcher to continue Block 7")
print("Waiting for researcher to continue")        
event.waitKeys() 

# BLOCK-7
PR7 = 48  # codes presentation rate
experiment(PR7,FR,tmp,code,KEYS,keyboard,KEYS_randomized_target,KEYS_randomized_targetkey,CUE_TIME)
                        
# Stop experiment
keyboard.log(marker=["visual", "cmd", "stop_experiment", ""])
keyboard.set_field_text("text", "Stopping...")
print("Stopping.")
#keyboard.run(highlights, 5.0)
#keyboard.set_field_text("text", "")
keyboard.quit()
print("Finished.")


# In[ ]:




