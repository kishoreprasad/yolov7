import cv2
import argparse
import numpy as np
import glob
import os
import types
import subprocess
from os.path import join
import tqdm
import PIL as pillow

ST_RES = 1440

def generate_thumbnails(args):
    """Function to generate thumbnails of the images in the output folder
    """
    # read all the images in the output folder
    imgs = [cv2.imread(file) for file in glob.glob(join(args.output, "*.JPG"))]
    # get the names of the images
    img_names = [os.path.basename(x) for x in glob.glob(join(args.output, "*.JPG"))]
    # create a thumbnails folder if it doesn't exist
    if not os.path.exists(join(args.output, "thumbnails")):
        os.mkdir(join(args.output, "thumbnails"))
    # resize the images and save them in the thumbnails folder
    for i in range(len(imgs)):
        img = imgs[i]
        img = img.resize((128,128),pillow.Image.ANTIALIAS)
        cv2.imwrite(join(args.output, "thumbnails", img_names[i]), img)

def combine_stride(height, width, channels):
    """Function to combine the images from the temporary folder
    Args:
        height (int): height of the image
        width (int): width of the image
        channels (int): number of channels in the image
    Returns:
        img (numpy array): combined image
    """
    # read all the images in the folder
    imgs_stride = [cv2.imread(file) for file in sorted(glob.glob(join(args.output, "tmp", "*.JPG")))]
    # create a numpy array of zeros with the same size as the original image
    img = np.zeros((height, width, channels))
    # combine the images
    k=0
    for i in range(0, width, ST_RES):
        for j in range(0, height, ST_RES):
            img[j : j + ST_RES, i : i + ST_RES] = imgs_stride[k]
            # img[]
            k+=1
    return img


def create_strides(img, args, height, width):
    """Function to split the image into number of parts, saving them in the temporary folder and
    running the YOLO model on each of the parts by calling the detect.py file
    Args:
        args (list): list of arguments
        img (numpy array): image to split
        height (int): height of the image
        width (int): width of the image
    """
    # create an empty list to store the images
    imgs_stride = list()
    # split the image into number of parts and append them to the list
    for i in range(0, width, ST_RES):
        for j in range(0, height, ST_RES):
            imgs_stride.append(img[j : j + ST_RES, i : i + ST_RES])
    # save the images in the temporary folder
    for i in range(len(imgs_stride)):
        cv2.imwrite(join(args.output, "tmp", "img" + str(i) + ".JPG"), imgs_stride[i])


def run_with_strides(args):
    # read all the images in the folder
    imgs = [cv2.imread(file) for file in glob.glob(join(args.source, "*.JPG"))]
    # get the names of the images
    img_names = [os.path.basename(x) for x in glob.glob(join(args.source, "*.JPG"))]
    # create an output folder if it doesn't exist
    if not os.path.exists(args.output):
        os.mkdir(args.output)
    # create a temporary folder to store the images if it doesn't exist
    if not os.path.exists(join(args.output, "tmp")):
        os.mkdir(join(args.output, "tmp"))
    # run the model on each of the images
    for i in tqdm.tqdm(range(len(imgs)),desc ="Processing Images"):
        #display the progress
        tqdm.tqdm.write(f"Processing image {i+1}/{len(imgs)}")
        # get the image
        img = imgs[i]
        # get the height, width and number of channels of the image
        height, width, channels = img.shape
        # split the image into number of parts
        create_strides(img, args, height, width)
        # run the model on each of the parts
        subprocess.call(
            f"python3 {args.yolo}/detect.py --weights {args.weights}/best.pt --conf {args.conf} --source {args.output}/tmp --project {args.output}/tmp",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        # combine the images
        combined_img = combine_stride(height, width, channels)
        # save the combined image
        cv2.imwrite(join(args.output, img_names[i]), combined_img)


if __name__ == "__main__":
    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("--strides",help="If strides is True, the image is split into number of parts and then merged back together.",action="store_true",default=False)
    ap.add_argument("-w", "--weights", required=False, help="path to weights file",default=".")
    ap.add_argument("-s","--source", required=True, help="path to source")
    ap.add_argument("-o","--output", required=True, help="path to output")
    ap.add_argument(
        "--conf", type=float, default=0.5, help="object confidence threshold"
    )
    ap.add_argument("-y","--yolo", required=True, help="path to yolo folder",default=".")
    ap.add_argument("-t","--thumbnails", required=False, help="path to thumbnails",default=True)
    args = ap.parse_args()
    if(args.weights=="."):
        args.weights=args.yolo
    if args.strides == True:
        print("executing with strides")
        run_with_strides(args)
        # remove the temporary folder and its contents
        os.system("rm -r " + args.output + "/tmp")
        if args.thumbnails == "True":
            generate_thumbnails(args)

    else:
        print("executing without strides")
        subprocess.call(
            f"python3 {args.yolo}/detect.py --weights {args.weights}/best.pt --conf {args.conf} --source {args.source} --project {args.output}",
            shell=True
        )
        if args.thumbnails == "True":
            generate_thumbnails(args)