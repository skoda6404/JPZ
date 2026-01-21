@echo off
echo Zkousim inicializovat pres 'py' launcher...
py -m pip install -r requirements.txt
py -m streamlit run app.py
if %errorlevel% neq 0 (
    echo Chyba pri spusteni pres 'py'. Zkousim 'python'...
    python -m pip install -r requirements.txt
    python -m streamlit run app.py
)
echo .
echo Pokud se nic nestalo, zrejme nemate nainstalovany Python.
pause
