"""
Модуль для парсинга данных GPS, событий и информации об устройстве.
"""

import json
import csv
from typing import List, Dict, Any


class DataParser:
    """Класс для парсинга различных типов данных."""
    
    @staticmethod
    def parse_gps_data(gps_data: str) -> List[Dict[str, Any]]:
        """Парсит GPS данные из CSV строки."""
        gps_data_list = []
        
        # Если это путь к файлу, читаем файл
        if isinstance(gps_data, str) and '\n' not in gps_data and len(gps_data) < 255:
            # Это путь к файлу
            with open(gps_data, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    gps_data_list.append({
                        'time': float(row['time']),
                        'lat': float(row['lat']),
                        'lon': float(row['lon']),
                        'accuracy': float(row['accuracy']),
                        'altitude': float(row['altitude']),
                        'speed': float(row['speed']),
                        'course': float(row['course']) if 'course' in row else None
                    })
        else:
            # Это данные в памяти
            import io
            reader = csv.DictReader(io.StringIO(gps_data))
            for row in reader:
                gps_data_list.append({
                    'time': float(row['time']),
                    'lat': float(row['lat']),
                    'lon': float(row['lon']),
                    'accuracy': float(row['accuracy']),
                    'altitude': float(row['altitude']),
                    'speed': float(row['speed']),
                    'course': float(row['course']) if 'course' in row else None
                })
        
        # Нормализуем время относительно первого timestamp
        if gps_data_list:
            start_time = gps_data_list[0]['time']
            for point in gps_data_list:
                point['time'] = point['time'] - start_time
        
        return gps_data_list
    
    @staticmethod
    def parse_detections_data(detections_data: str, gps_start_time: float = None) -> List[Dict[str, Any]]:
        """Парсит данные о событиях из JSON строки."""
        # Если это путь к файлу, читаем файл
        if isinstance(detections_data, str) and '\n' not in detections_data and len(detections_data) < 255:
            # Это путь к файлу
            with open(detections_data, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            # Это данные в памяти
            data = json.loads(detections_data)
        
        events = []
        
        # Обрабатываем ручные события
        if 'manualEvents' in data:
            for event in data['manualEvents']:
                events.append({
                    'type': 'manual',
                    'event_type': event['event']['type'],
                    'time': event['time'],
                    'lat': event['coordinate']['latitude'],
                    'lon': event['coordinate']['longitude'],
                    'custom_name': event['event'].get('customName', '')
                })
        
        # Обрабатываем ямы
        if 'potholes' in data:
            for pothole in data['potholes']:
                events.append({
                    'type': 'pothole',
                    'event_type': 'pothole',
                    'time': pothole['timestamp'],
                    'lat': pothole['coord']['latitude'],
                    'lon': pothole['coord']['longitude'],
                    'confidence': pothole['conf']
                })
        
        # Время событий уже нормализовано (относительное время в секундах)
        # Не нужно дополнительной нормализации
        
        return events
    
    @staticmethod
    def parse_device_info(device_data: str) -> Dict[str, Any]:
        """Парсит информацию об устройстве."""
        # Если это путь к файлу, читаем файл
        if isinstance(device_data, str) and '\n' not in device_data and len(device_data) < 255:
            # Это путь к файлу
            with open(device_data, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Это данные в памяти
            return json.loads(device_data)
    
    @staticmethod
    def parse_times_data(times_data: str) -> Dict[str, Any]:
        """Парсит данные о временных метках кадров из JSON строки."""
        # Если это путь к файлу, читаем файл
        if isinstance(times_data, str) and '\n' not in times_data and len(times_data) < 255:
            # Это путь к файлу
            with open(times_data, 'r', encoding='utf-8') as f:
                times_data = json.load(f)
        else:
            # Это данные в памяти
            times_data = json.loads(times_data)
        
        if not times_data:
            return {'start_time': 0, 'end_time': 0, 'duration': 0, 'frame_times': []}
        
        # Находим первую и последнюю временные метки
        start_time = times_data[0]['time']
        end_time = times_data[-1]['time']
        duration = end_time - start_time
        
        # Нормализуем время относительно первого кадра
        frame_times = []
        for frame in times_data:
            frame_times.append({
                'time': frame['time'] - start_time,
                'system_time': frame.get('system_time', 0)
            })
        
        return {
            'start_time': start_time,
            'end_time': end_time,
            'duration': duration,
            'frame_times': frame_times
        }
    
    @staticmethod
    def find_video_files(data_dir: str) -> List[str]:
        """Находит видео файлы в директории."""
        import os
        
        video_files = []
        for video_name in ['video.mp4', 'video_2.mp4']:
            video_path = os.path.join(data_dir, video_name)
            if os.path.exists(video_path):
                # Возвращаем относительный путь от корневой директории
                video_files.append(video_path)
        
        return video_files
