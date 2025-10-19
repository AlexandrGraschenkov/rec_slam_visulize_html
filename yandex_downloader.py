"""
Модуль для загрузки данных с Яндекс.Диска.
Работает с данными в памяти без скачивания файлов на диск.
"""

import json
import urllib.parse as ul
import requests
from typing import Dict, Optional, Any


class YandexDownloader:
    """Класс для загрузки данных с Яндекс.Диска в память."""
    
    def __init__(self):
        self.session = requests.Session()
    
    def get_data_from_yandex_disk(self, url: str) -> Dict[str, Any]:
        """
        Загружает данные с Яндекс.Диска в память.
        
        Args:
            url: URL папки на Яндекс.Диске
            
        Returns:
            Словарь с данными файлов в памяти
        """
        # Извлекаем ID папки из URL
        folder_id = self._extract_folder_id(url)
        if not folder_id:
            print("Не удалось извлечь ID папки из URL")
            return {}
        
        # Получаем список всех файлов в папке одним запросом
        files_data = self._get_all_files_from_folder(folder_id, url)
        if not files_data:
            print("Не удалось получить список файлов")
            return {}
        
        # Загружаем нужные файлы в память
        required_files = ['detections.json', 'gps.csv', 'device.txt', 'times_full.json']
        loaded_data = {}
        
        for filename in required_files:
            if filename in files_data:
                print(f"Загружаем {filename} в память...")
                file_content = self._download_file_content(files_data[filename])
                if file_content is not None:
                    loaded_data[filename] = file_content
                    print(f"Загружен: {filename}")
            else:
                print(f"Файл {filename} не найден")
        
        return loaded_data
    
    def get_video_urls_from_yandex_disk(self, url: str) -> Dict[str, str]:
        """
        Получает прямые ссылки на видео файлы с Яндекс.Диска.
        
        Args:
            url: URL папки на Яндекс.Диске
            
        Returns:
            Словарь с прямыми ссылками на видео файлы
        """
        # Извлекаем ID папки из URL
        folder_id = self._extract_folder_id(url)
        if not folder_id:
            print("Не удалось извлечь ID папки из URL")
            return {}
        
        # Получаем список всех файлов в папке одним запросом
        files_data = self._get_all_files_from_folder(folder_id, url)
        if not files_data:
            print("Не удалось получить список файлов")
            return {}
        
        # Ищем видео файлы
        video_files = ['video', 'video_2'] # видео файлы не имеют расширения
        video_urls = {}
        
        for video_filename in video_files:
            if video_filename in files_data:
                video_url = files_data[video_filename].get('file')
                if video_url:
                    video_urls[video_filename] = video_url
                    print(f"Найдена ссылка на видео: {video_filename}")
        
        return video_urls
    
    def _get_all_files_from_folder(self, folder_id: str, url: str) -> Dict[str, Any]:
        """
        Получает список всех файлов в папке одним запросом.
        
        Args:
            folder_id: ID папки
            url: URL папки на Яндекс.Диске
            
        Returns:
            Словарь с информацией о файлах
        """
        try:
            # Извлекаем путь к папке из URL
            folder_path = self._extract_folder_path(url)
            print(f"Путь к папке: {folder_path}")
            
            # Генерируем URL для получения списка всех файлов
            api_url = self._generate_api_url(folder_id, folder_path)
            print(f"API URL: {api_url}")
            
            # Получаем список файлов
            json_response = self._request_json(api_url)
            if not json_response or "_embedded" not in json_response or "items" not in json_response["_embedded"]:
                print("Не удалось получить список файлов")
                return {}
            
            files_data = {}
            for item in json_response["_embedded"]["items"]:
                if item.get("type") == "file":
                    filename = item.get("name")
                    files_data[filename] = item
            
            print(f"Найдено файлов: {len(files_data)}")
            return files_data
            
        except Exception as e:
            print(f"Ошибка при получении списка файлов: {e}")
            return {}
    
    def _download_file_content(self, file_info: Dict[str, Any]) -> Optional[str]:
        """
        Загружает содержимое файла в память.
        
        Args:
            file_info: Информация о файле из API
            
        Returns:
            Содержимое файла как строка или None при ошибке
        """
        try:
            if "file" not in file_info:
                print("Нет ссылки для скачивания файла")
                return None
            
            download_url = file_info["file"]
            response = self.session.get(download_url)
            
            if response.status_code == 200:
                return response.text
            else:
                print(f"Ошибка загрузки файла: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Ошибка при загрузке содержимого файла: {e}")
            return None
    
    def _extract_folder_id(self, url: str) -> Optional[str]:
        """
        Извлекает ID папки из URL.
        
        Args:
            url: URL папки на Яндекс.Диске
            
        Returns:
            ID папки или None при ошибке
        """
        import re
        match = re.search(r'/d/([^/]+)', url)
        return match.group(1) if match else None
    
    def _extract_folder_path(self, url: str) -> str:
        """
        Извлекает путь к папке из URL.
        
        Args:
            url: URL папки на Яндекс.Диске
            
        Returns:
            Путь к папке (например: /Default/2025-10-18_13-29-23_88113461-A83)
        """
        import re
        # Ищем путь после ID папки
        match = re.search(r'/d/[^/]+(.*)', url)
        if match:
            path = match.group(1)
            # Убираем ведущий слэш если есть
            if path.startswith('/'):
                path = path[1:]
            # Добавляем ведущий слэш для API
            return '/' + path if path else ""
        return ""
    
    def _generate_api_url(self, folder_id: str, path: str = "") -> str:
        """
        Генерирует URL для API запроса.
        
        Args:
            folder_id: ID папки
            path: Путь к файлу или папке
            
        Returns:
            URL для API запроса
        """
        # Используем тот же подход, что и в video_downloader.py
        base_url = f"https://yadi.sk/d/{folder_id}"
        key = ul.quote(base_url, safe="")
        path_key = ul.quote(f"{path}", safe="") if path else ""
        
        api_url = f"https://cloud-api.yandex.net/v1/disk/public/resources?public_key={key}&path={path_key}&limit=1000"
        return api_url
    
    def _request_json(self, url: str) -> Optional[dict]:
        """
        Выполняет JSON запрос.
        
        Args:
            url: URL для запроса
            
        Returns:
            JSON данные или None при ошибке
        """
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Ошибка запроса: {response.status_code}")
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"Ошибка при выполнении запроса: {e}")
        
        return None
    
