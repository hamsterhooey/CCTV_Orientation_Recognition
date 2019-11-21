"""

Create empty xml training annotations for images with no objects

"""

import os
import glob
import argparse


def create_empty_xml(image_dir, xml_template):

    for jpg_im in os.listdir(image_dir):
        if jpg_im[-4:] == '.jpg':
            if xml_exists(image_dir, jpg_im) == False:

                with open(xml_template, 'r') as f:
                    newText = f.read()
                    newText = newText.replace('insertfilenamehere.jpg', jpg_im)
                    f.close()

                with open(image_dir + '/' + jpg_im[:-4] + '.xml', "w") as annotation_file:
                    annotation_file.write(newText)
                    annotation_file.close()
    return


def xml_exists(image_dir, jpg_im):
    flag = False
    for xmlfile in os.listdir(image_dir):
        if xmlfile[-4:] == '.xml':

            if xmlfile[:-4] == jpg_im[:-4]:
                flag = True
                break
    return flag


def parse_args():
    parser = argparse.ArgumentParser(description='Create empty xml annotation files')
    parser.add_argument('--image_dir', help='Path to directory that contains video files', required=True)
    parser.add_argument('--xml_template', help='Path to empty xml template that will be replicated', required=True)
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    xml_template = args.xml_template
    image_dir = os.path.join(os.getcwd(), '{}'.format(args.image_dir))
    create_empty_xml(image_dir, xml_template)
    print('Successfully created empty annotation files')


if __name__ == "__main__":
    main()

"""
python create_empty_xml.py --image_dir "data/localize_by_joint/extracted" --xml_template "empty_xml_template.xml"
"""
