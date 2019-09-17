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
import datetime


class App:
    def __init__(self, window, window_title, video_path, media_db, cond_db):
        # Read image frames and defect timestamps from database
        self.video = Video(video_path, media_db, cond_db)
        self.defect_index = 0  # Index of defect image
        self.num_defects_in_video = len(self.video.defect_timestamps)  # Number of defects in a particular video
        self.defect_timestamps = [i for i, _ in self.video.defect_timestamps]  # List of [Timestamp, PACP_Code]
        self.defect_timestamp = self.defect_timestamps[self.defect_index]  # Which timestamp from the list we care about
        self.saved_time = "not saved"

        # Create the window
        self.window = window
        self.window.title(window_title)

        # Create some frames
        self.widget_labels_frame = tkinter.Frame(self.window)
        self.widget_labels_frame.pack(expand=True, anchor="nw")
        self.button_frame = tkinter.Frame(self.window)
        self.button_frame.pack(side=tkinter.LEFT, padx=5, pady=5, anchor="nw")
        self.button_height = 1
        self.button_width = 10
        self.image_frame = tkinter.Frame(self.window)
        self.image_frame.pack(expand=False, padx=5, pady=5, anchor="nw")

        # Widget labels
        self.label_buttons = tkinter.Label(self.widget_labels_frame, text="Activity Buttons", font=("", 14, "bold"), fg="dodgerblue3")
        self.label_buttons.grid(row=0, column=0, sticky="nsew", padx=45)
        self.label_image = tkinter.Label(self.widget_labels_frame, text="Image Frame", font=("", 14, "bold"), fg="dodgerblue3")
        self.label_image.grid(row=0, column=1, sticky="nsew", padx=110)
        self.label_listbox_left = tkinter.Label(self.widget_labels_frame, text="Left Timestamps", font=("", 14, "bold"), fg="dodgerblue3")
        self.label_listbox_left.grid(row=0, column=2, sticky="nsew", padx=47)
        self.label_listbox_straight = tkinter.Label(self.widget_labels_frame, text="Straight Timestamps", font=("", 14, "bold"), fg="dodgerblue3")
        self.label_listbox_straight.grid(row=0, column=3, sticky="nsew", padx=0)
        self.label_listbox_right = tkinter.Label(self.widget_labels_frame, text="Right Timestamps", font=("", 14, "bold"), fg="dodgerblue3")
        self.label_listbox_right.grid(row=0, column=4, sticky="nsew", padx=46)

        # Image widget
        self.canvas = tkinter.Canvas(self.image_frame, width=self.video.width, height=self.video.height)
        self.canvas.pack(side=tkinter.LEFT, padx=5, pady=5, anchor="nw")

        # Listboxes
        self.listbox_frame = tkinter.Frame(self.window)
        self.listbox_frame.pack(side=tkinter.LEFT, fill="both", expand=False, anchor="nw")

        self.listbox_left = tkinter.Listbox(self.image_frame, background="snow")
        self.listbox_left.pack(side=tkinter.LEFT, padx=5, pady=5, expand=False, fill="y")

        self.listbox_straight = tkinter.Listbox(self.image_frame, background="snow")
        self.listbox_straight.pack(side=tkinter.LEFT, padx=5, pady=5, expand=False, fill="y")

        self.listbox_right = tkinter.Listbox(self.image_frame, background="snow")
        self.listbox_right.pack(side=tkinter.LEFT, padx=5, pady=5, expand=False, fill="y")

        # Mark timestamp buttons
        self.btn_mark_left = tkinter.Button(self.button_frame, text="Left", height=self.button_height, width=self.button_width, command=self.update_listbox_left)
        self.btn_mark_left.grid(row=0, column=0, sticky="nsew", pady=5)

        self.btn_mark_straight = tkinter.Button(self.button_frame, text="Straight", height=self.button_height, width=self.button_width, command=self.update_listbox_straight)
        self.btn_mark_straight.grid(row=1, column=0, pady=5)

        self.btn_mark_right = tkinter.Button(self.button_frame, text="Right", height=self.button_height, width=self.button_width, command=self.update_listbox_right)
        self.btn_mark_right.grid(row=2, column=0, pady=5)

        self.btn_delete_left = tkinter.Button(self.button_frame, text="Delete", height=self.button_height, width=self.button_width, command=self.delete_listbox_left)
        self.btn_delete_left.grid(row=0, column=1, pady=5)

        self.btn_delete_straight = tkinter.Button(self.button_frame, text="Delete", height=self.button_height, width=self.button_width, command=self.delete_listbox_straight)
        self.btn_delete_straight.grid(row=1, column=1, pady=5)

        self.btn_delete_right = tkinter.Button(self.button_frame, text="Delete", height=self.button_height, width=self.button_width, command=self.delete_listbox_right)
        self.btn_delete_right.grid(row=2, column=1, pady=5)

        # Prev buttons
        self.btn_prev_jump = tkinter.Button(self.button_frame, text="<<< Jump", height=self.button_height, width=self.button_width, command=self.prev_jump)
        self.btn_prev_jump.grid(row=3, column=0, pady=5)

        self.btn_prev_step = tkinter.Button(self.button_frame, text="<<< Step", height=self.button_height, width=self.button_width, command=self.prev_step)
        self.btn_prev_step.grid(row=4, column=0, pady=5)

        self.btn_prev_micro = tkinter.Button(self.button_frame, text="<<< Micro", height=self.button_height, width=self.button_width, command=self.prev_micro_step)
        self.btn_prev_micro.grid(row=5, column=0, pady=5)

        # Next buttons
        self.btn_next_jump = tkinter.Button(self.button_frame, text="Jump >>>", height=self.button_height, width=self.button_width, command=self.next_jump)
        self.btn_next_jump.grid(row=3, column=1, pady=5)

        self.btn_next_step = tkinter.Button(self.button_frame, text="Step >>>", height=self.button_height, width=self.button_width, command=self.next_step)
        self.btn_next_step.grid(row=4, column=1, pady=5)

        self.btn_next_micro = tkinter.Button(self.button_frame, text="Micro >>>", height=self.button_height, width=self.button_width, command=self.next_micro_step)
        self.btn_next_micro.grid(row=5, column=1, pady=5)

        # Next image button
        self.btn_next_defect = tkinter.Button(self.button_frame, text="Next Defect", height=self.button_height, width=self.button_width, command=self.next_defect)
        self.btn_next_defect.grid(row=6, column=1, pady=5)

        self.btn_prev_defect = tkinter.Button(self.button_frame, text="Prev Defect", height=self.button_height, width=self.button_width, command=self.prev_defect)
        self.btn_prev_defect.grid(row=6, column=0, pady=5)

        # Save and close
        self.save = tkinter.Button(self.button_frame, text="Save", height=self.button_height, width=self.button_width, command=self.save)
        self.save.grid(row=7, column=0, pady=5)

        self.close = tkinter.Button(self.button_frame, text="Close", height=self.button_height, width=self.button_width, command=self.close)
        self.close.grid(row=7, column=1, pady=5)

        # Progress bar frame
        self.progress_text = tkinter.StringVar()  # Create label text
        self.progress_frame = tkinter.Frame(self.window)
        self.progress_frame.pack(padx=5, pady=5, anchor="ne")
        self.progress = tkinter.Label(self.progress_frame, textvariable=self.progress_text, font=("", 14, "bold"), fg="dodgerblue3")
        self.progress.grid(row=0, column=0, padx=5, pady=5)

        self.delay = 15
        self.update_progress_text()
        self.update_image()
        self.window.mainloop()

    def save(self):
        self.current_datetime = datetime.datetime.now()
        print(f"Saved at {self.current_datetime}")
        self.saved_time = self.current_datetime
        self.video.save_direction_timestamps()

    def close(self):
        print("Program exited correctly")
        self.window.destroy()

    def update_listboxes(self):
        self.listbox_left.delete(0, tkinter.END)
        self.listbox_straight.delete(0, tkinter.END)
        self.listbox_right.delete(0, tkinter.END)

        for i in self.video.direction_timestamps[0]:
            self.listbox_left.insert(tkinter.END, i)
        for i in self.video.direction_timestamps[1]:
            self.listbox_straight.insert(tkinter.END, i)
        for i in self.video.direction_timestamps[2]:
            self.listbox_right.insert(tkinter.END, i)

    def update_listbox_left(self):
        self.video.direction_timestamps[0].append(self.defect_timestamp)
        self.update_listboxes()

    def update_listbox_straight(self):
        self.video.direction_timestamps[1].append(self.defect_timestamp)
        self.update_listboxes()

    def update_listbox_right(self):
        self.video.direction_timestamps[2].append(self.defect_timestamp)
        self.update_listboxes()

    def delete_listbox_left(self):
        self.video.direction_timestamps[0] = self.video.direction_timestamps[0][:-1]
        self.update_listboxes()

    def delete_listbox_straight(self):
        self.video.direction_timestamps[1] = self.video.direction_timestamps[1][:-1]
        self.update_listboxes()

    def delete_listbox_right(self):
        self.video.direction_timestamps[2] = self.video.direction_timestamps[2][:-1]
        self.update_listboxes()

    # Functions to traverse frames
    def next_micro_step(self):
        self.defect_timestamp = self.defect_timestamp + 0.05

    def next_step(self):
        self.defect_timestamp = self.defect_timestamp + 0.1

    def next_jump(self):
        self.defect_timestamp = self.defect_timestamp + 1

    def prev_micro_step(self):
        self.defect_timestamp = self.defect_timestamp - 0.05

    def prev_step(self):
        self.defect_timestamp = self.defect_timestamp - 0.1

    def prev_jump(self):
        self.defect_timestamp = self.defect_timestamp - 1

    def next_defect(self):
        self.defect_index = self.defect_index + 1
        self.defect_index = min(self.defect_index, self.num_defects_in_video - 1)  # Don't let it go beyond max
        self.defect_timestamp = self.defect_timestamps[self.defect_index]

    def prev_defect(self):
        self.defect_index = self.defect_index - 1
        self.defect_index = max(0, self.defect_index)  # Don't let it go below 0
        self.defect_timestamp = self.defect_timestamps[self.defect_index]

    # Function to update image
    def update_image(self):
        ret, frame = self.video.get_frame(self.defect_timestamp * 1000)
        # Convert cv2 image into PIL image
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tkinter.NW)
        self.window.after(self.delay, self.update_image)

    def update_progress_text(self):
        text = str(f"Defect {self.defect_index + 1} out of {self.num_defects_in_video}    |    Saved at: {self.saved_time}")
        self.progress_text.set(text)
        self.progress.after(self.delay, self.update_progress_text)

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
