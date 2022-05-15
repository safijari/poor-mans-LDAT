from moviepy.editor import *
import cv2
import numpy as np

import matplotlib.pyplot as plt


def diff(arr1, arr2):
    d = [i1 - i2 for i1, i2 in zip(arr1, arr2)]
    return d


class LDAT(object):
    """
    video_rate_multiplier: Pixel 3 saves the 1/8th speed slowmo video as a 30fps video, not a 240 fps video
                           there is no way to determine the actual framerate without uesr input
                           in this case that multiplier would be 240//30 == 8
    """

    def __init__(self, video_rate_multiplier, audio_event_threshold=0.05):
        super(LDAT, self).__init__()
        self.video_rate_multiplier = video_rate_multiplier
        self.audio_event_threshold = audio_event_threshold

    def process_video(self, fname):
        clip = VideoFileClip(fname)
        audioclip = clip.audio

    def extract_audio_events(
        self, audio_data, audio_rate, thresh=0.5, event_length_sec=0.6, verbose=False
    ):
        event_length = event_length_sec * audio_rate * self.video_rate_multiplier
        event_times = []
        last_time = 0
        for i, val in enumerate(audio_data):
            if i < event_length * 0.3:
                continue
            if val > thresh and ((i - last_time) > event_length or last_time < 0):
                event_times.append(i)
                last_time = i

        if verbose:
            plt.figure(figsize=(80, 5))
            plt.plot(audio_data)
            plt.plot(event_times, [0.05 for _ in event_times], "r.")
            plt.title(f"Found {len(event_times)} events")

        return event_times


def process_audo_latency_video(fname, video_rate=8, audio_thresh=0.01, verbose=False):
    clip = VideoFileClip(fname)
    audioclip = clip.audio
    sa = audioclip.to_soundarray()[:, 0]
    audio_rate = len(sa) / clip.duration
    sa2 = sa.copy()
    if verbose:
        plt.plot(sa2)

    sa2[sa2 > audio_thresh] = 1
    sa2[sa2 <= audio_thresh] = 0

    event_times = extract_events(sa2)

    if verbose:
        plt.figure(figsize=(20, 2))
        plt.plot(sa2)
        plt.plot(event_times, [0.5 for _ in event_times], "r.")

    frame_sum = []

    for frame in clip.iter_frames():
        frame_sum.append(frame.sum())

    frame_sum = np.array(frame_sum)
    frame_sum = frame_sum - frame_sum.min()
    frame_sum = frame_sum / frame_sum.max()

    video_event_times = extract_events(
        frame_sum, event_length=0.6 * video_rate * 30, thresh=0.3
    )

    if verbose:
        plt.figure()
        plt.plot(frame_sum)
        plt.plot(video_event_times, [0.5 for _ in video_event_times], "r.")

    event_times_sec = np.array(event_times) / (audio_rate * video_rate)
    video_event_times_sec = np.array(video_event_times) / (video_rate * 30)

    if verbose:
        plt.figure()
        plt.plot(event_times_sec, [0 for _ in event_times], "b.")
        plt.plot(video_event_times_sec, [0.1 for _ in video_event_times], "r.")

    return np.array(diff(event_times_sec, video_event_times_sec))
