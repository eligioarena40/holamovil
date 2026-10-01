import os
import threading
import time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.clock import Clock

# Usamos ffpyplayer para un control preciso del audio y compatibilidad con Android
from ffpyplayer.player import MediaPlayer

class AudioPlayerWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(AudioPlayerWidget, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 10

        # Ruta del audio (Pon un archivo llamado 'cancion.mp3' en la misma carpeta)
        self.audio_path = "cancion.mp3"
        self.player = None
        self.duration = 0
        self.is_seeking = False  # Evita conflicto de hilos mientras arrastras el puntero

        # Etiqueta de información
        self.label_status = Label(text="Presiona Play para iniciar", font_size=18)
        self.add_widget(self.label_status)

        # Barra de tiempo (Slider)
        self.slider = Slider(min=0, max=100, value=0, value_track=True, value_track_color=[0, 1, 0, 1])
        # Evento cuando el usuario suelta el puntero del Slider
        self.slider.bind(on_touch_up=self.on_slider_release)
        # Evento cuando el usuario empieza a tocar/arrastrar el Slider
        self.slider.bind(on_touch_down=self.on_slider_touch)
        self.add_widget(self.slider)

        # Botón de reproducción
        self.btn_play = Button(text="Play / Pause", size_hint=(1, 0.3))
        self.btn_play.bind(on_press=self.toggle_playback)
        self.add_widget(self.btn_play)

        # Iniciar el reproductor en pausa
        if os.path.exists(self.audio_path):
            self.player = MediaPlayer(self.audio_path)
            self.player.set_pause(True)
            # Esperar un momento a que ffpyplayer cargue los metadatos para obtener la duración
            Clock.schedule_once(self.get_media_info, 0.5)
        else:
            self.label_status.text = "Error: 'cancion.mp3' no encontrado."

    def get_media_info(self, dt):
        if self.player:
            # Obtiene los metadatos de forma segura
            metadata = self.player.get_metadata()
            self.duration = metadata.get('duration') if metadata else None
            
            # Validamos que la duración no sea None y sea mayor a 0
            if self.duration is not None and self.duration > 0:
                self.slider.max = self.duration
                self.label_status.text = f"Audio cargado. Duración: {int(self.duration)}s"
                # Inicia el hilo de actualización continuo
                threading.Thread(target=self.update_slider_loop, daemon=True).start()
            else:
                # Si ffpyplayer no ha terminado de cargar, reintentamos en 0.2 segundos
                Clock.schedule_once(self.get_media_info, 0.2)

    def toggle_playback(self, instance):
        if self.player:
            # Invierte el estado actual de pausa
            is_paused = self.player.get_pause()
            self.player.set_pause(not is_paused)

    def on_slider_touch(self, instance, touch):
        # Si el toque cae dentro del Slider, avisamos que el usuario está interactuando
        if instance.collide_point(*touch.pos):
            self.is_seeking = True

    def on_slider_release(self, instance, touch):
        # Al soltar el puntero, cambiamos la posición del audio (Seek)
        if instance.collide_point(*touch.pos) and self.is_seeking:
            target_time = self.slider.value
            if self.player:
                self.player.seek(target_time, relative=False)
            # Devolvemos el control al bucle de actualización tras un leve retraso
            Clock.schedule_once(self.reset_seeking, 0.2)

    def reset_seeking(self, dt):
        self.is_seeking = False

    def update_slider_loop(self):
        while True:
            if self.player and not self.is_seeking:
                # Obtiene el tiempo actual de reproducción
                current_time = self.player.get_pts()
                # Actualiza la interfaz gráfica de forma segura mediante Kivy Clock
                Clock.schedule_once(lambda dt, t=current_time: self.set_slider_value(t))
            time.sleep(0.5)

    def set_slider_value(self, current_time):
        if not self.is_seeking and current_time is not None:
            self.slider.value = current_time
            self.label_status.text = f"Progreso: {int(current_time)}s / {int(self.duration)}s"

class AudioApp(App):
    def build(self):
        return AudioPlayerWidget()

if __name__ == '__main__':
    AudioApp().run()