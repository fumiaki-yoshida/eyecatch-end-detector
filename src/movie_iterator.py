import cv2
from src.metrics import MAE

MINUTES = 60


class MovieIter(object):
    def __init__(
        self,
        moviefile: str,
        serch_end_min: int,
        size: tuple[int, int] = None,
        inter_method: int = cv2.INTER_AREA,
    ):
        self.org = cv2.VideoCapture(moviefile)
        self.fps = self.org.get(cv2.CAP_PROP_FPS)
        self.frame_limit = int(
            self.fps * MINUTES * serch_end_min
        )
        self.size = size
        self.inter_method = inter_method
        self.threshold: int
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
            self.frame = cv2.resize(
                self.frame, self.size, interpolation=self.inter_method
            )
        return self.frame

        if self.prev_frame is not None:
            self.current_mae = MAE(self.prev_frame, self.frame)
            if self.current_mae < self.threshold:
                raise StopIteration()
        self.prev_frame = self.frame
        return self.frame

    def __del__(self):
        self.org.release()
