"""
Extract images for training, from annotated videos
The annotations are stored in pkl and csv files
"""

import argparse
import tqdm
import cv2
import glob
import os
import pickle
from tqdm import tqdm
from tqdm import trange

from annotate_videos import Video

# Chunker


class VideoChunker():

    def __init__(self, chunk_interval=100, output_dir="data/extracted_labeled_images"):
        self.chunk_interval = chunk_interval
        self.output_dir = output_dir

    def save_frame(self, cap, video_path, direction_timestamp, direction):
        cap.set(cv2.CAP_PROP_POS_MSEC, direction_timestamp)
        ret, frame = cap.read()
        output_filename = os.path.split(video_path)[-1][:-4] + '_' + direction + '_' + str(int(direction_timestamp)) + '.png'
        if ret:
            output_path = os.path.join(self.output_dir, output_filename)
            cv2.imwrite(output_path, frame)
            print('Saved: {}'.format(output_path))

    def chunk_video(self, video_path, direction_timestamps):  # Annotations are in pickle format
        # Left
        cap = cv2.VideoCapture(video_path)
        for direction_timestamp in direction_timestamps[0]:  # Left directions
            self.save_frame(cap, video_path, direction_timestamp, 'left')

    def get_direction_timestamps(self, annotations_path):
        direction_timestamps = [[], [], []]
        with open(annotations_path, "rb") as fp:
            direction_timestamps = pickle.load(fp)
            print("Successfully read {}".format(annotations_path))
        return direction_timestamps


def parse_args():
    parser = argparse.ArgumentParser(description='Extract images for training from the video files')
    parser.add_argument('--video_dir', help='Path to directory that contains video files', required=True)
    parser.add_argument('--output_dir', help='Path to directory that contains video files', required=True)
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    video_paths = glob.glob(args.video_dir + '/*.MPG')
    annotations_paths = [video_path[:-4] + '.pkl' for video_path in video_paths]
    chunker = VideoChunker()
    direction_timestamps = chunker.get_direction_timestamps(annotations_paths[0])
    chunker.chunk_video(video_paths[0], direction_timestamps)
    # for video_file in glob.glob(video_dir + '/*.pkl'):


if __name__ == '__main__':
    main()

    """
    Usage:

    python extract_images.py --video_dir "data/video_files" --output_dir "data/extracted_labeled_images"
    """
