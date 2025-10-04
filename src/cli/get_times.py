import argparse
from src.movie_iterator import MovieIter
import glob

SIZE = (640,480)

parser = argparse.ArgumentParser(description="Get eyecatch end times from movie files")
parser.add_argument("movie_directory", type=str, nargs='+', help="directory of movie files to process")
parser.add_argument("--threshold", type=int, default=30, help="threshold value for eyecatch detection")
args  = parser.parse_args()

def _frame_counter(path:str, size:tuple):
    movie_iter = MovieIter(moviefile=path, size=size)

    frame_count = 0
    for _ in movie_iter:
        frame_count += 1
    return frame_count

def get_eyecatch_times(movie_files:list[str]):
    counted_dict = {"file_path":[],"frame":[]}
    for path in movie_files:
        counted_frame = _frame_counter(path=path,size=SIZE)
        counted_dict["file_path"].append(path)
        counted_dict["frame"].append(counted_frame)
    return counted_dict


def run_get_eyecatch(args=args):
    path_list = glob.glob(args.movie_directory[0])
    
    result = get_eyecatch_times(path_list)
    print(result)

if __name__ == "__main__":
    run_get_eyecatch()
