import cv2

class PlayVideo(object):
    def __init__(self, path):
        self.video = cv2.VideoCapture(path)

    def __del__(self):
        self.video.release()
    
    def get_frame(self):
        success, image = self.video.read()
        #orig_h, orig_w = image.shape[:2]
        #sizes = (orig_h/2, orig_w/2)
        #image = cv2.resize(image, sizes)
        #ret, jpeg = cv2.imencode('.jpg', image)
        return image#jpeg.tobytes()
