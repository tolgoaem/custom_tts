[윈도우 아나콘다 환경 세팅 내역]

1. 새로운 환경 만들기

- conda 업데이트
conda update -n base conda
conda update --all
python -m pip install --upgrade pip

- 환경 생성 후 실행
conda create -n openvoice python=3.9
conda activate openvoice

- cuda 관련 설정(PC에 따라 다를 수 있음)
사용자 PC 환경: 윈도우11, RTX3060, 241010 기준 모든 드라이버 업데이트 최신 상태
conda install -c conda-forge cudatoolkit=11.8 cudnn=8.9
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia

- 아래 python 스크립트를 통해 cuda가 torch에서 동작하는지 확인
python
import torch
torch.cuda.is_available()
  : True가 출력되어야 함. False 출력시 다시 True가 나오도록 재 설정 하거나, GPU 사용을 포기하고 CPU로 구동해도 괜찮다면 계속 진행.

- openvoice 관련 환경 설정
git clone https://github.com/myshell-ai/OpenVoice.git
cd OpenVoice
pip install -r requirements.txt

- MELO TTS 설치
pip install git+https://github.com/myshell-ai/MeloTTS.git
python -m unidic download

- 설치 후 최종 확인
python
import torch; torch.cuda.is_available()
  : True 출력되는 것 확인