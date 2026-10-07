@echo off
title AI Poster Studio
echo ====================================================
echo           Iniciando AI Poster Studio
echo ====================================================
cd /d "%~dp0"
streamlit run app.py
pause
