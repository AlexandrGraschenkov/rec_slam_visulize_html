#!/usr/bin/env python3
"""
Скрипт для генерации HTML-страницы просмотра поездки с картой, видео и событиями.
"""

import os
import sys
import argparse
from data_parser import DataParser
from yandex_downloader import YandexDownloader
from html_generator import HTMLGenerator

def generate_html_from_yandex(url: str) -> str:
    """
    Генерирует HTML из данных с Яндекс.Диска и возвращает как строку.
    
    Args:
        url: URL папки на Яндекс.Диске
        
    Returns:
        HTML содержимое как строка
    """
    # Инициализируем компоненты
    data_parser = DataParser()
    yandex_downloader = YandexDownloader()
    html_generator = HTMLGenerator()
    
    # Загружаем с Яндекс.Диска
    loaded_data = yandex_downloader.get_data_from_yandex_disk(url)
    
    if not loaded_data:
        raise Exception("Не удалось загрузить необходимые файлы")
    
    # Парсим данные
    gps_data = data_parser.parse_gps_data(loaded_data.get('gps.csv'))
    events = data_parser.parse_detections_data(loaded_data.get('detections.json'))
    device_info = data_parser.parse_device_info(loaded_data.get('device.txt'))
    
    # Парсим временные метки
    times_data = None
    if 'times_full.json' in loaded_data:
        times_data = data_parser.parse_times_data(loaded_data.get('times_full.json'))
    
    # Получаем ссылки на видео
    video_urls = yandex_downloader.get_video_urls_from_yandex_disk(url)
    video_files = list(video_urls.values())
    
    # Генерируем HTML и возвращаем как строку
    return html_generator.generate_html(gps_data, events, device_info, video_files, None, times_data)


def main():
    parser = argparse.ArgumentParser(description='Генерация HTML для просмотра поездки')
    parser.add_argument('input', help='URL Яндекс.Диска или путь к папке с данными')
    parser.add_argument('-o', '--output', default='index.html', help='Выходной HTML файл')
    parser.add_argument('--local', action='store_true', help='Использовать локальные файлы вместо загрузки с Яндекс.Диска')
    
    args = parser.parse_args()
    
    try:
        # Инициализируем компоненты
        data_parser = DataParser()
        html_generator = HTMLGenerator()
        
        if args.local:
            # Используем локальные файлы
            data_dir = args.input
            gps_file = os.path.join(data_dir, 'gps.csv')
            detections_file = os.path.join(data_dir, 'detections.json')
            device_file = os.path.join(data_dir, 'device.txt')
            
            # Проверяем наличие файлов
            for file_path in [gps_file, detections_file, device_file]:
                if not os.path.exists(file_path):
                    print(f"Файл не найден: {file_path}")
                    return 1
        else:
            # Загружаем с Яндекс.Диска
            print("Загрузка данных с Яндекс.Диска...")
            yandex_downloader = YandexDownloader()
            loaded_data = yandex_downloader.get_data_from_yandex_disk(args.input)
            
            if not loaded_data:
                print("Не удалось загрузить необходимые файлы")
                return 1
            
            gps_data = loaded_data.get('gps.csv')
            detections_data = loaded_data.get('detections.json')
            device_data = loaded_data.get('device.txt')
            times_data = loaded_data.get('times_full.json')
        
        # Парсим данные
        print("Парсинг GPS данных...")
        if args.local:
            gps_data = data_parser.parse_gps_data(gps_file)
        else:
            gps_data = data_parser.parse_gps_data(gps_data)
        
        # Получаем оригинальный start_time для нормализации событий
        gps_start_time = None
        if gps_data:
            gps_start_time = gps_data[0]['time'] if gps_data else None
        
        print("Парсинг событий...")
        if args.local:
            events = data_parser.parse_detections_data(detections_file)
        else:
            events = data_parser.parse_detections_data(detections_data)
        
        print("Парсинг информации об устройстве...")
        if args.local:
            device_info = data_parser.parse_device_info(device_file)
        else:
            device_info = data_parser.parse_device_info(device_data)
        
        # Парсим данные о временных метках кадров
        print("Парсинг временных меток...")
        if args.local:
            times_file = os.path.join(data_dir, 'times_full.json')
            if os.path.exists(times_file):
                times_data = data_parser.parse_times_data(times_file)
                print(f"Продолжительность видео: {times_data['duration']:.2f} секунд")
            else:
                print("Файл times_full.json не найден, используем данные GPS")
                times_data = None
        else:
            if times_data:
                times_data = data_parser.parse_times_data(times_data)
                print(f"Продолжительность видео: {times_data['duration']:.2f} секунд")
            else:
                print("Файл times_full.json не найден, используем данные GPS")
                times_data = None
        
        # Ищем видео файлы
        if args.local:
            data_dir = args.input
            video_files = data_parser.find_video_files(data_dir)
            print(f"Найдено локальных видео файлов: {len(video_files)}")
        else:
            # Получаем прямые ссылки на видео с Яндекс.Диска
            print("Получение ссылок на видео с Яндекс.Диска...")
            video_urls = yandex_downloader.get_video_urls_from_yandex_disk(args.input)
            video_files = list(video_urls.values())
            print(f"Найдено ссылок на видео: {len(video_files)}")
            for video_name, video_url in video_urls.items():
                print(f"  {video_name}: {video_url}")
            
            if not video_files:
                print("Предупреждение: Видео файлы не найдены. HTML будет создан без видео.")
        
        # Генерируем HTML
        print("Генерация HTML...")
        html_content = html_generator.generate_html(gps_data, events, device_info, video_files, args.output, times_data)
        
        print("Готово!")
        
        return 0
        
    except Exception as e:
        print(f"Ошибка: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
