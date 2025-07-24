from unittest.mock import Mock, patch
import cv2
import numpy as np
from src.movie_iterator import MovieIter


def test_movie_iter():  # pytest命名規則: test_ で始める
    """test_video.mp4をモック化したテスト"""
    # VideoCaptureをモック化
    with patch('cv2.VideoCapture') as mock_cv2:
        mock_cap = Mock()
        mock_cap.get.return_value = 30.0  # FPS
        mock_cv2.return_value = mock_cap
        
        # テスト用フレームを作成
        test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        resized_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # read メソッドの戻り値を設定（3フレームで終了）
        mock_cap.read.side_effect = [
            (True, test_frame),
            (True, test_frame),
            (True, test_frame),
            (False, None)  # 終了
        ]
        
        # cv2.resizeをモック化
        with patch('cv2.resize', return_value=resized_frame) as mock_resize:
            # テスト実行
            movie_iter = MovieIter('test_video.mp4', size=(640, 480))
            frames = list(movie_iter)
            
            # アサーション
            assert isinstance(frames, list)
            assert all(isinstance(frame, np.ndarray) for frame in frames)  # numpy arrays
            assert len(frames) <= movie_iter.frame_limit
            assert all(frame.shape == (480, 640, 3) for frame in frames)
            assert len(frames) == 3  # 3フレーム取得されることを確認
            
            # cv2.resizeが正しく呼ばれたか確認
            assert mock_resize.call_count == 3
            mock_resize.assert_called_with(test_frame, (640, 480), interpolation=cv2.INTER_AREA)


def test_movie_iter_without_resize():
    """リサイズなしのテスト"""
    with patch('cv2.VideoCapture') as mock_cv2:
        mock_cap = Mock()
        mock_cap.get.return_value = 30.0
        mock_cv2.return_value = mock_cap
        
        # オリジナルサイズのフレーム
        original_frame = np.random.randint(0, 255, (720, 1280, 3), dtype=np.uint8)
        
        mock_cap.read.side_effect = [
            (True, original_frame),
            (True, original_frame),
            (False, None)
        ]
        
        # サイズ指定なしでテスト
        movie_iter = MovieIter('test_video.mp4')  # sizeパラメータなし
        frames = list(movie_iter)
        
        assert len(frames) == 2
        assert all(frame.shape == (720, 1280, 3) for frame in frames)


def test_movie_iter_frame_limit_reached():
    """フレーム制限に到達するテスト"""
    with patch('cv2.VideoCapture') as mock_cv2:
        mock_cap = Mock()
        mock_cap.get.return_value = 1.0  # 1FPS（テスト用に低く設定）
        mock_cv2.return_value = mock_cap
        
        test_frame = np.ones((100, 100, 3), dtype=np.uint8)
        # 常にフレームが読めるように設定
        mock_cap.read.return_value = (True, test_frame)
        
        movie_iter = MovieIter('test_video.mp4')
        # frame_limit = 1 * 60 * 3 = 180 フレーム
        
        frame_count = 0
        for frame in movie_iter:
            frame_count += 1
            if frame_count > 200:  # 無限ループ防止
                break
        
        # フレーム制限で止まることを確認
        assert frame_count == movie_iter.frame_limit


def test_movie_iter_video_end():
    """動画終了のテスト"""
    with patch('cv2.VideoCapture') as mock_cv2:
        mock_cap = Mock()
        mock_cap.get.return_value = 30.0
        mock_cv2.return_value = mock_cap
        
        # 最初から動画が終了している状態
        mock_cap.read.return_value = (False, None)
        
        movie_iter = MovieIter('test_video.mp4')
        frames = list(movie_iter)
        
        assert len(frames) == 0  # フレームが取得されない


def test_movie_iter_initialization():
    """初期化のテスト"""
    with patch('cv2.VideoCapture') as mock_cv2:
        mock_cap = Mock()
        mock_cap.get.return_value = 25.0
        mock_cv2.return_value = mock_cap
        
        movie_iter = MovieIter('test_video.mp4', size=(320, 240), inter_method=cv2.INTER_LINEAR)
        
        # 初期化の確認
        assert movie_iter.fps == 25.0
        assert movie_iter.frame_limit == 25 * 60 * 3  # 4500フレーム
        assert movie_iter.size == (320, 240)
        assert movie_iter.inter_method == cv2.INTER_LINEAR
        assert movie_iter.framecnt == 0
        
        # VideoCaptureが正しく呼ばれたか確認
        mock_cv2.assert_called_once_with('test_video.mp4')


# 元の関数名でも動作するようにする場合（ただしpytestでは推奨されない）
def TestMovieIter():
    """元の関数名での実行（モック版）"""
    test_movie_iter()  # 上記のテスト関数を呼び出し
