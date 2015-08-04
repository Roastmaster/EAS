from client_create import create_swift_client
from converter import Converter
import subprocess
import json
import os


def find_num_frames(frame_type, filename):
    """Find and return the number of frames of a given type
    Valid frame_types are 'I', 'P', and 'B'.
    """
    command = ('ffprobe -loglevel quiet -show_frames ' + filename + ' | ' +
               'grep pict_type=' + frame_type + ' | wc -l')
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    return int(process.stdout.read())


def ingest(path, credentials):
    if os.path.isdir(path):
        ingest_directory(path, credentials)

    elif os.path.isfile(path):
        ingest_file(path, credentials)

    else:
        raise IOError('Location not valid file or folder')


def ingest_directory(directory, credentials):
    for filename in os.listdir(directory):
        if not filename.endswith('.py'):
            ingest_file(filename, credentials)


def ingest_file(filename, credentials):
    index = generate_index(filename)
    write_file(filename, credentials)


def generate_index(filename):
    info = Converter.probe(filename)
    index = dict()

    index['i frames'] = find_num_frames('I', filename)
    index['b frames'] = find_num_frames('B', filename)
    index['p frames'] = find_num_frames('P', filename)
    index['duration'] = info.format.duration
    index['width'] = info.video.video_width
    index['height'] = info.video.video_height
    index['format'] = info.format.format
    index['fps'] = info.video.video_fps
    index['v codec'] = info.video.codec
    index['a codec'] = info.audio.codec

    return index


def write_file(filename, credentials, container='videos', type='video'):
    swift = create_swift_client(credentials)
    with open(filename, 'rb') as f:
        swift.put_object(container, filename, contents=f,
                         content_type=type)


def write_index(filename, index_file='index.json'):
    try:
        json.load(index_file)
    except ValueError: