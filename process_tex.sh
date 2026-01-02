#!/bin/bash
# CiteAgent File Mode - 서버에서 .tex 파일 처리
# SSH 서버에서 브라우저 없이 사용하는 스크립트

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 사용법 체크
if [ -z "$1" ]; then
    echo -e "${YELLOW}Usage:${NC} $0 <file.tex> [output_name]"
    echo ""
    echo "Examples:"
    echo "  $0 main.tex"
    echo "  $0 main.tex output"
    echo ""
    exit 1
fi

INPUT_FILE="$1"
OUTPUT_NAME="${2:-$(basename ${INPUT_FILE%.tex})_cited}"

# 파일 존재 확인
if [ ! -f "$INPUT_FILE" ]; then
    echo -e "${YELLOW}Error:${NC} File not found: $INPUT_FILE"
    exit 1
fi

# CiteAgent 디렉토리로 이동
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 가상환경 확인
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# 가상환경 활성화
source venv/bin/activate

# 의존성 확인
if ! python -c "import openai" 2>/dev/null; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install -q -r requirements.txt
fi

# 처리 시작
echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}  CiteAgent - File Mode${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""
echo -e "Input:  ${GREEN}$INPUT_FILE${NC}"
echo -e "Output: ${GREEN}${OUTPUT_NAME}.tex${NC}"
echo ""

# CiteAgent 실행
python main.py --file "$INPUT_FILE"

# 결과 파일 이름 변경
ORIGINAL_OUTPUT="${INPUT_FILE%.tex}_cited.tex"
ORIGINAL_BIB="${INPUT_FILE%.tex}_cited.bib"

if [ "$OUTPUT_NAME" != "$(basename ${INPUT_FILE%.tex})_cited" ]; then
    mv "$ORIGINAL_OUTPUT" "${OUTPUT_NAME}.tex" 2>/dev/null || true
    mv "$ORIGINAL_BIB" "${OUTPUT_NAME}.bib" 2>/dev/null || true
fi

# 결과 표시
echo ""
echo -e "${GREEN}✅ Processing complete!${NC}"
echo ""
echo -e "Output files:"
echo -e "  📄 ${GREEN}${OUTPUT_NAME}.tex${NC} - LaTeX with citations"
echo -e "  📚 ${GREEN}${OUTPUT_NAME}.bib${NC} - BibTeX entries"
echo ""

# 다운로드 명령어 표시
if [ -n "$SSH_CONNECTION" ]; then
    HOSTNAME=$(hostname)
    USERNAME=$(whoami)
    FILEPATH="$(pwd)/${OUTPUT_NAME}"

    echo -e "${BLUE}Download to your local machine:${NC}"
    echo -e "  scp ${USERNAME}@${HOSTNAME}:${FILEPATH}.tex ."
    echo -e "  scp ${USERNAME}@${HOSTNAME}:${FILEPATH}.bib ."
    echo ""
fi

echo -e "${BLUE}Upload to Overleaf:${NC}"
echo "  1. Copy content of ${OUTPUT_NAME}.tex to your Overleaf main.tex"
echo "  2. Copy content of ${OUTPUT_NAME}.bib to your Overleaf references.bib"
echo ""
