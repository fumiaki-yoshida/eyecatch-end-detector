import argparse
from pathlib import Path 
from src.movie_iterator import MINUTES, MovieIter
import glob

SIZE = (60,40)
SEARCH_END_MIN = 3

parser = argparse.ArgumentParser(description="Get eyecatch end times from movie files")
parser.add_argument("movie_directory", type=str, nargs='+', help="directory of movie files to process")
parser.add_argument("--search_end_min", type=int, default=MINUTES, help="minutes to search for eyecatch (default: 3 minutes)")
parser.add_argument("--threshold", type=int, default=30, help="threshold value for eyecatch detection")
args  = parser.parse_args()

def _frame_counter(path:str, size:tuple):
    movie_iter = MovieIter(moviefile=path, size=size, serch_end_min=args.search_end_min)

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
    movie_directory = Path(args.movie_directory[0])
    if not movie_directory.exists():
        raise ValueError(f"Directory {movie_directory} does not exist.")
    
    video_patterns = ["*.mp4", "*.mkv", "*.avi", "*.mov", "*.flv", "*.wmv", "*.webm"]
    path_list = []
    for pattern in video_patterns:
        path_list.extend([p for p in glob.glob(str(movie_directory.joinpath(pattern)))])
    result = get_eyecatch_times(path_list)
    print(result)

if __name__ == "__main__":
    run_get_eyecatch()
