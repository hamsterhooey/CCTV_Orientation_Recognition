import os
import cv2
import argparse

# Return duration of video in MSEC


def get_video_length(video_path):
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_AVI_RATIO, 1)
    return cap.get(cv2.CAP_PROP_POS_MSEC)


def create_destination_directory(destination_directory):
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)


def save_frame(frame, time, output_dir):
    save_name = str(time) + '.jpg'
    output_path = os.path.join(output_dir, save_name)
    create_destination_directory(output_dir)
    cv2.imwrite(output_path, frame)
    print('Saved: {}'.format(output_path))


def video_to_images(video_path, time_interval, offset, output_dir):
    cap = cv2.VideoCapture(video_path)
    for time in range(int(offset), int(get_video_length(video_path)), int(time_interval)):
        cap = cv2.VideoCapture(video_path)
        cap.set(cv2.CAP_PROP_POS_MSEC, time)
        ret, frame = cap.read()
        save_frame(frame, time, output_dir)

    return True


def parse_args():
    parser = argparse.ArgumentParser(description='Extract images from a video')
    parser.add_argument('--video_path', help='Path to directory with videos', required=True)
    parser.add_argument('--time_interval', help='Time interval between consecutive frames in milliseconds', required=True)
    parser.add_argument('--offset', help='Offset in milliseconds', required=True)
    parser.add_argument('--output_dir', help='Directory to store images', required=True)
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    video_to_images(args.video_path, args.time_interval, args.offset, args.output_dir)


if __name__ == "__main__":
    main()

"""
Example usage:
python video_to_frames.py --video_path "localize_by_joint" --time_interval 1000 --offset 60000


"""
