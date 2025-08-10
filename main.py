import network
import socket
import time
import math
from cosmic import CosmicUnicorn
from picographics import PicoGraphics, DISPLAY_COSMIC_UNICORN
from makey_arrays import mask_red, mask_white, base_image
from animations import AnimationManager
from laugh import animation_frames as laugh_frames  # Ensure laugh.py is imported



SSID = "RJB_PUK_2.4"
PASSWORD = "pimoroni"

cu = CosmicUnicorn()
graphics = PicoGraphics(display=DISPLAY_COSMIC_UNICORN)
cu.set_brightness(0.5)

# Initialize animation manager
anim_manager = AnimationManager(graphics, mask_red, mask_white, base_image)

# Modes
MODE_RED = 0
MODE_RAINBOW = 1
MODE_STATIC = 2
MODE_FIRE = 3
MODE_EYES_MOVING = 4
MODE_EYES_BLINKING = 5
MODE_EYES_CRAZY = 6
mode = MODE_RED

# Add frame index for discrete eyes moving
frame_index_eyes_moving = 0
TOTAL_EYES_FRAMES = 10  # Number of steps to move left (adjust as needed)

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)
print("Connecting to WiFi...")
while not wlan.isconnected():
    time.sleep(0.5)
print("Connected:", wlan.ifconfig())

# Setup TCP server
addr = socket.getaddrinfo('0.0.0.0', 5000)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)
s.setblocking(False)
print("Socket server listening on", addr)
print("Available commands: red, rainbow, static, fire, eyes_moving, eyes_blinking, eyes_crazy")

frame_delay = 33  # ~30 FPS
last_draw_time = time.ticks_ms()

# Draw initial red pixels on startup
anim_manager.draw_red()
cu.update(graphics)

