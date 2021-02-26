# UpdateEra README

## 한국어 사용자용

### 개요

**UpdateEra**는 *.srs* 또는 *.simplesrs* 형식으로 생성된 데이터베이스를 기반으로, *.conf* 파일로 설정한 방식으로 구동되는 파일 내 텍스트 일괄 변환기입니다.

### 사용법

#### 실행 프로그램 빌드

1. `UpdateEra\build.cmd` 내 `D:\dev\ActivePython-2.7.2.5-win32-x86\python.exe -O setup.py py2exe` 부분에서 *python* 경로를 내 컴퓨터에 설치된 파이썬 경로로 바꿉니다.
2. `UpdateEra\build.cmd`를 실행합니다. 만약 제대로 작동하지 않거나 글자가 깨진다면 *EUC-KR*, *CP949* 등의 한국어 인코딩으로 다시 시도해주세요.

#### 프로그램 사용

1. *.srs* 또는 *.simplesrs* 확장자로 양식에 맞게 작성된 데이터베이스 파일을 준비합니다.
2. *.conf* 파일로 설정을 지정합니다.
3. *.conf* 파일을 `run.cmd`에 드래그해 실행합니다.

### 유의사항

본 프로그램은 제가 만든 프로그램이 아닌, [*dcinside*](https://gall.dcinside.com/mgallery/board/view/?id=textgame&no=42247) 내 익명의 이용자가 올린 소스 코드를 받아 *github*에 올린 것입니다.  
당시 해당 글의 작성자분은 자신이 어디서 가져온 것인지 모르는 라이브러리파일을 제외하고 나머지 파일들은 퍼블릭 도메인이라 명시하셨습니다.  
따라서 본 코드를 웹상에 공유함으로써 집단지성을 활용한 프로그램의 업그레이드와 실사용자의 편리한 접근을 보장하기 위해 본 코드를 *github*에 올리게 되었습니다.  
만약 본 프로그램 내에서 사용된 외부 모듈(라이브러리)의 출처를 아시는 분이시라면 이슈 트래커로 제보 부탁드립니다.

### 프로그램 정보

* 원본에서 사용된 프로그래밍 언어 : **Python 2** *(2.7.2.5)*
* 원본 코드 내 기본 인코딩 : **CP949** *(EUC-KR)*
* 현 코드 내 인코딩 : **UTF-8** (일부 배치파일 제외)

## For English User

### Introduction

**UpdateEra** is the program uses *.srs* or *.simplesrs* format file for database, *.conf* format file for settings to convert whole text file's context.

### Notice

This program is from *dcinside*, S.Korea's anonymous community site.  
I'm just uploader of this program, not the original programmar.  
The author who posted this article on [*dcinside*](https://gall.dcinside.com/mgallery/board/view/?id=textgame&no=42247) said this program is in the **public domain** except some of external module that don't know where they come from.  
I, the admin of this repository, upload this program on *github* to develop the program and share it to many people.  
If you know the source of external module, please let us know on the issue tracker.

### Program Information

* Original Programming Language : **Python 2** *(2.7.2.5)*
* Original In-Code Encoding : **CP949** *(EUC-KR)*
* Current In-Code Encoding : **UTF-8** except some batch files
