# src/cde_orchestrator/infrastructure/file_watcher.py
import logging
import threading
import time
from pathlib import Path
from typing import Callable, List

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

logger = logging.getLogger(__name__)

class FileChangeDetector(FileSystemEventHandler):
    """Monitors specific files for changes and triggers a callback."""

    def __init__(self, project_path: str, watch_files: List[str], callback: Callable):
        self.project_path = Path(project_path)
        self.watch_files = [self.project_path / f for f in watch_files]
        self.callback = callback
        self.observer = Observer()

    def on_modified(self, event):
        """Callback triggered when a file is modified."""
        if not event.is_directory and Path(event.src_path) in self.watch_files:
            logger.info(f"Detected change in {event.src_path}, invalidating cache.")
            self.callback()

    def start(self):
        """Starts the file watcher in a separate thread."""
        self.observer.schedule(self, self.project_path, recursive=False)
        self.observer.start()
        logger.info(f"Started watching for file changes in {self.project_path}")

    def stop(self):
        """Stops the file watcher."""
        self.observer.stop()
        self.observer.join()
        logger.info("Stopped watching for file changes.")

def start_file_watcher(
    project_path: str, watch_files: List[str], callback: Callable
):
    """
    Initializes and starts a file watcher for a given project.
    """
    watcher = FileChangeDetector(
        project_path=project_path,
        watch_files=watch_files,
        callback=callback,
    )
    watcher.start()
    return watcher
