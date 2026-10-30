# AdaptLearn – AI-Powered Personalized Learning System

Flask + MySQL + scikit-learn (optional TensorFlow CPU) + OpenAI-compatible LLM (free Groq/Gemini) + React.

## Quick start
```bash
# 1) database (MySQL) – or skip: SQLite is used automatically if DATABASE_URL is empty
mysql -u root -p < database/schema.sql

# 2) backend
cd backend
python -m venv venv && source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                   # Windows: copy .env.example .env
flask --app run seed                                   # demo data + trains the model
python run.py                                          # http://localhost:5000

# 3) frontend (new terminal)
cd frontend && npm install && npm run dev              # http://localhost:5173
```
Demo logins (password `Password123`): student@demo.com, teacher@demo.com, admin@demo.com
