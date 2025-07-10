
import numpy as np
from src.movie_iterator import MovieIter
from src.metrics import MAE


INFILE = "/data/natori_sana/20210620_さなちゃんねる_【雑談】次に来るマンガ大賞2021や好きな漫画について、ひぐらしの沙都子は学校辞めてYouTuberとして大成してくれ頼むから、な配信【名取さな】.webm"  # 映像ファイルのパス
THRESH = 20  # 閾値（カット検出基準）


# 初期設定
picsize = (48, 27)  # 解像度を設定
frame_cnt = 0
cut_cnt = 0
frame_ultima = np.zeros((*picsize[::-1], 3), dtype=np.uint8)  # 空の画像を作成
list_diff = []
# 映像読み込みインスタンス
movie = MovieIter(INFILE, picsize)
# メイン処理ループ
for frame in movie:
    if frame_cnt == 0:
      frame_ultima = frame  # 初期化のみして次へ
      frame_cnt += 1
      continue
    if frame_cnt % int(movie.fps * 0.5) == 0:  # 0.5秒ごとに1回処理
        frame_penult = frame_ultima
        frame_ultima = frame
        diff = frame_ultima.astype(np.int16) - frame_penult.astype(np.int16)
        mae = MAE(diff)
        list_diff.append(mae)
    frame_cnt += 1
