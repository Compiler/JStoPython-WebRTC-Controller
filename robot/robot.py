import asyncio
from robot_webrtc_helper import RobotWRTC
from signal_helper import RobotSignaller


async def main_entry(video_track, keyboard_values):
    wrtc = RobotWRTC(video_track, keyboard_values)
    signaller = RobotSignaller(wrtc)