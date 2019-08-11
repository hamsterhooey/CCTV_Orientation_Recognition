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

    def get_slices():
        pass

    def get_output_path(self, video_path, direction, timestamp, sequence_id):
        output_filename = str(sequence_id) + '_' + os.path.split(video_path)[-1][:-4] + '_' + direction + '_' + str(int(timestamp)) + '.png'
        output_path = os.path.join(self.output_dir, output_filename)
        return output_path

    def save_frame(self, frame, output_path):
        cv2.imwrite(output_path, frame)
        print('Saved: {}'.format(output_path))

    def extract_frame(self, cap, timestamp):
        cap.set(cv2.CAP_PROP_POS_MSEC, timestamp)
        ret, frame = cap.read()
        return ret, frame  # ret: False when frame isn't read

    def chunk_video(self, video_path, direction_timestamps):  # Annotations are in pickle format
        cap = cv2.VideoCapture(video_path)
        directions = {0: 'left', 1: 'straight', 2: 'right'}
        for key in directions.keys():
            sequence_id = 0
            direction = directions[key]
            # direction_timestamps[0] is all the left timestamps
            direction_timestamp = direction_timestamps[key]

            if len(direction_timestamp) % 2 != 0:
                return

            # Extract timestamps between timestamp1 and timestamp2 at chunk_interval
            for i in range(0, len(direction_timestamp), 2):
                sequence_id += 1
                timestamp1 = int(direction_timestamp[i])
                timestamp2 = int(direction_timestamp[i + 1])
                timestamps_to_extract = [t for t in range(timestamp1, timestamp2, self.chunk_interval)]

                for timestamp_to_extract in timestamps_to_extract:
                    ret, frame = self.extract_frame(cap, timestamp_to_extract)
                    if ret:
                        output_path = self.get_output_path(video_path, direction, timestamp_to_extract, sequence_id)
                        self.save_frame(frame, output_path)

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
