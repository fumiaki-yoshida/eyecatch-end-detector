import cv2


class MovieIter(object):
    def __init__(self, moviefile, size=None, inter_method=cv2.INTER_AREA):
        self.org = cv2.VideoCapture(moviefile)
        self.fps = self.org.get(cv2.CAP_PROP_FPS)
        self.frame_limit = int(self.fps * 60 * 3)  # 最大3分間分のフレーム数
        self.size = size
        self.inter_method = inter_method
        self.framecnt = 0
    def __iter__(self):
        return self
    def __next__(self):
        if self.framecnt >= self.frame_limit:
            raise StopIteration()
        self.end_flg, self.frame = self.org.read()
        if not self.end_flg:
            raise StopIteration()
        self.framecnt += 1
        if self.size:
            self.frame = cv2.resize(self.frame, self.size, interpolation=self.inter_method)
        return self.frame
    def __del__(self):
        self.org.release()
