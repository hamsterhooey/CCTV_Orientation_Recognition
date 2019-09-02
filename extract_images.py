"""
Extract images for training, from annotated videos
The annotations are stored in pkl and csv files
"""

import argparse
import tqdm
import cv2
import glob
import os
import numpy as np
import pickle
from tqdm import tqdm
from tqdm import trange

from annotate_videos import Video


def create_destination_directory(destination_directory):
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)


def save_frame(frame, output_path):
    cv2.imwrite(output_path, frame)
    print('Saved: {}'.format(output_path))


class VideoChunker():
    # num_frames specifies how many frames will be extracted from a video snippet
    def __init__(self, num_frames=30, output_dir="data/extracted_labeled_images"):
        self.num_frames = num_frames
        self.output_dir = output_dir
        self.count = {'left': 0, 'straight': 0, 'right': 0}

    def get_output_path(self, video_path, direction, timestamp, count):
        output_filename = str(count) + '_' + os.path.split(video_path)[-1][:-4] + '_' + direction + '_' + str(int(timestamp)) + '.png'
        destination_directory = os.path.join(self.output_dir, direction)
        output_path = os.path.join(destination_directory, output_filename)
        return output_path, destination_directory

    def extract_frame(self, cap, timestamp):
        cap.set(cv2.CAP_PROP_POS_MSEC, timestamp)
        ret, frame = cap.read()
        return ret, frame  # ret: False when frame isn't read

    def pad_to_length(self, timestamps_to_extract):  # Make sure that we get exactly num_frames
        if len(timestamps_to_extract) > self.num_frames:
            return timestamps_to_extract[:self.num_frames]
        elif len(timestamps_to_extract) < self.num_frames:
            return timestamps_to_extract.append(timestamps_to_extract[-1])
        else:
            return timestamps_to_extract

    def chunk_video(self, video_path, direction_timestamps):  # Annotations are in pickle format
        cap = cv2.VideoCapture(video_path)
        directions = {0: 'left', 1: 'straight', 2: 'right'}
        for key in directions.keys():
            print(key)
            sequence_id = 0
            direction = directions[key]
            # direction_timestamps[0] is all the left timestamps
            direction_timestamp = direction_timestamps[key]
            print(direction)

            if len(direction_timestamp) % 2 == 0 and len(direction_timestamp) > 0:  # Do not chunk empty direction timestamps
                # Extract timestamps between timestamp1 and timestamp2 at intervals of (timestamp2 - timestamp1)/num_frames
                for i in range(0, len(direction_timestamp), 2):
                    self.count[direction] += 1  # Increment the count
                    timestamp1 = int(direction_timestamp[i])
                    timestamp2 = int(direction_timestamp[i + 1])
                    timestamps_to_extract = [int(t) for t in np.arange(timestamp1, timestamp2, abs(timestamp2 - timestamp1) / self.num_frames)]  # Create num_frames frames
                    timestamps_to_extract = self.pad_to_length(timestamps_to_extract)

                    for timestamp_to_extract in timestamps_to_extract:
                        ret, frame = self.extract_frame(cap, timestamp_to_extract)
                        if ret:
                            output_path, destination_directory = self.get_output_path(video_path, direction, timestamp_to_extract, self.count[direction])
                            create_destination_directory(destination_directory)
                            save_frame(frame, output_path)

    def get_direction_timestamps(self, annotations_path):
        """
        Loads the timestamps
        """
        direction_timestamps = [[], [], []]
        with open(annotations_path, "rb") as fp:
            direction_timestamps = pickle.load(fp)
            print("Successfully read {}".format(annotations_path))
        return direction_timestamps


def parse_args():
    parser = argparse.ArgumentParser(description='Extract images for training from the video files')
    parser.add_argument('--video_dir', help='Path to directory that contains video files', required=True)
    parser.add_argument('--output_dir', help='Path to directory that contains video files', required=True)
    parser.add_argument('--num_frames', help='Number of frames to be extracted from each video sequence', required=True)
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    chunker = VideoChunker(num_frames=int(args.num_frames), output_dir=args.output_dir)
    video_paths = glob.glob(args.video_dir + '/*.MPG')

    for video_path in video_paths:
        annotations_path = video_path[:-4] + '.pkl'
        direction_timestamps = chunker.get_direction_timestamps(annotations_path)
        chunker.chunk_video(video_path, direction_timestamps)


if __name__ == '__main__':
    main()

    """
    Usage:
    python extract_images.py --video_dir "data/video_files" --output_dir "data/extracted_labeled_images" --num_frames 10
    """
