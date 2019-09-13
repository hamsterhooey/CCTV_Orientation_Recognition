import os
import sys
import csv
import cv2
import PIL.Image
import PIL.ImageTk
import argparse
import glob
import pickle
import pandas as pd
import subprocess as sp
from tqdm import tqdm
from tqdm import trange
import tkinter


class App:
    def __init__(self, window, window_title, video_path, media_db, cond_db):
        # Read frames from database
        self.video = Video(video_path, media_db, cond_db)
        for self.defect_timestamp, self.pacp_code in tqdm(self.video.defect_timestamps[:1], desc='PACP defects in video'):
            pass

        # Create label text
        self.label_text = tkinter.StringVar()

        # Create the window
        self.window = window
        self.window.title(window_title)

        self.canvas = tkinter.Canvas(self.window, width=self.video.width, height=self.video.height)
        self.canvas.pack()

        self.button_frame = tkinter.Frame(self.window)
        self.button_frame.pack(side="bottom", fill="x", expand=False)

        # Display timestamp
        self.start_label = tkinter.Label(self.window, width=10, textvariable=self.label_text)
        self.start_label.pack(padx=5, pady=5)

        # Mark timestamp buttons
        self.btn_mark_left_start = tkinter.Button(self.button_frame, text="Left Start", width=10, command=self.update_labels)
        self.btn_mark_left_start.grid(row=0, column=0)

        self.btn_mark_left_end = tkinter.Button(self.button_frame, text="Left End", width=10, command=self.update_labels)
        self.btn_mark_left_end.grid(row=0, column=1)

        self.btn_mark_right_start = tkinter.Button(self.button_frame, text="Right Start", width=10, command=self.update_labels)
        self.btn_mark_right_start.grid(row=0, column=2)

        self.btn_mark_right_end = tkinter.Button(self.button_frame, text="Right End", width=10, command=self.update_labels)
        self.btn_mark_right_end.grid(row=0, column=3)

        # Prev buttons
        self.btn_prev_jump = tkinter.Button(self.button_frame, text="Prev Jump", width=10, command=self.prev_jump)
        self.btn_prev_jump.grid(row=1, column=0)

        self.btn_prev_step = tkinter.Button(self.button_frame, text="Prev Step", width=10, command=self.prev_step)
        self.btn_prev_step.grid(row=1, column=1)

        # Next buttons
        self.btn_next_step = tkinter.Button(self.button_frame, text="Next Step", width=10, command=self.next_step)
        self.btn_next_step.grid(row=1, column=2)

        self.btn_next_jump = tkinter.Button(self.button_frame, text="Next Jump", width=10, command=self.next_jump)
        self.btn_next_jump.grid(row=1, column=3)

        self.delay = 15

        self.update_image()
        self.window.mainloop()

    def update_labels(self):
        self.label_text.set(str(round(self.defect_timestamp, 2)))
        # self.start_label.after(self.delay, self.update_labels)

    # Functions to traverse frames
    def next_step(self):
        self.defect_timestamp = self.defect_timestamp + 0.1

    def next_jump(self):
        self.defect_timestamp = self.defect_timestamp + 1

    def prev_step(self):
        self.defect_timestamp = self.defect_timestamp - 0.1
        print("Previous Frame")

    def prev_jump(self):
        self.defect_timestamp = self.defect_timestamp - 1

    # Function to update image
    def update_image(self):
        ret, frame = self.video.get_frame(self.defect_timestamp * 1000)
        # Convert cv2 image into PIL image
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tkinter.NW)
        self.window.after(self.delay, self.update_image)

    # TODO:
    # Create list of recorded timestamps
    # Jump to image based on clicked timestamp
    # Integrate with annotate_images


class Video:
    def __init__(self, video_path, media_db, cond_db):
        self.direction_timestamps = [[], [], []]  # Left, center, right
        self.video_path = video_path
        self.filename = os.path.split(video_path)[-1]
        self.inspection_id = self.get_inspection_id_from_media(media_db)
        self.defect_timestamps = self.get_defect_timestamps_from_cond(cond_db)
        # Open the video file
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            raise ValueError("Unable to open video source", self.video_path)
        self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def get_inspection_id_from_media(self, media_db):
        self.df_media = pd.read_csv(media_db)
        self.df_media = self.df_media.loc[self.df_media['Video_Name'] == self.filename]
        return self.df_media['InspectionID'].values.tolist()[0]

    def get_defect_timestamps_from_cond(self, cond_db):
        self.df_cond = pd.read_csv(cond_db)
        self.df_cond = self.df_cond.loc[self.df_cond['InspectionID'] == self.inspection_id]
        return self.df_cond[['Counter', 'PACP_Code']].values.tolist()

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

    def get_frame(self, timestamp):
        self.cap.set(cv2.CAP_PROP_POS_MSEC, timestamp)
        self.ret, self.frame = self.cap.read()
        if not self.ret:
            self.frame = None
        return self.ret, self.frame


def parse_args():
    parser = argparse.ArgumentParser(description="Annotate CCTV videos for training")
    parser.add_argument("--media_db", help="Path to CSV file listing media inspections")
    parser.add_argument("--cond_db", help="Path to CSV file containing condition IDs")
    parser.add_argument("--video_path", help="Path to the video file")
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    app = App(tkinter.Tk(), "Tkinter OpenCV", args.video_path, args.media_db, args.cond_db)
    # for defect_timestamp, pacp_code in tqdm(video.defect_timestamps[:2], desc='PACP defects in video'):
    #     video.get_frame(defect_timestamp * 1000)


if __name__ == "__main__":
    main()
