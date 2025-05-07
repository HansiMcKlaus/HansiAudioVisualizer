from scripts.rendering import render_frame

import librosa
import numpy as np
import cv2
from scipy.ndimage import convolve1d
from scipy.interpolate import interp1d
from pathvalidate import sanitize_filename, is_valid_filename

import os
import shutil
import subprocess
import time
import concurrent.futures

import sys
sys.stdout.reconfigure(encoding="utf-8")

def get_video_file(audio_file_name, settings):
    start_time = time.time()
    start_time_sub = time.time()

    frames_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frames"))
    if os.path.exists(frames_path):
        shutil.rmtree(frames_path)

    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../upload"))
    audio_path = os.path.join(base_path, audio_file_name)

    y, sr = load_audio(audio_path, settings['startEnd'][0], settings['startEnd'][1])
    print_progress(start_time_sub, time.time(), "Loading Audio")

    start_time_sub = time.time()
    frame_data = get_frame_data(y, sr, settings)
    if (settings['smoothing']):
        kernel = np.array([0.25, 0.5, 0.25])
        frame_data = convolve1d(frame_data, kernel, axis=0, mode='nearest')
    print_progress(start_time_sub, time.time(), "Calculating Data")

    start_time_sub = time.time()
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frames"))
    os.makedirs(output_dir, exist_ok=True)

    MAX_CORES = 8
    num_workers = os.cpu_count() if os.cpu_count() and os.cpu_count() < MAX_CORES else MAX_CORES
    args_list = [(i, data, settings, output_dir) for i, data in enumerate(frame_data)]
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        executor.map(render_and_save_frame, args_list)
    print_progress(start_time_sub, time.time(), "Saving Frames")

    start_time_sub = time.time()
    os.makedirs(os.path.abspath(os.path.join(os.path.dirname(__file__), "../video")), exist_ok=True)
    filename = settings['fileName'] if settings['fileName'] else "video"
    if not is_valid_filename(filename):
        filename = sanitize_filename(filename)
    output_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "../video/" + filename + ".mp4"))

    ffmpeg_command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "error",
        "-y",
        "-framerate", str(settings['framerate']),
        "-i", os.path.join(output_dir, "%05d.png"),
        "-i", audio_path,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        output_file
    ]

    try:
        subprocess.run(ffmpeg_command, check=True)
        print_progress(start_time_sub, time.time(), "FFMPEG")
        print(f"Video saved as: {filename}")
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg failed: {e}")

    print_progress(start_time, time.time(), "Total")
    return filename + ".mp4"

def get_preview_image(settings):
    frame_data = []
    if (settings["visualization"] == "volume"):
        frame_data = [1]
    elif (settings["visualization"] == "spectrum"):
        sample_data = np.load(os.path.join(os.path.abspath(os.path.dirname(__file__)), "_sample_audio.npz"))
        frame_data = get_frame_data(sample_data["y"], sample_data["sr"], settings)
    img = render_frame(frame_data[0], settings)
    output_dir = os.path.abspath(os.path.dirname(__file__))
    filename = os.path.join(output_dir, "_preview.jpg")
    cv2.imwrite(filename, img)
    return "_preview.jpg"

def print_progress(start, end, message):
    print(f"{message}: {end - start:.2f} seconds")

def load_audio(file_path, start, end):
    # audio_sample, sr = librosa.load(file_path, sr=None)
    # np.savez("_sample_audio.npz", y=y, sr=sr)
    return librosa.load(file_path, sr=None, offset=start, duration=end - start)

def get_frame_data(y, sr, settings):
    samples_per_frame = sr // settings["framerate"]
    if (settings["visualization"] == "volume"):
        stft = librosa.stft(y, n_fft=samples_per_frame, hop_length=samples_per_frame)
        freqs = librosa.fft_frequencies(sr=sr, n_fft=samples_per_frame)

        min_freq, max_freq = settings["minMaxFrequency"]
        valid_indices = np.where((freqs >= min_freq) & (freqs <= max_freq))[0]

        filtered_stft = np.zeros_like(stft)
        filtered_stft[valid_indices, :] = stft[valid_indices, :]
        filtered_y = librosa.istft(filtered_stft, hop_length=samples_per_frame)

        rms = librosa.feature.rms(y=filtered_y, frame_length=samples_per_frame, hop_length=samples_per_frame)
        db = librosa.amplitude_to_db(rms, ref=np.max)
        normalized_db = np.clip((db[0] + 60) / 60, 0, 1)
        return normalized_db

    elif settings["visualization"] == "spectrum":
        stft = librosa.stft(y, n_fft=samples_per_frame, hop_length=samples_per_frame)
        magnitude = np.abs(stft)
        freqs = librosa.fft_frequencies(sr=sr, n_fft=samples_per_frame)

        min_freq, max_freq = settings["minMaxFrequency"]
        valid_indices = np.where((freqs >= min_freq) & (freqs <= max_freq))[0]
        filtered_magnitude = magnitude[valid_indices, :]

        bins = settings["bins"]

        if len(valid_indices) < bins:
            x_old = np.linspace(0, 1, len(valid_indices))
            x_new = np.linspace(0, 1, bins)
            interpolator = interp1d(x_old, filtered_magnitude, axis=0, kind="linear", fill_value="extrapolate")
            binned_spectrum = interpolator(x_new)
        else:
            bin_size = max(1, len(valid_indices) / bins)
            binned_spectrum = np.array([
                np.mean(filtered_magnitude[int(i * bin_size) : int((i + 1) * bin_size)], axis=0)
                for i in range(bins)
            ])

        normalized_spectrum = np.clip(binned_spectrum / np.max(binned_spectrum), 0, 1)
        return normalized_spectrum.T

def render_and_save_frame(args):
    i, data, settings, output_dir = args
    img = render_frame(data, settings)
    filename = os.path.join(output_dir, f"{i:05d}.png")
    cv2.imwrite(filename, img)


# python -m scripts.entrypoint
if __name__ == "__main__":
    filename = "Circles.mp3"
    settings = {
        'visualization': 'spectrum',
        'style': 'line',
        'styleVariant': 'filled',
        'fileName': '_TestVideo',
        'width': 854, # 854
        'height': 480, # 480
        'framerate': 30,
        'startEnd': [0, 15],
        'smoothing': True,
        'antiAliasing': True,
        'polarWarp': False,
        'bins': 64,
        'binWidth': 0.75,
        'lineThickness': 10,
        'minMaxFrequency': [0, 2000],
        'color': '#ff0000',
        'backgroundColor': '#010204',
        'innerOuterRadius': [0, 1],
    }
    result = get_video_file(filename, settings)