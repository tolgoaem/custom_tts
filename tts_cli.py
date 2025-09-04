#!/usr/bin/env python3
"""
고급 TTS CLI 도구
"""

import argparse
import sys
import os
import time  # 시간 측정을 위한 모듈 추가
from custom_tts import Custom_TTS

def print_banner():
    print("🎤 ═══════════════════════════════════════════════════════")
    print("   Simple TTS CLI - 한국어 텍스트 음성 변환 도구")
    print("═══════════════════════════════════════════════════════")

def main():
    parser = argparse.ArgumentParser(
        description="한국어 텍스트를 음성으로 변환하는 CLI 도구",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python tts_cli.py "안녕하세요"
  python tts_cli.py "빠르게 말하기" --speed 1.5
  python tts_cli.py "테스트" --output my_audio
  python tts_cli.py "조용히" --no-play --quiet
        """
    )
    
    parser.add_argument("text", help="음성으로 변환할 텍스트")
    parser.add_argument("--speed", "-s", type=float, default=1.1, help="음성 재생 속도 (기본: 1.1)")
    parser.add_argument("--output", "-o", type=str, default=None, help="출력 파일명")
    parser.add_argument("--no-play", action="store_true", help="TTS 생성 후 자동 재생 비활성화")
    parser.add_argument("--quiet", "-q", action="store_true", help="진행상황 메시지 최소화")
    parser.add_argument("--conversion", "-c", action="store_true", help="음성 변조 사용 (기본: 단순 TTS)")
    
    args = parser.parse_args()
    
    if not args.quiet:
        print_banner()
    
    # 전체 시작 시간 기록
    total_start_time = time.time()
    
    try:
        if not args.quiet:
            print("🔧 TTS 시스템 초기화 중...")
        
        # TTS 인스턴스 생성
        tts = Custom_TTS()
        
        # 모델 설정
        tts.set_model(language='KR')
        
        if not args.quiet:
            print(f"🔧  텍스트 처리 중: '{args.text[:50]}{'...' if len(args.text) > 50 else ''}'")
            print(f"⚡ 속도: {args.speed}x")
        
        # TTS 생성 시작 시간 기록
        tts_start_time = time.time()
        
        # TTS 생성
        if args.conversion:
            # 음성 변조 사용 (기존 방식)
            tts.make_speech(args.text, speed=args.speed)
            result_path = f"{tts.output_path}/result_{tts.result_cnt-1}.wav"
        else:
            # 단순 TTS 사용
            result_path = tts.make_simple_speech(
                args.text, 
                speed=args.speed, 
                output_filename=args.output
            )
        
        # TTS 생성 완료 시간 기록
        tts_end_time = time.time()
        tts_duration = tts_end_time - tts_start_time
        
        if result_path and os.path.exists(result_path):
            # 파일 크기 계산
            file_size = os.path.getsize(result_path)
            
            print(f"✅ TTS 생성 완료!")
            print(f"📁 결과 파일: {result_path}")
            print(f"📊 파일 크기: {file_size:,} bytes")
            print(f"⏱️  TTS 생성 시간: {tts_duration:.2f}초")
            
            # 자동 재생
            if not args.no_play:
                try:
                    import subprocess
                    print("🔊 오디오 재생 중...")
                    subprocess.run(['aplay', result_path], check=True)
                    print("🎵 재생 완료!")
                except subprocess.CalledProcessError:
                    print("⚠️ 재생 실패 (aplay 명령을 찾을 수 없음)")
                except FileNotFoundError:
                    print("⚠️ aplay 명령을 찾을 수 없습니다. alsa-utils를 설치하세요:")
                    print("   sudo apt install alsa-utils")
            
            # 전체 처리 시간 계산
            total_end_time = time.time()
            total_duration = total_end_time - total_start_time
            
            print(f"⏱️  전체 처리 시간: {total_duration:.2f}초")
            
            if not args.quiet:
                print()
                print("💡 생성된 음성 파일을 재생하려면:")
                print(f"   aplay {result_path}")
        else:
            print("❌ TTS 생성 실패")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  사용자에 의해 중단되었습니다.")
        sys.exit(130)
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        if not args.quiet:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
