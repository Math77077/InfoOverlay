import os
import sys
import random

class AssetService:
    def __init__(self):
        if getattr(sys, 'frozen', False):
            self.internal_base = sys._MEIPASS
            self.external_base = os.path.dirname(sys.executable)
        else:
            self.internal_base = os.path.dirname(os.path.abspath(__file__))
            self.external_base = self.internal_base

        self.assets_dir = os.path.join(self.internal_base, "app_assets")
        self.images_dir = os.path.join(self.external_base, "resources", "images")
        self.video_dir = os.path.join(self.external_base, "resources", "videos")

        self._cached_images_h = []
        self._cached_images_v = []

        self.refresh_all_caches()

    def refresh_all_caches(self):
        self._cached_images_h = [
            os.path.abspath(os.path.join(self.images_dir, f))
            for f in os.listdir(self.images_dir)
            if f.lower().endswith(('.png', '.jpg', '.jpeg')) and "_h" in f.lower()
        ]
        
        self._cached_images_v = [
            os.path.abspath(os.path.join(self.images_dir, f))
            for f in os.listdir(self.images_dir)
            if f.lower().endswith(('.png', '.jpg', '.jpeg')) and "_v" in f.lower()
        ]

        self._cached_videos_h = [
            os.path.abspath(os.path.join(self.video_dir, f))
            for f in os.listdir(self.video_dir)
            if f.lower().endswith(('.mp4', '.mov')) and "_h" in f.lower()
        ]
        
        self._cached_videos_v = [
            os.path.abspath(os.path.join(self.video_dir, f))
            for f in os.listdir(self.video_dir)
            if f.lower().endswith(('.mp4', '.mov')) and "_v" in f.lower()
        ]

    def get_image_playlist(self, orientation="horizontal"):
        source_cache = self._cached_images_h if orientation == "horizontal" else self._cached_images_v
        playlist = list(source_cache)

        random.shuffle(playlist)
        return playlist
    
    def get_video_playlist(self, orientation="horizontal"):
        source_cache = self._cached_videos_h if orientation == "horizontal" else self._cached_videos_v
        playlist = list(source_cache)

        random.shuffle(playlist)
        return playlist
    
    def get_asset_path(self, filename):
        return os.path.abspath(os.path.join(self.assets_dir, filename))
    
