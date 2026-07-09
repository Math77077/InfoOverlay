"""
Module managing filesystem mapping, asset caching, and memory-isolated playlist production.
"""

import os
import sys
import random

class AssetService:
    """
    Service responsible for separating internal compiled UI assets from external user-facing media.

    It provides a separation between the actual .svg icons used in the system and the resources that'll
    be put by the user. The folder for internal assets, such as the .svg, will be incorpored into the .exe, 
    while the resources folder will live alongside the .exe so the users can access it and put
    either the images or videos.

    Attributes:
        internal_base (str): Root path for compiled application internal assets.
        external_base (str): Root path where the active executable lives on disk.
        assets_dir (str): Absolute directory containing core visual UI vectors.
        images_dir (str): Path to external directory containing localized image campaigns.
        video_dir (str): Path to external directory containing localized video assets.
    """
    def __init__(self) -> None:
        """Initializes paths and automatically populates master files caches."""
        if getattr(sys, 'frozen', False):
            self.internal_base: str = sys._MEIPASS
            self.external_base: str = os.path.dirname(sys.executable)
        else:
            self.internal_base: str = os.path.dirname(os.path.abspath(__file__))
            self.external_base: str = self.internal_base

        self.assets_dir: str = os.path.join(self.internal_base, "app_assets")
        self.images_dir: str = os.path.join(self.external_base, "resources", "images")
        self.video_dir: str = os.path.join(self.external_base, "resources", "videos")

        self._cached_images_h: list[str] = []
        self._cached_images_v: list[str] = []
        self._cached_videos_h: list[str] = []
        self._cached_videos_v: list[str] = []

        self.refresh_all_caches()

    def refresh_all_caches(self) -> None:
        """
        Scans external directories and maps media file paths straight to RAM cache.

        Reads folders exactly once at startup. Then, sort the files into separated lists based on 
        aspect ratio (_h is horizontal/landscape, _v is vertical/portrait). Isolates the storage
        disk from the visual presentation thread.
        """
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

    def get_image_playlist(self, orientation: str ="horizontal") -> list[str]:
        """
        Generates a randomized playlist of image paths.

        Copy the master cache to avoid misleading tracking of files, then shuffle the isolated
        copy and pass it to the UI component.

        Args:
            orientation (str): Layout design targets, either "horizontal" or "vertical".

        Returns:
            list[str]: Shuffled absolute filesystem paths to available image assets.
        """
        source_cache = self._cached_images_h if orientation == "horizontal" else self._cached_images_v
        playlist = list(source_cache)

        random.shuffle(playlist)
        return playlist
    
    def get_video_playlist(self, orientation: str ="horizontal") -> list[str]:
        """
        Generates a randomized playlist of video paths.

        Copy the master cache to avoid misleading tracking of files, then shuffle the isolated
        copy and pass it to the UI component.

        Args:
            orientation (str): Layout design targets, either "horizontal" or "vertical".

        Returns:
            list[str]: Shuffled absolute filesystem paths to available video assets.
        """
        source_cache = self._cached_videos_h if orientation == "horizontal" else self._cached_videos_v
        playlist = list(source_cache)

        random.shuffle(playlist)
        return playlist
    
    def get_asset_path(self, filename: str) -> str:
        """
        Resolves an absolute path to internal application icons.

        Args:
            filename (str): The name of the file inside of the app_assets folder

        Returns:
            str: Normalized absolute path directly to the internal graphic asset.
        """
        return os.path.abspath(os.path.join(self.assets_dir, filename))
    
