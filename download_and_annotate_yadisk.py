import os
import json
import argparse
from typing import Dict, List, Tuple

import cv2
import requests

from yandex_downloader import YandexDownloader


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def download_text_files(downloader: YandexDownloader, yadisk_url: str, dest_dir: str) -> Dict[str, str]:
    loaded = downloader.get_data_from_yandex_disk(yadisk_url)
    saved: Dict[str, str] = {}
    for name, content in loaded.items():
        local_path = os.path.join(dest_dir, name)
        with open(local_path, "w", encoding="utf-8") as f:
            f.write(content)
        saved[name] = local_path
    return saved


def download_videos(downloader: YandexDownloader, yadisk_url: str, dest_dir: str) -> Dict[str, str]:
    video_urls = downloader.get_video_urls_from_yandex_disk(yadisk_url)
    saved: Dict[str, str] = {}
    session = requests.Session()
    for base_name, url in video_urls.items():
        local_name = f"{base_name}.mp4"
        local_path = os.path.join(dest_dir, local_name)
        with session.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
        saved[base_name] = local_path
    return saved


def load_pothole_detections(detections_json_path: str) -> List[Dict]:
    with open(detections_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("potholes", [])


def group_detections_by_frame(detections: List[Dict], fps: float) -> Dict[int, List[Tuple[int, int, int, int, float]]]:
    by_frame: Dict[int, List[Tuple[int, int, int, int, float]]] = {}
    for det in detections:
        timestamp = float(det.get("timestamp", 0.0))
        rect = det.get("rect", None)
        conf = float(det.get("conf", 0.0))
        if not rect or len(rect) != 2:
            continue
        x = int(round(rect[0][0]))
        y = int(round(rect[0][1]))
        w = int(round(rect[1][0]))
        h = int(round(rect[1][1]))
        frame_idx = int(round(timestamp * fps))
        by_frame.setdefault(frame_idx, []).append((x, y, w, h, conf))
    return by_frame


def annotate_and_save_frames(video_path: str, by_frame: Dict[int, List[Tuple[int, int, int, int, float]]], out_frames_dir: str) -> None:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    used_indices = sorted([idx for idx in by_frame.keys() if total == 0 or idx < total])

    if not used_indices:
        cap.release()
        return

    last_needed = used_indices[-1]
    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx in by_frame:
            for (x, y, w, h, conf) in by_frame[frame_idx]:
                pt1 = (max(0, x), max(0, y))
                pt2 = (max(0, x + w), max(0, y + h))
                cv2.rectangle(frame, pt1, pt2, (0, 255, 0), 2)
                label = f"{conf:.2f}"
                t_pt = (pt1[0], max(0, pt1[1] - 6))
                cv2.putText(frame, label, t_pt, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv2.LINE_AA)
            out_name = f"frame_{frame_idx:06d}.jpg"
            out_path = os.path.join(out_frames_dir, out_name)
            cv2.imwrite(out_path, frame)
        frame_idx += 1
        if total and frame_idx > last_needed and frame_idx > total:
            break

    cap.release()


def main() -> None:
    parser = argparse.ArgumentParser(description="Download Yandex Disk data, draw pothole bboxes, save frames")
    parser.add_argument("yadisk_folder_url", type=str, help="Public folder URL on Yandex Disk")
    parser.add_argument("output_dir", type=str, help="Local directory to store downloads and annotated frames")
    args = parser.parse_args()

    ensure_dir(args.output_dir)
    frames_dir = os.path.join(args.output_dir, "frames")
    ensure_dir(frames_dir)

    downloader = YandexDownloader()

    saved_texts = download_text_files(downloader, args.yadisk_folder_url, args.output_dir)
    saved_videos = download_videos(downloader, args.yadisk_folder_url, args.output_dir)

    detections_path = saved_texts.get("detections.json")
    if not detections_path:
        raise FileNotFoundError("detections.json not found in Yandex folder")

    detections = load_pothole_detections(detections_path)
    if not detections:
        return

    chosen_video = None
    if "video" in saved_videos:
        chosen_video = saved_videos["video"]
    elif "video_2" in saved_videos:
        chosen_video = saved_videos["video_2"]
    else:
        raise FileNotFoundError("No video or video_2 found in Yandex folder")

    cap = cv2.VideoCapture(chosen_video)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {chosen_video}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    cap.release()

    by_frame = group_detections_by_frame(detections, fps)
    annotate_and_save_frames(chosen_video, by_frame, frames_dir)


if __name__ == "__main__":
    main()


