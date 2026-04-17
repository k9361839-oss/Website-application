import os
import subprocess
import shutil
from flask import Flask, request, send_file

app = Flask(__name__)

# דף הבית של האתר (HTML)
HTML_PAGE = """
<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
    <meta charset="UTF-8">
    <title>מפרק APK לקוד מקור</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f0f2f5; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .card { background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); text-align: center; width: 400px; }
        h1 { color: #1a73e8; font-size: 24px; }
        p { color: #5f6368; }
        input[type="file"] { margin: 20px 0; border: 1px dashed #ccc; padding: 20px; width: 80%; border-radius: 8px; cursor: pointer; }
        button { background-color: #1a73e8; color: white; border: none; padding: 12px 24px; border-radius: 6px; cursor: pointer; font-size: 16px; transition: background 0.3s; }
        button:hover { background-color: #1557b0; }
        .footer { margin-top: 20px; font-size: 12px; color: #9aa0a6; }
    </style>
</head>
<body>
    <div class="card">
        <h1>מחלץ קוד מ-APK</h1>
        <p>העלה קובץ אפליקציה וקבל ZIP עם כל הקוד</p>
        <form action="/convert" method="post" enctype="multipart/form-data">
            <input type="file" name="apk_file" accept=".apk" required><br>
            <button type="submit">פרק והורד ZIP</button>
        </form>
        <div class="footer">הפירוק עשוי לקחת מספר דקות לקבצים גדולים</div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return HTML_PAGE

@app.route('/convert', methods=['POST'])
def convert():
    if 'apk_file' not in request.files:
        return "שגיאה: לא נבחר קובץ", 400
    
    file = request.files['apk_file']
    if file.filename == '':
        return "שגיאה: שם קובץ ריק", 400

    # הגדרת נתיבים
    base_name = "extracted_source"
    apk_temp = "temp_app.apk"
    out_dir = "./output_code"
    zip_name = "source_code" # הקובץ שיווצר יהיה source_code.zip

    try:
        # שמירה זמנית
        file.save(apk_temp)
        
        # הרצת JADX לפירוק (מותקן בשרת דרך ה-Dockerfile)
        subprocess.run(['jadx', '-d', out_dir, apk_temp], check=True)
        
        # יצירת ZIP מהתוצאה
        shutil.make_archive(zip_name, 'zip', out_dir)
        
        # ניקוי תיקיות זמניות
        os.remove(apk_temp)
        shutil.rmtree(out_dir)
        
        return send_file(f"{zip_name}.zip", as_attachment=True)

    except Exception as e:
        return f"אירעה שגיאה בשרת: {str(e)}", 500

if __name__ == '__main__':
    # Render דורש שהפורט יהיה דינמי או 10000, 0.0.0.0 מאפשר גישה חיצונית
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)