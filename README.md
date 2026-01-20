attendance_app/
│
├── app.py
├── database.py
├── requirements.txt
└── attendance.db (auto-created when app runs)

## Installation

The project dependencies are managed using a requirements.txt file. All required Python libraries were installed using the pip package manager

```
python3.11 --version
python3.11 -m venv venv
source venv/bin/activate
python --version

pip install --upgrade pip

brew install cmake
brew install boost

pip install -r requirements.txt

streamlit run app.py
or
python -m streamlit run app.py
```

## Default Admin Login Credentials

Username: admin
Password: admin123
