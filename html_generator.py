"""
Модуль для генерации HTML страницы.
"""

import json
from typing import List, Dict, Any


class HTMLGenerator:
    """Класс для генерации HTML страницы просмотра поездки."""
    
    def __init__(self):
        self.template = self._load_template()
    
    def _load_template(self) -> str:
        """Загружает HTML шаблон."""
        return """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Просмотр поездки</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: Arial, sans-serif;
            height: 100vh;
            overflow: hidden;
        }}
        
        .container {{
            display: flex;
            height: 100vh;
        }}
        
        .left-panel {{
            flex: 1;
            display: flex;
            flex-direction: column;
            border-right: 2px solid #ccc;
            min-width: 300px;
        }}
        
        .right-panel {{
            flex: 1;
            display: flex;
            flex-direction: column;
            min-width: 300px;
        }}
        
        .resize-handle {{
            width: 4px;
            background: #ccc;
            cursor: col-resize;
            flex-shrink: 0;
        }}
        
        .video-section {{
            flex: 1;
            display: flex;
            flex-direction: column;
            padding: 10px;
            min-height: 0;
            overflow: hidden;
        }}
        
        .video-container {{
            flex: 1;
            display: flex;
            flex-direction: column;
            margin-bottom: 10px;
            min-height: 0;
        }}
        
        .video-player {{
            width: 100%;
            height: 100%;
            margin-bottom: 10px;
        }}
        
        .video-switcher {{
            display: flex;
            gap: 10px;
            margin-bottom: 10px;
            flex-shrink: 0;
        }}
        
        .video-switch-btn {{
            padding: 8px 16px;
            background: #6c757d;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }}
        
        .video-switch-btn.active {{
            background: #007bff;
        }}
        
        .timeline {{
            height: 100px;
            background: #f0f0f0;
            border: 1px solid #ccc;
            position: relative;
            cursor: pointer;
            flex-shrink: 0;
        }}
        
        .timeline-marker {{
            position: absolute;
            top: 0;
            width: 2px;
            height: 100%;
            background: #ff0000;
            z-index: 10;
        }}
        
        .timeline-event {{
            position: absolute;
            top: 0;
            width: 4px;
            height: 100%;
            transform: translateX(-50%);
            z-index: 5;
            opacity: 0.8;
        }}
        
        .event-pothole {{ background: #e74c3c; }}
        .event-erased_markings {{ background: #f39c12; }}
        .event-garbage_on_road {{ background: #27ae60; }}
        .event-damaged_sign {{ background: #9b59b6; }}
        .event-manual {{ background: #3498db; }}
        .event-default {{ background: #95a5a6; }}
        
        .map-section {{
            flex: 1;
            display: flex;
            flex-direction: column;
        }}
        
        #map {{
            flex: 1;
            width: 100%;
        }}
        
        .device-info {{
            background: #f8f9fa;
            padding: 10px;
            border-bottom: 1px solid #dee2e6;
            cursor: pointer;
            flex-shrink: 0;
        }}
        
        .device-info h3 {{
            margin: 0 0 10px 0;
            font-size: 16px;
        }}
        
        .device-details {{
            display: none;
            font-size: 12px;
            color: #666;
        }}
        
        .device-details.show {{
            display: block;
        }}
        
        .controls {{
            padding: 10px;
            background: #f8f9fa;
            border-top: 1px solid #dee2e6;
            flex-shrink: 0;
        }}
        
        .play-pause-btn {{
            padding: 8px 16px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin-right: 10px;
        }}
        
        .time-display {{
            display: inline-block;
            margin-left: 10px;
            font-family: monospace;
        }}
        
        .arrow-marker {{
            background: transparent !important;
            border: none !important;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="left-panel">
            <div class="device-info" onclick="toggleDeviceInfo()">
                <h3>Информация об устройстве</h3>
                <div class="device-details" id="deviceDetails">
                    {device_info_html}
                </div>
            </div>
            
            <div class="video-section">
                <div class="video-container">
                    <div class="video-switcher" id="videoSwitcher">
                        {video_switcher_html}
                    </div>
                    {video_html}
                </div>
                
                <div class="timeline" id="timeline" onclick="seekToTime(event)">
                    <div class="timeline-marker" id="timelineMarker"></div>
                    {timeline_events_html}
                </div>
            </div>
            
            <div class="controls">
                <button class="play-pause-btn" id="playPauseBtn" onclick="togglePlayPause()">▶️ Воспроизведение</button>
                <span class="time-display" id="timeDisplay">00:00 / 00:00</span>
            </div>
        </div>
        
        <div class="resize-handle" id="resizeHandle"></div>
        
        <div class="right-panel">
            <div class="map-section">
                <div id="map"></div>
            </div>
        </div>
    </div>

    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        // Данные GPS
        const gpsData = {gps_data_json};
        
        // События
        const events = {events_json};
        
        // Информация об устройстве
        const deviceInfo = {device_info_json};
        
        // Данные временных меток кадров
        const frameTimes = {frame_times_json};
        
        // Временной диапазон
        const startTime = {start_time};
        const endTime = {end_time};
        const duration = endTime - startTime;
        
        // Инициализация карты
        const map = L.map('map').setView([gpsData[0].lat, gpsData[0].lon], 15);
        
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '© OpenStreetMap contributors'
        }}).addTo(map);
        
        // Создание траектории
        const trajectory = L.polyline(
            gpsData.map(point => [point.lat, point.lon]),
            {{color: 'blue', weight: 3}}
        ).addTo(map);
        
        // Функция для получения цвета события
        function getEventColor(eventType) {{
            const colors = {{
                'pothole': '#e74c3c',           // Красный - яма (опасность)
                'erased_markings': '#f39c12',   // Оранжевый - стертая разметка
                'garbage_on_road': '#27ae60',   // Зеленый - мусор на дороге
                'damaged_sign': '#9b59b6',      // Фиолетовый - поврежденный знак
                'manual': '#3498db',            // Синий - ручное событие
                'default': '#95a5a6'             // Серый - по умолчанию
            }};
            return colors[eventType] || colors['default'];
        }}
        
        // Добавление маркеров событий
        const eventMarkers = [];
        events.forEach(event => {{
            const eventColor = getEventColor(event.event_type);
            const marker = L.circleMarker([event.lat, event.lon], {{
                radius: 8,
                color: eventColor,
                fillColor: eventColor,
                fillOpacity: 0.7
            }}).addTo(map);
            
            marker.bindPopup(`
                <strong>${{event.event_type}}</strong><br>
                Время: ${{formatTime(event.time)}}<br>
                GPS: ${{event.lat.toFixed(6)}}, ${{event.lon.toFixed(6)}}<br>
                ${{event.type === 'pothole' ? 'Уверенность: ' + (event.confidence * 100).toFixed(1) + '%' : ''}}
            `);
            
            eventMarkers.push({{marker, time: event.time}});
        }});
        
        // Подгонка карты под траекторию
        map.fitBounds(trajectory.getBounds());
        
        // Получение видео элементов
        const video1 = document.getElementById('video1');
        const video2 = document.getElementById('video2');
        const videos = [video1, video2].filter(v => v);
        let currentVideoIndex = 0;
        let currentVideo = videos[currentVideoIndex];
        
        // Элементы управления
        const playPauseBtn = document.getElementById('playPauseBtn');
        const timeDisplay = document.getElementById('timeDisplay');
        const timeline = document.getElementById('timeline');
        const timelineMarker = document.getElementById('timelineMarker');
        
        let isPlaying = false;
        let currentTime = 0;
        
        // Синхронизация видео
        function syncVideos() {{
            if (currentVideo) {{
                currentVideo.currentTime = currentTime;
            }}
        }}
        
        // Переключение видео
        function switchVideo(index) {{
            if (videos[index]) {{
                // Скрываем все видео
                videos.forEach(video => {{
                    if (video) video.style.display = 'none';
                }});
                
                // Показываем выбранное видео
                videos[index].style.display = 'block';
                currentVideoIndex = index;
                currentVideo = videos[index];
                
                // Обновляем активную кнопку
                document.querySelectorAll('.video-switch-btn').forEach((btn, i) => {{
                    btn.classList.toggle('active', i === index);
                }});
                
                // Синхронизируем время
                if (currentVideo) {{
                    currentVideo.currentTime = currentTime;
                }}
            }}
        }}
        
        // Интерполяция GPS координат
        function interpolateGPS(time) {{
            // Находим две ближайшие GPS точки
            let point1 = null;
            let point2 = null;
            
            for (let i = 0; i < gpsData.length - 1; i++) {{
                if (gpsData[i].time <= time && gpsData[i + 1].time >= time) {{
                    point1 = gpsData[i];
                    point2 = gpsData[i + 1];
                    break;
                }}
            }}
            
            // Если время до первой точки
            if (time <= gpsData[0].time) {{
                return [gpsData[0].lat, gpsData[0].lon, gpsData[0].course];
            }}
            
            // Если время после последней точки
            if (time >= gpsData[gpsData.length - 1].time) {{
                return [gpsData[gpsData.length - 1].lat, gpsData[gpsData.length - 1].lon, gpsData[gpsData.length - 1].course];
            }}
            
            // Интерполяция между двумя точками
            if (point1 && point2) {{
                const ratio = (time - point1.time) / (point2.time - point1.time);
                const lat = point1.lat + (point2.lat - point1.lat) * ratio;
                const lon = point1.lon + (point2.lon - point1.lon) * ratio;
                
                // Интерполяция курса
                let course = null;
                if (point1.course !== null && point2.course !== null) {{
                    // Учитываем переход через 0/360 градусов
                    let courseDiff = point2.course - point1.course;
                    if (courseDiff > 180) courseDiff -= 360;
                    if (courseDiff < -180) courseDiff += 360;
                    course = point1.course + courseDiff * ratio;
                    if (course < 0) course += 360;
                    if (course >= 360) course -= 360;
                }} else if (point1.course !== null) {{
                    course = point1.course;
                }} else if (point2.course !== null) {{
                    course = point2.course;
                }}
                
                return [lat, lon, course];
            }}
            
            return [gpsData[0].lat, gpsData[0].lon, gpsData[0].course];
        }}
        
        // Расчет направления между двумя точками
        function calculateBearing(lat1, lon1, lat2, lon2) {{
            const dLon = (lon2 - lon1) * Math.PI / 180;
            const lat1Rad = lat1 * Math.PI / 180;
            const lat2Rad = lat2 * Math.PI / 180;
            
            const y = Math.sin(dLon) * Math.cos(lat2Rad);
            const x = Math.cos(lat1Rad) * Math.sin(lat2Rad) - Math.sin(lat1Rad) * Math.cos(lat2Rad) * Math.cos(dLon);
            
            let bearing = Math.atan2(y, x) * 180 / Math.PI;
            return (bearing + 360) % 360;
        }}
        
        // Обновление маркера на карте
        function updateMapMarker(time) {{
            const [lat, lon, course] = interpolateGPS(time);
            
            // Удаляем предыдущий маркер
            if (window.currentMarker) {{
                map.removeLayer(window.currentMarker);
            }}
            
            // Определяем направление движения
            let direction = course;
            if (direction === null || direction === undefined) {{
                // Находим ближайшие GPS точки для расчета направления
                let point1 = null;
                let point2 = null;
                
                for (let i = 0; i < gpsData.length - 1; i++) {{
                    if (gpsData[i].time <= time && gpsData[i + 1].time >= time) {{
                        point1 = gpsData[i];
                        point2 = gpsData[i + 1];
                        break;
                    }}
                }}
                
                if (point1 && point2) {{
                    direction = calculateBearing(point1.lat, point1.lon, point2.lat, point2.lon);
                }} else if (time <= gpsData[0].time && gpsData.length > 1) {{
                    // Если время до первой точки, используем направление к следующей
                    direction = calculateBearing(gpsData[0].lat, gpsData[0].lon, gpsData[1].lat, gpsData[1].lon);
                }} else if (time >= gpsData[gpsData.length - 1].time && gpsData.length > 1) {{
                    // Если время после последней точки, используем направление от предыдущей
                    const lastIndex = gpsData.length - 1;
                    direction = calculateBearing(gpsData[lastIndex - 1].lat, gpsData[lastIndex - 1].lon, gpsData[lastIndex].lat, gpsData[lastIndex].lon);
                }} else {{
                    direction = 0; // По умолчанию на север
                }}
            }}
            direction -= 90;
            
            // Создаем иконку стрелочки
            const arrowIcon = L.divIcon({{
                html: `<div style="transform: rotate(${{direction}}deg); font-size: 30px; color: #ff0000; text-align: center; line-height: 1;">➤</div>`,
                iconSize: [30, 30],
                iconAnchor: [15, 15],
                className: 'arrow-marker'
            }});
            
            // Создаем маркер со стрелочкой
            window.currentMarker = L.marker([lat, lon], {{icon: arrowIcon}}).addTo(map);
        }}
        
        // Обновление таймлайна
        function updateTimeline(time) {{
            const progress = (time - startTime) / duration;
            timelineMarker.style.left = (progress * 100) + '%';
        }}
        
        // Форматирование времени
        function formatTime(seconds) {{
            const mins = Math.floor(seconds / 60);
            const secs = Math.floor(seconds % 60);
            return mins.toString().padStart(2, '0') + ':' + secs.toString().padStart(2, '0');
        }}
        
        // Обновление отображения времени
        function updateTimeDisplay() {{
            const current = formatTime(currentTime);
            const total = formatTime(duration);
            timeDisplay.textContent = `${{current}} / ${{total}}`;
        }}
        
        // Переключение воспроизведения
        function togglePlayPause() {{
            if (isPlaying) {{
                if (currentVideo) currentVideo.pause();
                playPauseBtn.textContent = '▶️ Воспроизведение';
                isPlaying = false;
            }} else {{
                if (currentVideo) currentVideo.play();
                playPauseBtn.textContent = '⏸️ Пауза';
                isPlaying = true;
            }}
        }}
        
        // Переход к времени по клику на таймлайн
        function seekToTime(event) {{
            const rect = timeline.getBoundingClientRect();
            const x = event.clientX - rect.left;
            const progress = x / rect.width;
            const time = startTime + progress * duration;
            
            currentTime = time;
            syncVideos();
            updateMapMarker(time);
            updateTimeline(time);
            updateTimeDisplay();
        }}
        
        // Обработчики событий видео
        videos.forEach((video, index) => {{
            if (video) {{
                // Скрываем все видео кроме первого
                if (index > 0) {{
                    video.style.display = 'none';
                }}
                
                video.addEventListener('timeupdate', () => {{
                    if (video === currentVideo) {{
                        currentTime = video.currentTime;
                        updateMapMarker(currentTime);
                        updateTimeline(currentTime);
                        updateTimeDisplay();
                    }}
                }});
                
                video.addEventListener('play', () => {{
                    if (video === currentVideo) {{
                        isPlaying = true;
                        playPauseBtn.textContent = '⏸️ Пауза';
                    }}
                }});
                
                video.addEventListener('pause', () => {{
                    if (video === currentVideo) {{
                        isPlaying = false;
                        playPauseBtn.textContent = '▶️ Воспроизведение';
                    }}
                }});
            }}
        }});
        
        // Переключение информации об устройстве
        function toggleDeviceInfo() {{
            const details = document.getElementById('deviceDetails');
            details.classList.toggle('show');
        }}
        
        // Обработчик изменения размера панелей
        let isResizing = false;
        const resizeHandle = document.getElementById('resizeHandle');
        const leftPanel = document.querySelector('.left-panel');
        const rightPanel = document.querySelector('.right-panel');
        
        resizeHandle.addEventListener('mousedown', (e) => {{
            isResizing = true;
            document.addEventListener('mousemove', handleResize);
            document.addEventListener('mouseup', stopResize);
        }});
        
        function handleResize(e) {{
            if (!isResizing) return;
            
            const containerWidth = document.querySelector('.container').offsetWidth;
            const leftWidth = (e.clientX / containerWidth) * 100;
            const rightWidth = 100 - leftWidth;
            
            if (leftWidth > 20 && rightWidth > 20) {{
                leftPanel.style.flex = leftWidth;
                rightPanel.style.flex = rightWidth;
            }}
        }}
        
        function stopResize() {{
            isResizing = false;
            document.removeEventListener('mousemove', handleResize);
            document.removeEventListener('mouseup', stopResize);
        }}
        
        // Инициализация
        updateTimeDisplay();
        updateMapMarker(currentTime);
        updateTimeline(currentTime);
        
        // Инициализация переключателя видео
        if (videos.length > 1) {{
            switchVideo(0);
        }}
    </script>
</body>
</html>"""
    
    def generate_html(self, gps_data: List[Dict[str, Any]], events: List[Dict[str, Any]], 
                     device_info: Dict[str, Any], video_files: List[str], output_file: str, 
                     times_data: Dict[str, Any] = None) -> None:
        """
        Генерирует HTML страницу.
        
        Args:
            gps_data: GPS данные
            events: События
            device_info: Информация об устройстве
            video_files: Список видео файлов
            output_file: Путь к выходному файлу
        """
        # Сортируем события по времени
        events.sort(key=lambda x: x['time'])
        
        # Находим временной диапазон
        if times_data and times_data['duration'] > 0:
            # Используем данные из times_full.json для точной продолжительности видео
            start_time = 0
            end_time = times_data['duration']
        else:
            # Fallback на GPS данные (теперь время уже нормализовано)
            start_time = 0  # Начало записи всегда 0
            end_time = max(gps_data[-1]['time'], events[-1]['time'] if events else gps_data[-1]['time'])
        
        # Генерируем HTML компоненты
        device_info_html = self._generate_device_info_html(device_info)
        video_switcher_html = self._generate_video_switcher_html(video_files)
        video_html = self._generate_video_html(video_files)
        timeline_events_html = self._generate_timeline_events_html(events, start_time, end_time)
        
        # Заполняем шаблон
        frame_times_json = json.dumps(times_data.get('frame_times', []) if times_data else [])
        
        html_content = self.template.format(
            device_info_html=device_info_html,
            video_switcher_html=video_switcher_html,
            video_html=video_html,
            timeline_events_html=timeline_events_html,
            gps_data_json=json.dumps(gps_data),
            events_json=json.dumps(events),
            device_info_json=json.dumps(device_info),
            frame_times_json=frame_times_json,
            start_time=start_time,
            end_time=end_time
        )
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("HTML файл создан: {}".format(output_file))
    
    def _generate_device_info_html(self, device_info: Dict[str, Any]) -> str:
        """Генерирует HTML для информации об устройстве."""
        info_items = [
            "<p><strong>Устройство:</strong> {}</p>".format(device_info.get('device', 'Неизвестно')),
            "<p><strong>ОС:</strong> {}</p>".format(device_info.get('os', 'Неизвестно')),
            "<p><strong>Версия приложения:</strong> {}</p>".format(device_info.get('app_version', 'Неизвестно')),
            "<p><strong>Разрешение видео:</strong> {}</p>".format(device_info.get('video_resolution', 'Неизвестно')),
            "<p><strong>FPS:</strong> {}</p>".format(device_info.get('fps', 'Неизвестно')),
            "<p><strong>Режим записи:</strong> {}</p>".format(device_info.get('record_mode', 'Неизвестно'))
        ]
        
        return '\n'.join(info_items)
    
    def _generate_video_html(self, video_files: List[str]) -> str:
        """Генерирует HTML для видео плееров."""
        video_html = []
        
        for i, video_file in enumerate(video_files, 1):
            # Проверяем, является ли это URL или локальным путем
            if video_file.startswith('http'):
                # Это прямая ссылка на видео
                video_html.append('''
                    <video class="video-player" id="video{}" controls crossorigin="anonymous">
                        <source src="{}" type="video/mp4">
                        Ваш браузер не поддерживает видео.
                    </video>
                '''.format(i, video_file))
            else:
                # Это локальный файл
                video_html.append('''
                    <video class="video-player" id="video{}" controls>
                        <source src="{}" type="video/mp4">
                        Ваш браузер не поддерживает видео.
                    </video>
                '''.format(i, video_file))
        
        return '\n'.join(video_html)
    
    def _generate_video_switcher_html(self, video_files: List[str]) -> str:
        """Генерирует HTML для переключателя видео."""
        if len(video_files) <= 1:
            return ''
        
        switcher_html = []
        for i, video_file in enumerate(video_files):
            video_name = video_file.split('/')[-1]  # Получаем только имя файла
            switcher_html.append(
                '<button class="video-switch-btn" onclick="switchVideo({})" {}>Видео {}</button>'.format(
                    i, 'class="active"' if i == 0 else '', i + 1
                )
            )
        
        return '\n'.join(switcher_html)
    
    def _generate_timeline_events_html(self, events: List[Dict[str, Any]], 
                                     start_time: float, end_time: float) -> str:
        """Генерирует HTML для событий на таймлайне."""
        timeline_events = []
        
        for event in events:
            left_percent = ((event['time'] - start_time) / (end_time - start_time)) * 100
            timeline_events.append(
                '<div class="timeline-event event-{}" '
                'style="left: {}%" title="{}"></div>'.format(
                    event["event_type"], left_percent, event["event_type"]
                )
            )
        
        return ''.join(timeline_events)
