# Project Title

Sensing the camera-pose of a sewer-inspection robot using vision-based methods.

## Project Overview

Underground sewers are GPS-denied environments. Hence, we use a vision-based method to determine the location of autonomous robots in pipes. The project consists of three parts: (1) extraction and annotation of images for training an object detection model, (2) training a Faster R-CNN object detection model to detect the vanishing points and joints in sewer inspection videos, and (3) using the results of inference (i.e., joint and vanishing point detection) to calculate the position of the robot.


### Extraction and annotation of images

Please see annotated_images.py. It runs a Tkinter-based tool to mark events in a video. Events represent the start and end of a particular feature appearing in the video. For instance, marking the start and end of an event which involves the camera making a turn.

Please see annotated_images.py. It runs a Tkinter-based tool to mark events in a video. Events represent the start and end of a particular feature appearing in the video. For instance, marking the start and end of an event which involves the camera making a turn.

Once a video has been marked, extract_images.py reads the marked events and extracts images between the marked time intervals. For instance if an event is marked at 10 seconds and 15 seconds, then extract_images.py can be used to extract multiple images in this time interval.

The extracted images are then labeled with bounding boxes using the LabelImg tool (github:Tzuatlin).

![alt text](https://github.com/hamsterhooey/CCTV_Orientation_Recognition/blob/master/images/Step%201.jpg)

### Training a model to detect vanishing points and joints

We then use tensorflow object detection api to train a Faster R-CNN model. We make use of the numerous utils provided by tensorflow to accomplish this.

[embed](https://github.com/hamsterhooey/CCTV_Orientation_Recognition/blob/master/images/Step%202.jpg)[/embed]

### Inference on videos to detect joint and vanishing points

We then run the inference script located in the "models" folder, to load the frozen tensorflow model and process frames of an input video.

![alt text](https://github.com/hamsterhooey/CCTV_Orientation_Recognition/blob/master/images/Step%203.jpg)

### Example Usage

```
python annotate_videos.py --media_db "data/video_databases/Media_Inspections.csv" --cond_db "data/video_databases/Conditions.csv" --video_path "data/video_files/3.MPG"
```
```
python extract_images.py --video_dir "data/video_files" --output_dir "data/extracted_labeled_images" --num_frames 10
```

### Prerequisites

Tested using opencv3.4.2

## Authors

* **Srinath Shiv Kumar** - [hamsterhooey](https://github.com/hamsterhooey)
