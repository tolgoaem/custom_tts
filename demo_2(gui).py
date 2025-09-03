import tkinter as tk
#import tk
from tkinter import filedialog
#from tk import filedialog
from tkinter import messagebox
#from tk import messagebox
from tkinter import scrolledtext
#from tk import scrolledtext
import os
import threading
from custom_tts import Custom_TTS
import pygame  # 추가된 부분

class TTS_GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TTS Demo")
        self.root.geometry("500x400")
        
        # TTS 모듈 초기화
        self.tts_module = Custom_TTS()
        self.tts_module.set_model()

        # pygame 초기화
        pygame.mixer.init()  # 추가된 부분

        # 샘플 화자 음성 파일 입력
        self.label_sample = tk.Label(root, text="Sample MP3 File:")
        self.label_sample.pack()
        self.entry_sample = tk.Entry(root, width=40)
        self.entry_sample.pack()
        self.btn_browse = tk.Button(root, text="Browse", command=self.browse_file)
        self.btn_browse.pack()

        self.btn_load_sample = tk.Button(root, text="Load Sample Voice", command=self.load_sample_voice)
        self.btn_load_sample.pack()

        # 텍스트 입력
        self.label_text = tk.Label(root, text="Text for TTS:")
        self.label_text.pack()
        self.entry_text = tk.Entry(root, width=40)
        self.entry_text.pack()

        self.btn_generate_tts = tk.Button(root, text="Generate TTS", command=self.generate_tts)
        self.btn_generate_tts.pack()

        # TTS 음성 재생 버튼
        self.btn_play_tts = tk.Button(root, text="Play TTS", command=self.play_tts)
        self.btn_play_tts.pack()

        # 출력 창
        self.output_text = scrolledtext.ScrolledText(root, height=10, width=50)
        self.output_text.pack()

        self.log("TTS System Initialized.")

    def log(self, message):
        """출력창에 로그 메시지를 추가하는 함수"""
        self.output_text.insert(tk.END, message + '\n')
        self.output_text.see(tk.END)

    def browse_file(self):
        """사용자가 샘플 음성 파일을 선택할 수 있도록 파일 다이얼로그를 여는 함수"""
        file_path = filedialog.askopenfilename(
            title="Select MP3 File",
            filetypes=(("MP3 files", "*.mp3;*.wav;*.acc;*.m4a"), ("All files", "*.*"))
        )
        if file_path:
            self.entry_sample.delete(0, tk.END)
            self.entry_sample.insert(0, file_path)

    def load_sample_voice(self):
        """샘플 음성 파일을 로드하여 화자의 목소리를 임베딩"""
        sample_path = self.entry_sample.get()
        if os.path.exists(sample_path):
            self.log(f"Loading sample voice from {sample_path}")
            self.tts_module.get_reference_speaker(speaker_path=sample_path)
            self.log("Sample voice loaded successfully.")
        else:
            messagebox.showerror("Error", "Sample MP3 file not found.")

    def generate_tts(self):
        """입력된 텍스트로 TTS 생성"""
        text = self.entry_text.get()
        if text:
            self.log(f"Generating TTS for text: {text}")
            threading.Thread(target=self._tts_thread, args=(text,)).start()
        else:
            messagebox.showerror("Error", "Please enter text for TTS.")

    def _tts_thread(self, text):
        """TTS 생성 비동기 작업"""
        try:
            self.tts_module.make_speech(text)
            self.log("TTS generation completed.")
        except Exception as e:
            self.log(f"Error generating TTS: {e}")

    def play_tts(self):
        """생성된 TTS 음성을 재생"""
        tts_path = f'./output/result_{self.tts_module.result_cnt-1}.wav'
        
        if os.path.exists(tts_path):
            self.log("Playing generated TTS.")
            pygame.mixer.music.load(tts_path)  # 음성 파일 로드
            pygame.mixer.music.play()  # 음성 재생

            # 재생 완료 후 파일 해제 처리
            while pygame.mixer.music.get_busy():  # 음악이 재생 중인지 확인
                continue  # 재생 중이라면 계속 기다림

            # 재생이 끝난 후 stop 호출 (명시적으로)
            pygame.mixer.music.stop()  # 파일 사용 해제
            self.log("TTS playback completed and file released.")
        else:
            messagebox.showerror("Error", "TTS file not found. Please generate TTS first.")



if __name__ == "__main__":
    root = tk.Tk()
    app = TTS_GUI(root)
    root.mainloop()
