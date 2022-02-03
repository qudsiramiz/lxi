#!/home/cephadrius/pyspedas/bin/python
# -*- coding: utf-8 -*-

import datetime
import glob as glob
import os
import time

import imageio as iio
import numpy as np


def gif_maker(file_list, vid_name, mode="I", skip_rate=10, vid_type="mp4", duration=0.05, fps=25):
    """
    Make a gif from a list of images.
    
    Parameters
    ----------
    file_list : list
        List of image files.
    vid_name : str
        Name of the gif file.
    mode : str, optional
        Mode of the gif. The default is "I".
    skip_rate : int, optional
        Skip rate of the gif. The default is 10.
    vid_type : str, optional
        Type of the video. The default is "mp4".
    duration : float, optional
        Duration for which each image is displayed in gif. The default is 0.05.
    fps : int, optional
        Frames per second for mp4 video. The default is 25.

    Raises
    ------
    ValueError
        If the skip_rate is not an integer.
    ValueError
        If the duration is not a float.
    ValueError
        If the file_list is empty.
    ValueError
        If vid_name is empty.

    Returns
    -------
    None.
    """
    if file_list is None:
        raise ValueError("file_list is None")
    if vid_name is None:
        raise ValueError("vid_name is None. Please provide the name of the gif/video")
    if len(file_list) == 0:
        raise ValueError("file_list is empty")
    if len(file_list) >= 1501:
        # Check if the skip_rate is an integer
        if skip_rate != int(skip_rate):
            raise ValueError("skip_rate must be an integer")
        file_list = file_list[-1500::skip_rate]
    if vid_type == "gif":
        if duration != float(duration):
            raise ValueError("duration must be a float")
    if vid_type == "mp4":
        if fps != int(fps):
            raise ValueError("Frame rate (fps) must be an integer")

    count = 0
    if vid_type == "gif":
        with iio.get_writer(vid_name, mode=mode, duration=duration) as writer:
            for file in file_list:
                count += 1
                print(f"Processing image {count} of {len(file_list)}")
                image = iio.imread(file)
                writer.append_data(image)
    elif vid_type == "mp4":
        with iio.get_writer(vid_name, mode=mode, fps=fps) as writer:
            for filename in file_list:
                count += 1
                print(f"Processing image {count} of {len(file_list)}")
                img = iio.imread(filename)
                writer.append_data(img)
    writer.close()

    print(f"{vid_name} is created\n")


def make_gifs(
    img_folder="/home/cephadrius/Desktop/git/lxi/figures/",
    vid_folder="/home/cephadrius/Desktop/git/lxi/figures/",
    particle_number= 0,
    vid_name="0000",
    vid_type="mp4",
    skip_rate=1,
    duration=0.05,
    fps=25,
    search_recursive=True
    ):
    """
    Make gifs for the last n days. Default is 120 days, averaged over the last 30 days.

    Parameters
    ----------
    img_folder : str, optional
        Folder where the images are stored. The default is
        "/home/cephadrius/Desktop/git/lxi/figures/".
    vid_folder : str, optional
        Folder where the gifs are stored. The default is
        "/home/cephadrius/Desktop/git/lxi/figures/".
    particle_number : int, optional
        Particle number. The default is 0.
    vid_name : str, optional
        Name of the gif file. The default is "0000".
    vid_type : str, optional
        Type of the video. The default is "mp4".
        options: "gif" and "mp4".
    skip_rate : int, optional
        Skip rate of the video. The default is 1. If it is set to 1 then every image is file used to
        create the video. If it is set to 2 then every other image is used to create the video and
        so on. Please NOTE that the skip_rate must be an integer and is only considered if the
        total number of images is greater than 1500.
    duration : float, optional
        Duration for which each image is displayed in gif. The default is 0.05.
    fps : int, optional
        Frames per second for mp4 video. The default is 25.
    search_recursive : bool, optional
        Search for files recursively in each folder and subfolders. The default is True.

    Returns
    -------
        A dictionary with all the files used for creating the video.
    """

    print(f"Code execution started at (UTC):" +
          f"{datetime.datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')}\n")

    file_list_dict = {}
    if search_recursive:
        # Search for all the files in the folder and subfolders recursively and store them in a
        # dictionary sorted by the modified date of the file.
        fl = filter(os.path.isfile, glob.glob(img_folder + "/**/*.png", recursive=search_recursive))
        file_list_dict["file_list"] = sorted(fl, key=os.path.getctime)
    else :
        if isinstance(particle_number, (list, np.ndarray)):
            for particle in particle_number:
                file_list_dict[f"{particle}"] = np.sort(glob.glob(
                    f"{img_folder}/{str(particle).zfill(5)}/*.png"))
        elif not isinstance(particle_number, (list, np.ndarray)):
            file_list_dict[f"{str(particle_number).zfill(5)}"] = np.sort(glob.glob(
                                             f"{img_folder}/{str(particle_number).zfill(5)}/*.png"))

    for i,key in enumerate(list(file_list_dict.keys())):
        print(key, i)
        vid_name = f"{vid_folder}{vid_name}_particleNumber_{str(key).zfill(5)}_{fps}fps.mp4"
        try:
            gif_maker(file_list_dict[key], vid_name, mode="I", skip_rate=skip_rate,
                      vid_type=vid_type, fps=fps, duration=duration)
        except ValueError as e:
            print(e)
            pass
    return file_list_dict

image_inputs = {
    "img_folder":"/home/cephadrius/Desktop/git/lxi/figures/",
    "vid_folder":"/home/cephadrius/Desktop/git/lxi/figures/",
    "particle_number": [684],
    "vid_name":"particle_trajectories",
    "vid_type":"mp4",
    "skip_rate":1,
    "duration":0.05,
    "fps":15,
    "search_recursive":True
}
file_list = make_gifs(**image_inputs)
