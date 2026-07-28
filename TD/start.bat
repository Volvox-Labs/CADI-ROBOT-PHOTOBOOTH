rem turn off echo
@echo off


IF EXIST ".env" (
  echo ".env exists"
) ELSE (
  COPY .env.sample .env
)

:: Copy missing env variables from .env.sample to .env, skipping comments
FOR /F "usebackq tokens=1* delims==" %%i IN (.env.sample) DO (
  IF NOT "%%i"=="" (
    IF NOT "%%i:~0,1"=="#" (
      FINDSTR /R /C:"^%%i=" .env >nul || ECHO %%i=%%j>>.env
    )
  )
)

:: TouchDesigner build numbers
set TOUCHVERSION=2025.32280

:: set our project file target
set TOEFILE="cadi-robot-photobooth26.toe"

:: set the rest of our paths for executables
set TOUCHDIR=%PROGRAMFILES%\Derivative\TouchDesigner.
set TOUCHEXE=\bin\TouchDesigner.exe

:: combine our elements so we have a single path to our TouchDesigner.exe
set TOUCHPATH="%TOUCHDIR%%TOUCHVERSION%%TOUCHEXE%"

IF EXIST %TOUCHPATH% (
  REM Do one thing
) ELSE (
  set TOUCHDIR=%PROGRAMFILES%\Derivative\TouchDesigner
  set TOUCHPATH="%TOUCHDIR%%TOUCHEXE%"
)

@REM :: BEGIN ENV VARIABLES 
@REM set MODE=dev
@REM set assets_path=assets\

@REM set status_view_monitor_index=0
@REM :: Monitor index should be set based on which touch monitor you want to use
@REM set monitor_index=1
@REM set blackmagic_camera_index=0
@REM set takeaways_render_dir=C:\Users\vvox\Documents\GitHub\CADI-USOPEN-PHOTOBOOTH\TD\assets\takeaway\
@REM set dante_channels=1:Dante_tx_1,2:Dante_tx_2
@REM set photobooth_id=1

:: start our project file with the target TD installation
start "" %TOUCHPATH% %TOEFILE%
