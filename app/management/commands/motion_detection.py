import urllib
from urllib import parse

from django.core.files.temp import NamedTemporaryFile
from django.core.mail import EmailMessage
from django.core.management import BaseCommand
from django.db import IntegrityError
from imutils.video import VideoStream
import argparse
import datetime
import imutils
import time
import cv2

from Picmove import settings
from app.models import Movement, Option


class Command(BaseCommand):
    START_PIC_PATH = './media/'
    OCCUPIED = "Occupied"
    UNOCCUPIED = "Unoccupied"
    stream = None
    is_started_stream = False

    def add_arguments(self, parser):
        parser.add_argument("-vi", "--video", help="path to the video file")
        parser.add_argument("-a", "--min-area", type=int, default=500, help="minimum area size")
        parser.add_argument("-s", "--saving", type=int, default=0, help="minimum area size")

    def get_video_stream(self, video):
        if video is None:
            return VideoStream(src=0)
        # otherwise, we are reading from a video file
        else:
            return cv2.VideoCapture(video)

    def start_stream(self, video):
        if not self.is_started_stream:
            self.stream = self.get_video_stream(video)
            if video is None:
                self.stream.start()
                self.is_started_stream = True

    def stop_stream(self, video):
        if self.is_started_stream:
            self.stream.stop() if video is None else self.stream.release()
            cv2.destroyAllWindows()
            self.stream = None
            self.is_started_stream = False

    def send_mail(self, image_link):
        email_subject = 'PicMove'
        email_message = EmailMessage(
            email_subject,
            "sdfsdfsdf",
            settings.DEFAULT_FROM_EMAIL,
            ['xxxxx@gmail.com'],
        )
        email_message.attach_file(image_link)
        email_message.send(fail_silently=False)

    def handle(self, *args, **options):
        print("Start Motion Detection")
        text = None
        video = options['video']
        min_area = options['min_area']
        saving = options['saving']
        # if the video argument is None, then we are reading from webcam

        # initialize the first frame in the video stream
        firstFrame = None
        key = None

        #
        i = 0
        datetime_occupied = None
        j = 1
        flag = 0

        # loop over the frames of the video
        tim1 = time.time()
        while True:

            if Option.objects.filter(key='is_camera_on', value=True).exists():
                self.start_stream(video)

                tim2 = time.time()

                if tim2 - tim1 > 5:
                    if saving == 1:
                        datetime_occupied = time.strftime('%Y-%m-%d %I:%M:%S %p %Z')
                        self.create_file('{}.{}'.format(str(datetime_occupied), '.jpg'), frame)
                        tim1 = time.time()

                    # grab the current frame and initialize the occupied/unoccupied
                    # text
                    frame = self.stream.read()
                    frame = frame if video is None else frame[1]
                    text = "Unoccupied"

                    # if the frame could not be grabbed, then we have reached the end
                    # of the video
                    if frame is None:
                        break

                    # resize the frame, convert it to grayscale, and blur it
                    frame = imutils.resize(frame, width=500)
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    gray = cv2.GaussianBlur(gray, (21, 21), 0)

                    # if the first frame is None, initialize it
                    if firstFrame is None:
                        firstFrame = gray
                        continue

                    # compute the absolute difference between the current frame and
                    # first frame
                    frameDelta = cv2.absdiff(firstFrame, gray)
                    thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

                    # dilate the thresholded image to fill in holes, then find contours
                    # on thresholded image
                    thresh = cv2.dilate(thresh, None, iterations=2)
                    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                            cv2.CHAIN_APPROX_SIMPLE)
                    cnts = imutils.grab_contours(cnts)

                    # loop over the contours
                    for c in cnts:
                        # if the contour is too small, ignore it
                        if cv2.contourArea(c) < min_area:
                            continue

                        # compute the bounding box for the contour, draw it on the frame,
                        # and update the text
                        (x, y, w, h) = cv2.boundingRect(c)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        text = "Occupied"

                    # draw the text and timestamp on the frame
                    cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                                (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

                    # show the frame and record if the user presses a key
                    cv2.imshow("Security Feed", frame)
                    # cv2.imshow("Thresh", thresh)
                    # cv2.imshow("Frame Delta", frameDelta)
                    key = cv2.waitKey(1) & 0xFF

                if text == "Unoccupied":
                    if flag == 0 and j == 1:
                        flag = 1
                    elif flag == 0 and j == 2:
                        datetime_occupied = time.strftime('%Y-%m-%d %I:%M:%S %p %Z')
                        self.create_file('{}-{}.{}'.format(self.UNOCCUPIED, str(datetime_occupied), 'jpg'), frame)
                        flag = 1
                        j = 1
                if text == "Occupied" and flag == 1:

                    if i == 50:
                        datetime_occupied = time.strftime('%Y-%m-%d %I:%M:%S %p %Z')
                        self.create_file('{}-{}.{}'.format(self.OCCUPIED, str(datetime_occupied), 'jpg'), frame)
                        i = 0
                        flag = 0
                        j = 2
                    i = i + 1

                # if the `q` key is pressed, break from the lop
            if key == ord("q") or Option.objects.filter(key='is_camera_on', value=False).exists():
                self.stop_stream(video)
                break

    def create_file(self, file_name, frame):
        cv2.imwrite('{}/{}'.format(self.START_PIC_PATH, file_name), frame)
        movement = Movement()
        movement.img = '{}/{}'.format(self.START_PIC_PATH, file_name)
        movement.save()
        if Option.objects.filter(key='is_send_email', value=True).exists():
            self.send_mail(parse.unquote('.' + movement.img.url))

