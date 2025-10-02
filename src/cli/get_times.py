from pathlib import Path
from src.movie_iterator import MovieIter

SIZE = (640,480)

def _frame_counter(path:str, size:tuple):
    movie_iter = MovieIter(moviefile=path, size=size)

    frame_count = 0
    for _ in movie_iter:
        frame_count += 1
    return frame_count

def get_eyecatch_times(movie_files:list[str]):
    counted_dict = {"file_path":[],"frame":[]}
    for path in movie_files:
        counted_frame = _frame_counter(moviefile=path,size=SIZE)
        counted_dict["file_path"].append(path)
        counted_dict["frame"].append(counted_frame)
    return 
        

def run_get_eyecatch():
    path_list = glob.glob()
