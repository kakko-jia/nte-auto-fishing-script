import argparse
import ctypes
import time

import cv2
import dxcam
import numpy as np
import pydirectinput
import pygetwindow as gw


# Reference layout from the original 2560x1440 tuning.
REFERENCE_W = 2560
REFERENCE_H = 1440

SCREEN_W = REFERENCE_W
SCREEN_H = REFERENCE_H

BAR_REGION_REF = (800, 70, 1770, 130)
ICON_REGION_REF = (REFERENCE_W - 750, REFERENCE_H - 220, REFERENCE_W - 100, REFERENCE_H - 40)
HOOK_REGION_REF = (REFERENCE_W - 280, REFERENCE_H - 220, REFERENCE_W - 100, REFERENCE_H - 40)

BAR_REGION = BAR_REGION_REF
ICON_REGION = ICON_REGION_REF
HOOK_REGION = HOOK_REGION_REF

YELLOW_LOWER = np.array([20, 80, 120])
YELLOW_UPPER = np.array([40, 255, 255])
GREEN_LOWER = np.array([45, 80, 80])
GREEN_UPPER = np.array([85, 255, 255])

STEP2_BLUE_THRESHOLD = 0.06

TIMEOUT = {
    "STEP1_WAIT_START": 10,
    "STEP2_WAIT_HOOK": 30,
    "STEP3_FIGHTING": 60,
}

SLEEP = {
    "STEP1_WAIT_START": 0.3,
    "STEP2_WAIT_HOOK": 0.1,
    "STEP2_TRIGGER": 0.1,
    "STEP3_FIGHTING": 0.02,
    "STEP4_FINISH": 0.1,
}

REENTER_CURRENT_STATE = "__REENTER_CURRENT_STATE__"
STOP_KEY = 0x77  # F8


def scale_region(region, width, height):
    x1, y1, x2, y2 = region
    sx = width / REFERENCE_W
    sy = height / REFERENCE_H
    return (
        int(round(x1 * sx)),
        int(round(y1 * sy)),
        int(round(x2 * sx)),
        int(round(y2 * sy)),
    )


def configure_screen(width, height):
    global SCREEN_W, SCREEN_H, BAR_REGION, ICON_REGION, HOOK_REGION

    SCREEN_W = width
    SCREEN_H = height
    BAR_REGION = scale_region(BAR_REGION_REF, width, height)
    ICON_REGION = scale_region(ICON_REGION_REF, width, height)
    HOOK_REGION = scale_region(HOOK_REGION_REF, width, height)

    print(f"Detected capture size: {SCREEN_W}x{SCREEN_H}")
    print(f"BAR_REGION={BAR_REGION}")
    print(f"ICON_REGION={ICON_REGION}")
    print(f"HOOK_REGION={HOOK_REGION}")


def detect_primary_screen_size():
    width = ctypes.windll.user32.GetSystemMetrics(0)
    height = ctypes.windll.user32.GetSystemMetrics(1)
    return width, height


def activate_game_window(title="NTE"):
    windows = gw.getWindowsWithTitle(title)
    if not windows:
        print(f"Could not find a window with title containing {title!r}.")
        return False

    windows[0].activate()
    print(f"Activated window: {windows[0].title}")
    time.sleep(1)
    return True


def press_f():
    pydirectinput.keyDown("f")
    time.sleep(0.05)
    pydirectinput.keyUp("f")
    print(">>> Press F")


def should_stop():
    return ctypes.windll.user32.GetAsyncKeyState(STOP_KEY) & 0x8000


def release_keys():
    for key in ("a", "d", "f"):
        pydirectinput.keyUp(key)


def tap_fight_key(key):
    pydirectinput.keyDown(key)
    time.sleep(0.01)
    pydirectinput.keyUp(key)


