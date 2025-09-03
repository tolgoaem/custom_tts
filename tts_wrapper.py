"""
SafeTTS - Custom_TTS의 안전한 래퍼 클래스
기존 코드를 수정하지 않고 CLI에서 안전하게 사용할 수 있도록 래핑
"""

import os
import sys
import subprocess
from datetime import datetime

# CLI용 최소 의존성으로 직접 import
import torch
from openvoice.api import ToneColorConverter
from melo.api import TTS


class SafeTTS:
    """
    Custom_TTS를 안전하게 래핑하여 CLI에서 사용 가능하도록 하는 클래스
    - target_se 미설정 문제 해결
    - 기본 화자 목소리로 TTS 생성
    """
    
    def __init__(self, model_path='checkpoints_v2', output_path='output'):
        """
        SafeTTS 초기화
        
        Args:
            model_path (str): 모델 경로
            output_path (str): 출력 경로
        """
        print("🔧 SafeTTS 초기화 중...")
        self.model_path = model_path
        self.output_path = output_path
        self.result_cnt = 0
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        print(f'사용 환경: {self.device}')
        self.initialized = False
        
        # output 폴더 생성
        os.makedirs(self.output_path, exist_ok=True)
        
    def initialize(self, language='KR'):
        """
        TTS 모델 초기화 및 설정 - 한국어 전용
        
        Args:
            language (str): 언어 코드 (기본: 'KR', 한국어만 지원)
        """
        try:
            print("📡 TTS 모델 로딩 중...")
            print("🌍 언어 설정: KR (한국어 전용)")
            
            # 한국어만 강제 사용
            language = 'KR'
            
            # 톤 변경 모델 로드
            self.tone_color_converter = ToneColorConverter(f'{self.model_path}/converter/config.json', device=self.device)
            self.tone_color_converter.load_ckpt(f'{self.model_path}/converter/checkpoint.pth')
            print('톤 변경 모델 로드 완료')

            # TTS 모델 선언
            self.tts_model = TTS(language=language, device=self.device)
            print('TTS 모델 로드 완료')

            # 기본 화자 음성 임베딩
            speaker_ids = self.tts_model.hps.data.spk2id
            for speaker_key in speaker_ids.keys():
                self.speaker_id = speaker_ids[speaker_key]
                speaker_key = speaker_key.lower().replace('_', '-')
            self.source_se = torch.load(f'{self.model_path}/base_speakers/ses/{speaker_key}.pth', map_location=self.device)
            print('기본 화자 음성 임베딩 완료')
            
            # 기본 화자 목소리 사용 (샘플 음성 없이 TTS 가능)
            self.target_se = self.source_se
            print("🎯 기본 화자 음성으로 설정 완료")
            
            self.initialized = True
            print("✅ TTS 시스템 초기화 완료!")
            return True
            
        except Exception as e:
            print(f"❌ 초기화 실패: {e}")
            print(f"🔍 오류 상세: {type(e).__name__}")
            import traceback
            print("📋 전체 오류 정보:")
            traceback.print_exc()
            return False
    
    def generate_speech(self, text, speed=1.1, custom_filename=None, auto_play=True):
        """
        텍스트를 음성으로 변환
        
        Args:
            text (str): 변환할 텍스트
            speed (float): 재생 속도 (기본: 1.1)
            custom_filename (str): 사용자 지정 파일명 (None이면 timestamp 사용)
            auto_play (bool): 생성 후 자동 재생 여부 (기본: True)
            
        Returns:
            tuple: (성공 여부, 결과 파일 경로)
        """
        if not self.initialized:
            return False, "TTS 시스템이 초기화되지 않았습니다. initialize()를 먼저 호출하세요."
        
        if not text or not text.strip():
            return False, "텍스트가 비어있습니다."
        
        try:
            print(f"🗣️  TTS 생성 중: '{text[:50]}{'...' if len(text) > 50 else ''}'")
            
            # TTS 생성 로직
            src_path = f'{self.output_path}/tmp.wav'
            
            # TTS 수행
            self.tts_model.tts_to_file(text, self.speaker_id, src_path, speed=speed)
            print('TTS 생성 완료')

            # 파일명 결정 (timestamp 또는 사용자 지정)
            if custom_filename:
                # 확장자 확인 및 추가
                if not custom_filename.endswith('.wav'):
                    custom_filename += '.wav'
                result_path = f'{self.output_path}/{custom_filename}'
            else:
                # timestamp 기반 파일명 생성
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                result_path = f'{self.output_path}/tts_{timestamp}.wav'

            # 목소리 변조 수행
            self.tone_color_converter.convert(audio_src_path=src_path, 
                                            src_se=self.source_se, 
                                            tgt_se=self.target_se, 
                                            output_path=result_path)
            print('목소리 변조 완료')
            self.result_cnt += 1
            
            if os.path.exists(result_path):
                print(f"✅ TTS 파일 생성 완료: {result_path}")
                
                # 자동 재생 수행
                if auto_play:
                    self.play_audio(result_path)
                
                return True, result_path
            else:
                return False, "결과 파일이 생성되지 않았습니다."
                
        except Exception as e:
            return False, f"TTS 생성 중 오류 발생: {e}"
    
    def get_last_result_path(self):
        """
        마지막으로 생성된 결과 파일 경로 반환
        
        Returns:
            str: 파일 경로 또는 None
        """
        if not self.initialized or self.result_cnt == 0:
            return None
        
        result_path = f"{self.output_path}/result_{self.result_cnt-1}.wav"
        return result_path if os.path.exists(result_path) else None
    
    def get_output_directory(self):
        """
        출력 디렉토리 경로 반환
        
        Returns:
            str: 출력 디렉토리 경로
        """
        return self.output_path if self.initialized else None
    
    def play_audio(self, file_path):
        """
        aplay를 사용하여 오디오 파일 재생
        
        Args:
            file_path (str): 재생할 오디오 파일 경로
        """
        try:
            print(f"🔊 오디오 재생 중: {os.path.basename(file_path)}")
            
            # aplay 명령 실행
            result = subprocess.run(['aplay', file_path], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=30)
            
            if result.returncode == 0:
                print("🎵 재생 완료!")
            else:
                print(f"⚠️ 재생 중 경고: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("⏰ 재생 시간 초과 (30초)")
        except FileNotFoundError:
            print("❌ aplay 명령을 찾을 수 없습니다. alsa-utils 패키지를 설치하세요:")
            print("   sudo apt install alsa-utils")
        except Exception as e:
            print(f"❌ 재생 중 오류: {e}")


def main():
    """
    테스트용 메인 함수
    """
    print("SafeTTS 래퍼 클래스 테스트")
    
    # SafeTTS 인스턴스 생성
    safe_tts = SafeTTS()
    
    # 초기화
    if not safe_tts.initialize():
        print("초기화 실패")
        return
    
    # 테스트 텍스트로 TTS 생성
    test_text = "안녕하세요. SafeTTS 테스트입니다."
    success, result = safe_tts.generate_speech(test_text)
    
    if success:
        print(f"✅ TTS 생성 성공: {result}")
    else:
        print(f"❌ TTS 생성 실패: {result}")


if __name__ == "__main__":
    main()
