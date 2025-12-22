```bash
git clone https://github.com/Carbon-Scan/Model-AI.git
cd Model-AI
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
pip install rapidfuzz
pip install python-dotenv
pip install pymysql
uvicorn app.main:app --reload

```