while True:
    try:
        cl, addr = s.accept()
    except:
        cl = None

    if cl:
        print("Client connected from", addr)
        try:
            cl.setblocking(True)
            cl.settimeout(5.0)  # 5 second timeout
            cmd = cl.recv(1024).decode().strip().lower()
            print("Received command:", cmd)
            
            if cmd in ["red", "blue", "green", "purple", "pink"]:
                mode = MODE_RED
                anim_manager.set_mask_color(cmd)
                anim_manager.draw_mask_color()
                cu.update(graphics)
                response = f"OK: {cmd.upper()} mode"
            elif cmd == "rainbow":
                mode = MODE_RAINBOW
                response = "OK: RAINBOW mode 🌈"
            elif cmd == "static":
                mode = MODE_STATIC
                anim_manager.draw_static()
                cu.update(graphics)
                response = "OK: STATIC mode"
            elif cmd == "fire":
                mode = MODE_FIRE
                response = "OK: FIRE mode 🔥"
            elif cmd == "eyes_moving":
                mode = MODE_EYES_MOVING
                response = "OK: EYES MOVING mode 👀"
                # Run the eyes animation loop twice, then stop
                for _ in range(2 * len(anim_manager.eyes_move.animation_frames)):
                    anim_manager.draw_eyes_moving()
                    cu.update(graphics)
                    time.sleep(frame_delay / 1000.0)
                mode = MODE_STATIC
            elif cmd == "eyes_blinking":
                mode = MODE_EYES_BLINKING
                response = "OK: EYES BLINKING mode 😉"
            elif cmd == "eyes_crazy":
                mode = MODE_EYES_CRAZY
                response = "OK: EYES CRAZY mode 😵"
            elif cmd == "laugh":
                mode = MODE_STATIC  # Or a new MODE_LAUGH if you want
                response = "OK: LAUGH mode 😆"
                from laugh import animation_frames
                for i in range(2 * len(animation_frames)):
                    anim_manager.draw_laugh()
                    cu.update(graphics)
                    # Add a longer delay after each frame
                    time.sleep(0.5)
                mode = MODE_STATIC
            elif cmd == "leftarm_up":
                mode = MODE_STATIC  # Or a new MODE_LAUGH if you want
                response = "OK: leftarm_up mode 😆"
                for i in range(1 * len(anim_manager.leftarm_up.animation_frames)):
                    anim_manager.draw_leftarm_up()
                    cu.update(graphics)
                    # Add a longer delay after each frame
                    time.sleep(frame_delay / 1000.0)
                mode = MODE_STATIC
            elif cmd == "leftarm_down":
                mode = MODE_STATIC  # Or a new MODE_LAUGH if you want
                response = "OK: leftarm_down mode 😆"
                from leftarm_down import animation_frames
                for i in range(1 * len(animation_frames)):
                    anim_manager.draw_leftarm_down()
                    cu.update(graphics)
                    # Add a longer delay after each frame
                    time.sleep(frame_delay / 1000.0)
                mode = MODE_STATIC
            elif cmd == "rightarm_up":
                mode = MODE_STATIC  # Or a new MODE_LAUGH if you want
                response = "OK: rightarm_up mode 😆"
                from rightarm_up import animation_frames
                for i in range(1 * len(animation_frames)):
                    anim_manager.draw_rightarm_up()
                    cu.update(graphics)
                    # Add a longer delay after each frame
                    time.sleep(frame_delay / 1000.0)
                mode = MODE_STATIC
            elif cmd == "rightarm_down":
                mode = MODE_STATIC  # Or a new MODE_LAUGH if you want
                response = "OK: rightarm_down mode 😆"
                from rightarm_down import animation_frames
                for i in range(1 * len(animation_frames)):
                    anim_manager.draw_rightarm_down()
                    cu.update(graphics)
                    # Add a longer delay after each frame
                    time.sleep(frame_delay / 1000.0)
                mode = MODE_STATIC
            elif cmd == "dance_1":
                mode = MODE_STATIC  # Or a new MODE_LAUGH if you want
                response = "OK: dance_1 mode 😆"
                for i in range(1 * len(leftarm_up.animation_frames)):
                    anim_manager.draw_leftarm_up()
                    cu.update(graphics)
                    # Add a longer delay after each frame
                    time.sleep(frame_delay / 1000.0)
                for i in range(1 * len(leftarm_up.animation_frames)):
                    anim_manager.draw_leftarm_down()
                    anim_manager.draw_rightarm_up()
                    cu.update(graphics)
                    # Add a longer delay after each frame
                    time.sleep(frame_delay / 1000.0)
                for i in range(1 * len(leftarm_up.animation_frames)):
                    anim_manager.draw_leftarm_up()
                    anim_manager.draw_rightarm_down()
                    cu.update(graphics)
                    # Add a longer delay after each frame
                    time.sleep(frame_delay / 1000.0)
                mode = MODE_STATIC
            elif cmd == "dance_2":
                mode = MODE_STATIC  # Or a new MODE_LAUGH if you want
                response = "OK: dance_1 mode 😆"
                for i in range(1 * len(dance_1.animation_frames)):
                    anim_manager.draw_dance_1()
                    cu.update(graphics)
                    # Add a longer delay after each frame
                    time.sleep(frame_delay / 1000.0)
                mode = MODE_STATIC
            else:
                response = f"ERROR: Unknown command '{cmd}'. Available: red, rainbow, static, fire, eyes_moving, eyes_blinking, eyes_crazy"
            
            cl.send((response + "\n").encode())
        except Exception as e:
            print("Client error:", e)
            try:
                cl.send(b"ERROR: Connection failed\n")
            except:
                pass
        finally:
            cl.close()

    now = time.ticks_ms()
    if (mode == MODE_RAINBOW or mode == MODE_FIRE or mode == MODE_EYES_MOVING or 
        mode == MODE_EYES_BLINKING or mode == MODE_EYES_CRAZY) and time.ticks_diff(now, last_draw_time) >= frame_delay:
        last_draw_time = now
        if mode == MODE_RAINBOW:
            anim_manager.update_rainbow_phase()
            anim_manager.draw_rainbow()
        elif mode == MODE_FIRE:
            anim_manager.update_rainbow_phase()
            anim_manager.draw_fire()
        elif mode == MODE_EYES_BLINKING:
            anim_manager.draw_eyes_blinking()
        elif mode == MODE_EYES_CRAZY:
            anim_manager.draw_eyes_crazy()
        print("[MAIN DEBUG] Calling cu.update(graphics)")
        cu.update(graphics)
