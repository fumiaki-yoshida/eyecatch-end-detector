import pytest
import cv2
from unittest.mock import Mock, patch
import sys
import os

# プロジェクトのsrcディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from movie_iterator import MovieIter, SEARCH_END_MIN, MINUTES


class TestMovieIter:
    """MovieIterクラスのテストスイート"""
    
    def setup_method(self):
        """各テストメソッドの前に実行される初期化処理"""
        self.mock_cap = Mock()
        self.test_moviefile = "test_movie.mp4"
        self.test_fps = 30.0
    
    def test_init_with_default_parameters(self):
        """デフォルトパラメータでの初期化テスト"""
        with patch('cv2.VideoCapture') as mock_video_capture:
            mock_video_capture.return_value = self.mock_cap
            self.mock_cap.get.return_value = self.test_fps
            
            movie_iter = MovieIter(self.test_moviefile)
            
            # 初期化の検証
            mock_video_capture.assert_called_once_with(self.test_moviefile)
            self.mock_cap.get.assert_called_once_with(cv2.CAP_PROP_FPS)
            assert movie_iter.fps == self.test_fps
            assert movie_iter.frame_limit == int(self.test_fps * MINUTES * SEARCH_END_MIN)
            assert movie_iter.size is None
            assert movie_iter.inter_method == cv2.INTER_AREA
            assert movie_iter.framecnt == 0
    
    def test_init_with_custom_parameters(self):
        """カスタムパラメータでの初期化テスト"""
        custom_size = (640, 480)
        custom_inter_method = cv2.INTER_LINEAR
        
        with patch('cv2.VideoCapture') as mock_video_capture:
            mock_video_capture.return_value = self.mock_cap
            self.mock_cap.get.return_value = self.test_fps
            
            movie_iter = MovieIter(
                self.test_moviefile, 
                size=custom_size, 
                inter_method=custom_inter_method
            )
            
            assert movie_iter.size == custom_size
            assert movie_iter.inter_method == custom_inter_method
    
    def test_frame_limit_calculation(self):
        """フレーム制限の計算が正しいことを確認"""
        with patch('cv2.VideoCapture') as mock_video_capture:
            mock_video_capture.return_value = self.mock_cap
            self.mock_cap.get.return_value = 25.0  # 25 FPS
            
            movie_iter = MovieIter(self.test_moviefile)
            
            expected_frame_limit = int(25.0 * MINUTES * SEARCH_END_MIN)
            assert movie_iter.frame_limit == expected_frame_limit
    
    def test_iter_returns_self(self):
        """__iter__が自分自身を返すことを確認"""
        with patch('cv2.VideoCapture') as mock_video_capture:
            mock_video_capture.return_value = self.mock_cap
            self.mock_cap.get.return_value = self.test_fps
            
            movie_iter = MovieIter(self.test_moviefile)
            
            assert iter(movie_iter) is movie_iter
    
    def test_next_successful_frame_read(self):
        """正常なフレーム読み取りのテスト"""
        test_frame = "dummy_frame_data"
        
        with patch('cv2.VideoCapture') as mock_video_capture:
            mock_video_capture.return_value = self.mock_cap
            self.mock_cap.get.return_value = self.test_fps
            self.mock_cap.read.return_value = (True, test_frame)
            
            movie_iter = MovieIter(self.test_moviefile)
            
            frame = next(movie_iter)
            
            assert frame == test_frame
            assert movie_iter.framecnt == 1
            self.mock_cap.read.assert_called_once()
    
    def test_next_with_resize(self):
        """リサイズありのフレーム読み取りテスト"""
        original_frame = "original_frame"
        resized_frame = "resized_frame"
        test_size = (320, 240)
        
        with patch('cv2.VideoCapture') as mock_video_capture, \
             patch('cv2.resize') as mock_resize:
            
            mock_video_capture.return_value = self.mock_cap
            self.mock_cap.get.return_value = self.test_fps
            self.mock_cap.read.return_value = (True, original_frame)
            mock_resize.return_value = resized_frame
            
            movie_iter = MovieIter(self.test_moviefile, size=test_size)
            
            frame = next(movie_iter)
            
            assert frame == resized_frame
            mock_resize.assert_called_once_with(
                original_frame, 
                test_size, 
                interpolation=cv2.INTER_AREA
            )
    
    def test_next_raises_stopiteration_on_read_failure(self):
        """フレーム読み取り失敗時のStopIteration例外テスト"""
        with patch('cv2.VideoCapture') as mock_video_capture:
            mock_video_capture.return_value = self.mock_cap
            self.mock_cap.get.return_value = self.test_fps
            self.mock_cap.read.return_value = (False, None)
            
            movie_iter = MovieIter(self.test_moviefile)
            
            with pytest.raises(StopIteration):
                next(movie_iter)
    
    def test_next_raises_stopiteration_on_frame_limit(self):
        """フレーム制限到達時のStopIteration例外テスト"""
        with patch('cv2.VideoCapture') as mock_video_capture:
            mock_video_capture.return_value = self.mock_cap
            self.mock_cap.get.return_value = self.test_fps
            
            movie_iter = MovieIter(self.test_moviefile)
            movie_iter.framecnt = movie_iter.frame_limit  # 制限に到達
            
            with pytest.raises(StopIteration):
                next(movie_iter)
            
            # readが呼ばれていないことを確認
            self.mock_cap.read.assert_not_called()
    
    def test_frame_count_increments_correctly(self):
        """フレームカウントが正しく増加することを確認"""
        test_frame = "test_frame"
        
        with patch('cv2.VideoCapture') as mock_video_capture:
            mock_video_capture.return_value = self.mock_cap
            self.mock_cap.get.return_value = self.test_fps
            self.mock_cap.read.return_value = (True, test_frame)
            
            movie_iter = MovieIter(self.test_moviefile)
            
            assert movie_iter.framecnt == 0
            
            next(movie_iter)
            assert movie_iter.framecnt == 1
            
            next(movie_iter)
            assert movie_iter.framecnt == 2
    
    def test_iteration_stops_at_frame_limit(self):
        """イテレーションがフレーム制限で停止することを確認"""
        test_frame = "test_frame"
        
        with patch('cv2.VideoCapture') as mock_video_capture:
            mock_video_capture.return_value = self.mock_cap
            self.mock_cap.get.return_value = 1.0  # 低いFPSで制限を小さく
            self.mock_cap.read.return_value = (True, test_frame)
            
            movie_iter = MovieIter(self.test_moviefile)
            frame_limit = movie_iter.frame_limit
            
            # フレーム制限まで読み取り
            frames = []
            for frame in movie_iter:
                frames.append(frame)
            
            assert len(frames) == frame_limit
            assert movie_iter.framecnt == frame_limit
    
    def test_del_releases_video_capture(self):
        """デストラクタでVideoCapture.release()が呼ばれることを確認"""
        with patch('cv2.VideoCapture') as mock_video_capture:
            mock_video_capture.return_value = self.mock_cap
            self.mock_cap.get.return_value = self.test_fps
            
            movie_iter = MovieIter(self.test_moviefile)
            
            # デストラクタを明示的に呼び出し
            movie_iter.__del__()
            
            self.mock_cap.release.assert_called_once()
    
    def test_context_manager_like_usage(self):
        """コンテキストマネージャ的な使用方法のテスト"""
        test_frame = "test_frame"
        
        with patch('cv2.VideoCapture') as mock_video_capture:
            mock_video_capture.return_value = self.mock_cap
            self.mock_cap.get.return_value = self.test_fps
            self.mock_cap.read.return_value = (True, test_frame)
            
            movie_iter = MovieIter(self.test_moviefile)
            
            # いくつかのフレームを処理
            processed_frames = 0
            for frame in movie_iter:
                processed_frames += 1
                if processed_frames >= 5:  # 5フレームで停止
                    break
            
            assert processed_frames == 5
            assert movie_iter.framecnt == 5


class TestMovieIterConstants:
    """MovieIterで使用される定数のテスト"""
    
    def test_search_end_min_constant(self):
        """SEARCH_END_MIN定数の値を確認"""
        assert SEARCH_END_MIN == 3
    
    def test_minutes_constant(self):
        """MINUTES定数の値を確認"""
        assert MINUTES == 60
