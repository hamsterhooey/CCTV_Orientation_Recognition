# Project Title

Orientation recognition of CCTV camera using deep action recognition.

## Getting Started

annotate_videos.py is used to create annotations in videos.
An example of an annotation is: ('left', 10800, 11800). This indicates that the video segment between 108sec and 118sec contained a left turn. First, we annotate multiple videos. Next, we run extract_images.py

extract_images.py reads the annotations and extracts image sequences from the video files. For example, extract_images.py can be used to extract 30 image frames from the previous annotation, i.e., ('left', 10800, 11800)

Note: You need the inspection video files and the inspection database to execute the above two programs.

Sample extracted training images can be found in: data/extracted_labeled_images

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
* **Jianna Cai** - [jiannan0721](https://github.com/jiannan0721)
