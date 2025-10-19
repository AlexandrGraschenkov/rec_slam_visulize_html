#!/usr/bin/env python3
"""
Скрипт для запуска Streamlit приложения.
"""

import subprocess
import sys
import os

def main():
    """Запускает Streamlit приложение."""
    try:
        # Проверяем, что мы в правильной директории
        if not os.path.exists('streamlit_app.py'):
            print("❌ Файл streamlit_app.py не найден в текущей директории")
            return 1
        
        print("🚀 Запуск Road Events Visualizer...")
        print("📱 Откройте браузер и перейдите по адресу: http://localhost:8501")
        print("⏹️  Для остановки нажмите Ctrl+C")
        print("-" * 50)
        
        # Запускаем Streamlit через виртуальное окружение
        venv_python = os.path.join(os.getcwd(), 'venv', 'bin', 'python')
        if os.path.exists(venv_python):
            subprocess.run([
                venv_python, '-m', 'streamlit', 'run', 'streamlit_app.py',
                '--server.port', '8501',
                '--server.address', 'localhost',
                '--browser.gatherUsageStats', 'false'
            ])
        else:
            # Fallback на системный Python
            subprocess.run([
                sys.executable, '-m', 'streamlit', 'run', 'streamlit_app.py',
                '--server.port', '8501',
                '--server.address', 'localhost',
                '--browser.gatherUsageStats', 'false'
            ])
        
        return 0
        
    except KeyboardInterrupt:
        print("\n👋 Приложение остановлено")
        return 0
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
