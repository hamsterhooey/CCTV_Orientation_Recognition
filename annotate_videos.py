import os
import sys
import csv
import cv2
import argparse
import glob
import pickle
import pandas as pd
import subprocess as sp
from tqdm import tqdm
from tqdm import trange


class Video:
    def __init__(self):
        self.direction_timestamps = [[], [], []]  # Left, center, right

    def initialize_for_annotation(self, video_path, media_db, cond_db):
        self.set_video_path(video_path)
        self.set_filename_from_path(video_path)
        self.set_inspection_id_from_media(media_db)
        self.set_defect_timestamps_from_cond(cond_db)

    def set_video_path(self, video_path):
        self.video_path = video_path

    def set_filename_from_path(self, video_path):
        self.filename = os.path.split(video_path)[-1]

    def set_inspection_id_from_media(self, media_db):
        self.df_media = pd.read_csv(media_db)
        self.df_media = self.df_media.loc[self.df_media['Video_Name'] == self.filename]
        self.inspection_id = self.df_media['InspectionID'].values.tolist()[0]

    def set_defect_timestamps_from_cond(self, cond_db):
        self.df_cond = pd.read_csv(cond_db)
        self.df_cond = self.df_cond.loc[self.df_cond['InspectionID'] == self.inspection_id]
        self.defect_timestamps = self.df_cond[['Counter', 'PACP_Code']].values.tolist()

    def display_marked(self):
        print('\nNew Timestamps for {}'.format(self.filename))
        print('---------------')
        print('Left Timestamps:\t{}'.format(self.direction_timestamps[0]))
        print('Center Timestamps:\t{}'.format(self.direction_timestamps[1]))
        print('Right Timestamps:\t{}'.format(self.direction_timestamps[2]))

    def save_direction_timestamps(self):  # Save as pickle as well as a CSV
        with open(self.video_path[:-4] + '.pkl', "wb") as fp:
            pickle.dump(self.direction_timestamps, fp)

        with open(self.video_path[:-4] + '.csv', "w", newline="") as fp:
            writer = csv.writer(fp)
            writer.writerow(self.direction_timestamps)

    def mark_timestamps(self, timestamp):
        # Open the video file
        cap = cv2.VideoCapture(self.video_path)
        cv2.namedWindow(self.filename)
        cv2.moveWindow(self.filename, 250, 150)

        mark_frame = [97, 115, 100]  # a, s, and d to mark frame
        delete_marked = [122, 120, 99]  # z, x, and c to delete marked

        while True:
            cap.set(cv2.CAP_PROP_POS_MSEC, timestamp)
            ret, frame = cap.read()
            key = cv2.waitKey(1)
            cv2.imshow(self.filename, frame)

            if key == ord('n'):  # Next image
                break

            if key == ord('q'):
                sys.exit()

            elif key == ord('1'):
                timestamp += -100

            elif key == ord('2'):
                timestamp += 100

            elif key == ord('3'):
                timestamp += -2000

            elif key == ord('4'):
                timestamp += 2000

            elif key in mark_frame:
                self.direction_timestamps[mark_frame.index(key)].append(timestamp)
                self.display_marked()

            elif key in delete_marked:
                delete_index = delete_marked.index(key)
                self.direction_timestamps[delete_index] = self.direction_timestamps[delete_index][:-1]
                self.display_marked()

        cap.release()
        cv2.destroyAllWindows()


def parse_args():
    parser = argparse.ArgumentParser(description="Annotate CCTV videos for training")
    parser.add_argument("--media_db", help="Path to CSV file listing media inspections")
    parser.add_argument("--cond_db", help="Path to CSV file containing condition IDs")
    parser.add_argument("--video_path", help="Path to the video file")
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    video = Video()
    video.initialize_for_annotation(args.video_path, args.media_db, args.cond_db)
    for defect_timestamp, pacp_code in tqdm(video.defect_timestamps, desc='PACP defects in video'):
        video.mark_timestamps(defect_timestamp * 1000)
    video.save_direction_timestamps()

    """
    Usage:

python annotate_videos.py --media_db "data/video_databases/Media_Inspections.csv" --cond_db "data/video_databases/Conditions.csv" --video_path "data/video_files/3.MPG"
    """


if __name__ == "__main__":
    main()
