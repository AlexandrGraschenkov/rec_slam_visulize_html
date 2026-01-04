// Простая перемотка видео - найти все видео и перемотать первое на 15 секунд с паузой
const videos = document.querySelectorAll('video');
if (videos.length > 0) {
    const video = videos[0];
    video.pause();
    video.currentTime = 15;
} else {
    console.log('Видео не найдено');
}
