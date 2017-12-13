import cv2

class VideoCamera(object):
    def __init__(self):
        # Using OpenCV to capture from device 0. If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.
        self.video = cv2.VideoCapture(0)
        # If you decide to use video.mp4, you must have this file in the folder
        # as the main.py.
        # self.video = cv2.VideoCapture('video.mp4')
    
    def __del__(self):
        self.video.release()
    
    def get_frame(self):
        success, image = self.video.read()
        # We are using Motion JPEG, but OpenCV defaults to capture raw images,
        # so we must encode it into JPEG in order to correctly display the
        # video stream.
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tostring()
    def canny(self, thrs1, thrs2):
    	success, image = self.video.read()
    	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edge = cv2.Canny(gray, thrs1, thrs2, apertureSize = 5)
    	ret, jpeg = cv2.imencode('.jpg', edge)
    	return jpeg.tostring()