def click_screen():
    pydirectinput.click(SCREEN_W // 2, SCREEN_H // 2)
    print(">>> Click center")


def crop_region(frame, region):
    x1, y1, x2, y2 = region
    return frame[y1:y2, x1:x2]


def get_color_ratio(frame, region, lower, upper):
    area = crop_region(frame, region)
    if area.size == 0:
        return 0

    hsv = cv2.cvtColor(area, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower, upper)
    return cv2.countNonZero(mask) / (area.shape[0] * area.shape[1])


def get_blue_ratio(frame):
    return get_color_ratio(
        frame,
        HOOK_REGION,
        np.array([100, 120, 120]),
        np.array([130, 255, 255]),
    )


def has_step2_prompt(frame):
    return get_blue_ratio(frame) > STEP2_BLUE_THRESHOLD


def get_yellow_ratio(frame):
    return get_color_ratio(frame, BAR_REGION, YELLOW_LOWER, YELLOW_UPPER)


def get_green_ratio(frame):
    return get_color_ratio(frame, BAR_REGION, GREEN_LOWER, GREEN_UPPER)


def has_step3_bar(frame):
    green_ratio = get_green_ratio(frame)
    yellow_ratio = get_yellow_ratio(frame)
    return green_ratio > 0.03 or (green_ratio > 0.015 and yellow_ratio > 0.001)


def find_yellow_x(frame):
    bar = crop_region(frame, BAR_REGION)
    hsv = cv2.cvtColor(bar, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, YELLOW_LOWER, YELLOW_UPPER)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    x, _, w, _ = cv2.boundingRect(max(contours, key=cv2.contourArea))
    return x + w // 2


def find_green_center_x(frame):
    bar = crop_region(frame, BAR_REGION)
    hsv = cv2.cvtColor(bar, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, GREEN_LOWER, GREEN_UPPER)
    _, xs = np.where(mask > 0)
    if len(xs) == 0:
        return None

    return (int(xs.min()) + int(xs.max())) // 2


def on_enter(state):
    print(f"\n{'=' * 50}")
    print(f"Enter state: {state}")
    print(f"{'=' * 50}")

    if state == "STEP1_WAIT_START":
        time.sleep(0.3)
        click_screen()
        time.sleep(0.2)
        press_f()
    elif state == "STEP2_TRIGGER":
        press_f()
    elif state == "STEP4_FINISH":
        time.sleep(0.5)
        click_screen()


def run_step1(frame, state_start):
    if time.time() - state_start > TIMEOUT["STEP1_WAIT_START"]:
        print("STEP1 timeout, retry")
        return REENTER_CURRENT_STATE

    if has_step2_prompt(frame):
        return "STEP2_TRIGGER"

    if has_step3_bar(frame):
        return "STEP3_FIGHTING"

    return "STEP1_WAIT_START"


def run_step2_wait(frame, state_start):
    if time.time() - state_start > TIMEOUT["STEP2_WAIT_HOOK"]:
        print("STEP2 timeout, back to STEP1")
        return "STEP1_WAIT_START"

    if has_step2_prompt(frame):
        return "STEP2_TRIGGER"

    if has_step3_bar(frame):
        return "STEP3_FIGHTING"

    return "STEP2_WAIT_HOOK"


def run_step2_trigger(frame, state_start):
    if has_step3_bar(frame):
        return "STEP3_FIGHTING"

    if time.time() - state_start > 3:
        print("STEP2_TRIGGER timeout")
        return "STEP1_WAIT_START"

    return "STEP2_TRIGGER"


def run_step3(frame, state_start):
    if time.time() - state_start > TIMEOUT["STEP3_FIGHTING"]:
        print("STEP3 timeout, back to STEP1")
        return "STEP1_WAIT_START"

    if get_green_ratio(frame) < 0.02:
        print("Fishing bar disappeared, finish")
        return "STEP4_FINISH"

    yellow_x = find_yellow_x(frame)
    green_x = find_green_center_x(frame)

    if yellow_x is not None and green_x is not None:
        diff = yellow_x - green_x
        print(f"yellow={yellow_x} | green={green_x} | diff={diff}")
        if diff < -10:
            tap_fight_key("d")
        elif diff > 10:
            tap_fight_key("a")

    return "STEP3_FIGHTING"


def run_step4(frame, state_start):
    if time.time() - state_start > 1.0:
        return "STEP1_WAIT_START"

    return "STEP4_FINISH"


def run_bot(window_title="NTE", target_fps=60):
    if not activate_game_window(window_title):
        return

    width, height = detect_primary_screen_size()
    configure_screen(width, height)

    camera = dxcam.create(device_idx=0, output_idx=0, output_color="BGR")
    camera.start(target_fps=target_fps)

    print("Auto fishing started. Press F8 or Ctrl+C to stop.")
    print("-" * 50)

    current_state = "STEP1_WAIT_START"
    state_start = time.time()
    first_frame_seen = False
    on_enter(current_state)

    try:
        while True:
            if should_stop():
                print("F8 pressed, stopping")
                break

            frame = camera.get_latest_frame()
            if frame is None:
                continue

            if not first_frame_seen:
                frame_h, frame_w = frame.shape[:2]
                if frame_w != SCREEN_W or frame_h != SCREEN_H:
                    configure_screen(frame_w, frame_h)
                first_frame_seen = True

            if current_state == "STEP1_WAIT_START":
                next_state = run_step1(frame, state_start)
            elif current_state == "STEP2_WAIT_HOOK":
                next_state = run_step2_wait(frame, state_start)
            elif current_state == "STEP2_TRIGGER":
                next_state = run_step2_trigger(frame, state_start)
            elif current_state == "STEP3_FIGHTING":
                next_state = run_step3(frame, state_start)
            elif current_state == "STEP4_FINISH":
                next_state = run_step4(frame, state_start)
            else:
                next_state = "STEP1_WAIT_START"

            if next_state == REENTER_CURRENT_STATE:
                state_start = time.time()
                on_enter(current_state)
            elif next_state != current_state:
                current_state = next_state
                state_start = time.time()
                on_enter(current_state)

            time.sleep(SLEEP.get(current_state, 0.1))

    finally:
        release_keys()
        camera.stop()
        print("Stopped")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Auto fishing helper for NTE using screen capture and keyboard input."
    )
    parser.add_argument(
        "--window-title",
        default="NTE",
        help="Game window title keyword to activate before starting. Default: NTE",
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=60,
        help="Screen capture target FPS. Default: 60",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_bot(window_title=args.window_title, target_fps=args.fps)
