# -*- coding: utf-8 -*-
from ImageFile import Parser as ImageFileParser

def read_image_file(file):
    parser = ImageFileParser()
    parser.feed(file.read())
    return parser.close()
