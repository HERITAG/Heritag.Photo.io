#!/usr/bin/env python3
import glob, os
import pyexiv2
from PIL import Image

ORIGINAL_IMAGE_PATH = os.path.normpath(os.path.normpath(f'{os.path.join(os.getcwd(), "../test_images")}'))
PROCESSED_IMAGE_PATH = os.path.normpath(os.path.normpath(f'{os.path.join(os.getcwd(), "../test_images/processed")}'))
# ORIGINAL_IMAGE_PATH = os.path.normpath(
#     os.path.normpath('/mnt/backupaninstancedatacenter/family-history-29032019-clone/IMAGE_ARCHIVE/InProgress'))
# PROCESSED_IMAGE_PATH = os.path.normpath(
#     os.path.normpath('/mnt/backupaninstancedatacenter/family-history-29032019-clone/IMAGE_ARCHIVE/Processed'))
CONVERSION_FORMAT = 'jpg'


class ProcessImages:
    """
    Processes images by:
        - convert image format (e.g. .tif to .jpg)
        - read & transfer IPTC 'keyword' tags from original to converted image
    """

    ALLOWED_CONVERSION_FORMATS = ['jpeg', 'jpg', 'tiff', 'tif', 'png']

    def __init__(self, image_path=None, processed_image_path=None, conversion_format=None, reconvert=False,
                 retag=False):
        """
        initiate the class
        :param image_path: path of the image to be converted and/or tagged
        :param processed_image_path: path to save the processed image to
        :param conversion_format: file format to convert image to
        :param reconvert: boolean value, signifying whether to perform conversion
            if the image name already exists in the defined location where
            converted & tagged images are saved.
        :param retag: boolean value, signifying whether to perform tagging
            if the image name already exists in the defined location where
            converted & tagged images are saved.
        """
        self.ORIGINAL_IMAGE_PATH = image_path
        self.PROCESSED_IMAGE_PATH = processed_image_path
        self.CONVERSION_FORMAT = conversion_format if conversion_format.lower() in self.ALLOWED_CONVERSION_FORMATS \
            else 'jpg'
        self.retag = retag if isinstance(retag, bool) else False
        self.reconvert = reconvert if isinstance(reconvert, bool) else False

    @staticmethod
    def read_iptc_tags(filename, path):
        """
        method to read IPTC tags
        :param filename: filename of image
        :param path: path to image
        :return: {'path': path, 'filename': filename, 'key': key, 'tags': ['tag 1', 'tag 2']} | False
        """
        try:
            image_data = {}
            url = os.path.join(path, filename)
            meta = pyexiv2.ImageMetadata(os.path.join(url))
            meta.read()
            iptc_keys = meta.iptc_keys
            for key in iptc_keys:
                tag = meta[key]
                image_data = {'path': path, 'filename': filename, 'iptc_key': key, 'tags': tag.raw_value}
            return image_data
        except IOError as e:
            print(f'An error occurred: {e}')
            return False

    @staticmethod
    def write_iptc_tags(path, filename, tag_data):
        """
        method to write IPTC tags to image
        :param path: path to target image
        :param filename: filename of target image
        :param tag_data: original image data: in form:
            {'path': /path/to/original/image, 'filename': filename, 'iptc_key': key, 'tags': ['tag 1', 'tag 2']}
        :return: True | False
        """
        try:
            iptc_key = tag_data['iptc_key']
            tags = tag_data['tags']
            url = os.path.join(path, filename)
            meta = pyexiv2.ImageMetadata(os.path.join(url))
            meta.read()
            meta[iptc_key] = pyexiv2.IptcTag(iptc_key, tags)
            meta.write()
            print('Tags successfully written!')
            return True
        except (TypeError, Exception) as e:
            print(e)
        return False

    @staticmethod
    def convert_format(filename, path, save_path, conversion_format):
        """
        method to convert the format of an image file
        :param filename: filename of image
        :param path: path of image
        :param conversion_format: file format to covert to
        :param save_path: where to save the converted image
        :return: [new file path, new file filename] | False
        """
        try:
            url = os.path.join(path, filename)
            file, extension = os.path.splitext(filename)
            outfile = f'{file}.{conversion_format}'
            Image.open(url).save(os.path.join(save_path, outfile), quality=100)
            print('Conversion done!')
            return {'path': save_path, 'filename': outfile}
        except (IOError, Exception) as e:
            print(f'An error occurred: {e}')
        return False

    @staticmethod
    def get_filenames(directory):
        """
        method to get filenames of all files (not sub-dirs) in a directory
        :param directory: the directory to scan for files
        :return: a list of files
        """
        filenames = []
        try:
            for filename in os.listdir(directory):
                if not os.path.isdir(os.path.join(directory, filename)):
                    filenames.append(filename)
            return filenames
        except (IOError, Exception) as e:
            print(f'An error occurred: {e}')
        return False

    def run(self):
        """
        method to run the image conversion and tagging processes
        :return: dict of saved conversion data and tags: e.g.:
            {'conversions': [{'path': '/path/to/processed/image', 'filename': '4058.jpeg'}], 'tags': [{'path':
             '/path/to/tagged/image', 'filename': '4058.tif', 'iptc_key': 'Iptc.Application2.Keywords', 'tags':
             ['DATE: 1974', 'PLACE: The Moon']}]}
        """
        try:
            existing_converted = self.get_filenames(self.PROCESSED_IMAGE_PATH)
            saved_tags = []
            saved_conversions = []
            for filename in os.listdir(self.ORIGINAL_IMAGE_PATH):
                if not os.path.isdir(os.path.join(self.ORIGINAL_IMAGE_PATH, filename)):
                    if self.reconvert is True or os.path.splitext(filename)[0] not in [os.path.splitext(f)[0] for f in
                                                                                       existing_converted]:
                        # save copy of the image with converted format
                        converted = self.convert_format(filename=filename, path=self.ORIGINAL_IMAGE_PATH,
                                                        save_path=self.PROCESSED_IMAGE_PATH,
                                                        conversion_format=self.CONVERSION_FORMAT)
                        saved_conversions.append(converted)
                    if self.retag is True or \
                            os.path.splitext(filename)[0] not in [os.path.splitext(f)[0] for f in existing_converted]:
                        # read tag data from original image
                        tag_data = self.read_iptc_tags(filename=filename, path=self.ORIGINAL_IMAGE_PATH)
                        # any additions or updates to the incoming tag data
                        tag_data['path'] = self.PROCESSED_IMAGE_PATH  # update tag_data['path'] to target image file
                        tag_data['tags'].append('TAG COPIED FROM ORIGINAL')  # add tag to identify as copied
                        # add to the return dict
                        saved_tags.append(tag_data)
                        # write tag data to the converted copy
                        file, extension = os.path.splitext(filename)
                        self.write_iptc_tags(path=self.PROCESSED_IMAGE_PATH,
                                             filename=f'{file}.{self.CONVERSION_FORMAT}',
                                             tag_data=tag_data)
            return {'conversions': saved_conversions, 'tags': saved_tags}
        except (TypeError, Exception) as e:
            print(f'Error: {e}')
        return False

# ProcessImages(image_path=ORIGINAL_IMAGE_PATH,
#               processed_image_path=PROCESSED_IMAGE_PATH,
#               conversion_format=CONVERSION_FORMAT,
#               reconvert=False,
#               retag=False).run()

# os.path.normpath('/mnt/adc_family_history/IMAGE_ARCHIVE/InProgress')
