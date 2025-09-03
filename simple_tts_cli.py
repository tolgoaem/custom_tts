#!/usr/bin/env python3
"""
Simple TTS CLI - 한국어 텍스트를 음성으로 변환하는 간단한 CLI 도구

사용법:
    python simple_tts_cli.py "변환할 텍스트"
    python simple_tts_cli.py "변환할 텍스트" --speed 1.2
    python simple_tts_cli.py "변환할 텍스트" --output custom_output

예시:
    python simple_tts_cli.py "안녕하세요. 한국어 TTS 테스트입니다."
"""

import sys
import os
import argparse
import time
try:
    from tts_wrapper import SafeTTS
except Exception as e:
    print(f"❌ TTS 모듈 로드 실패: {e}")
    print("💡 해결방법: MeCab 사전이 설치되지 않았을 수 있습니다.")
    print("   다음 명령어를 실행하세요:")
    print("   python -m unidic download")
    sys.exit(1)


def print_banner():
    """CLI 시작 배너 출력"""
    print("🎤 ═══════════════════════════════════════════════════════")
    print("   Simple TTS CLI - 한국어 텍스트 음성 변환 도구")
    print("   Real-time Zero-shot TTS for Korean")
    print("═══════════════════════════════════════════════════════")
    print()


def print_usage():
    """사용법 출력"""
    print("📖 사용법:")
    print("   python simple_tts_cli.py \"변환할 텍스트\"")
    print("   python simple_tts_cli.py \"텍스트\" --speed 1.2")
    print("   python simple_tts_cli.py \"텍스트\" --output my_output")
    print()
    print("📝 예시:")
    print("   python simple_tts_cli.py \"안녕하세요. 테스트입니다.\"")
    print("   python simple_tts_cli.py \"빠르게 말하기\" --speed 1.5")
    print()


def validate_text(text):
    """
    입력 텍스트 유효성 검사
    
    Args:
        text (str): 검사할 텍스트
        
    Returns:
        tuple: (유효 여부, 오류 메시지)
    """
    if not text:
        return False, "텍스트가 비어있습니다."
    
    text = text.strip()
    if not text:
        return False, "공백만 포함된 텍스트입니다."
    
    if len(text) > 1000:
        return False, f"텍스트가 너무 깁니다. (최대 1000자, 현재 {len(text)}자)"
    
    return True, text


def validate_speed(speed):
    """
    속도 값 유효성 검사
    
    Args:
        speed (float): 검사할 속도 값
        
    Returns:
        tuple: (유효 여부, 오류 메시지 또는 정규화된 값)
    """
    try:
        speed = float(speed)
        if speed < 0.5 or speed > 3.0:
            return False, "속도는 0.5에서 3.0 사이여야 합니다."
        return True, speed
    except ValueError:
        return False, "유효하지 않은 속도 값입니다."


def main():
    """메인 함수"""
    # 명령행 인자 파서 설정
    parser = argparse.ArgumentParser(
        description="한국어 텍스트를 음성으로 변환하는 CLI 도구",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python simple_tts_cli.py "안녕하세요"
  python simple_tts_cli.py "빠르게 말하기" --speed 1.5
  python simple_tts_cli.py "테스트" --output my_audio
  python simple_tts_cli.py "조용히" --no-play --quiet
        """
    )
    
    parser.add_argument(
        "text",
        help="음성으로 변환할 텍스트"
    )
    
    parser.add_argument(
        "--speed", "-s",
        type=float,
        default=1.1,
        help="음성 재생 속도 (기본: 1.1, 범위: 0.5-3.0)"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="출력 파일명 (기본: timestamp 기반 자동 생성)"
    )
    
    parser.add_argument(
        "--no-play",
        action="store_true",
        help="TTS 생성 후 자동 재생 비활성화"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="진행상황 메시지 최소화"
    )
    
    # 인자가 없으면 도움말 출력
    if len(sys.argv) == 1:
        print_banner()
        print_usage()
        parser.print_help()
        sys.exit(0)
    
    # 명령행 인자 파싱
    try:
        args = parser.parse_args()
    except SystemExit:
        sys.exit(1)
    
    # 배너 출력 (quiet 모드가 아닐 때)
    if not args.quiet:
        print_banner()
    
    # 텍스트 유효성 검사
    valid, result = validate_text(args.text)
    if not valid:
        print(f"❌ 오류: {result}")
        sys.exit(1)
    
    text = result
    
    # 속도 유효성 검사
    valid, result = validate_speed(args.speed)
    if not valid:
        print(f"❌ 오류: {result}")
        sys.exit(1)
    
    speed = result
    
    # 출력 디렉토리 설정
    output_dir = "output"
    try:
        os.makedirs(output_dir, exist_ok=True)
    except Exception as e:
        print(f"❌ 출력 디렉토리 생성 실패: {e}")
        sys.exit(1)
    
    # TTS 처리 시작
    start_time = time.time()
    
    try:
        # SafeTTS 인스턴스 생성
        if not args.quiet:
            print("🔧 TTS 시스템 초기화 중...")
        
        safe_tts = SafeTTS(output_path=output_dir)
        
        # 초기화
        if not safe_tts.initialize():
            print("❌ TTS 시스템 초기화 실패")
            sys.exit(1)
        
        # TTS 생성
        if not args.quiet:
            print(f"🗣️  텍스트 처리 중: '{text[:50]}{'...' if len(text) > 50 else ''}'")
            print(f"⚡ 속도: {speed}x")
        
        # 재생 여부 결정 (--no-play 옵션의 반대)
        auto_play = not args.no_play
        
        success, result_path = safe_tts.generate_speech(
            text, 
            speed=speed, 
            custom_filename=args.output,
            auto_play=auto_play
        )
        
        if success:
            elapsed_time = time.time() - start_time
            file_size = os.path.getsize(result_path) if os.path.exists(result_path) else 0
            
            print(f"✅ 완료!")
            print(f"📁 결과 파일: {result_path}")
            print(f"📊 파일 크기: {file_size:,} bytes")
            print(f"⏱️  처리 시간: {elapsed_time:.2f}초")
            
            if not args.quiet:
                print()
                print("💡 생성된 음성 파일을 재생하려면:")
                print(f"   aplay {result_path}  # Linux")
                print(f"   afplay {result_path}  # macOS")
                print()
        
        else:
            print(f"❌ TTS 생성 실패: {result_path}")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n⚠️  사용자에 의해 중단되었습니다.")
        sys.exit(130)
    
    except Exception as e:
        print(f"❌ 예상치 못한 오류 발생: {e}")
        if not args.quiet:
            import traceback
            print("\n🔍 상세 오류 정보:")
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
