from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

# Data Storage: List of dictionaries (จำลองฐานข้อมูล)
# ในการใช้งานจริง ควรใช้ SQLite หรือ Database อื่นๆ
health_records = []

# ฟังก์ชันคำนวณ BMI
def calculate_bmi(weight_kg, height_m):
    """Calculates BMI (Body Mass Index). BMI = kg / m^2"""
    if height_m <= 0:
        return 0
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 2)

# ฟังก์ชันจัดหมวดหมู่ BMI (Simple Business Logic)
def get_bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 25.0:
        return "Healthy Weight"
    elif 25.0 <= bmi < 30.0:
        return "Overweight"
    else:
        return "Obesity"

@app.route('/', methods=['GET', 'POST'])
def index():
    error_message = None
    today_date = datetime.now().strftime('%Y-%m-%d')
    
    if request.method == 'POST':
        # --- 1. Input Retrieval & Initial Parsing ---
        try:
            # รับค่าจากฟอร์ม (cm/kg)
            height_cm = float(request.form['height_cm'])
            weight_kg = float(request.form['weight_kg'])
            date_str = request.form.get('date', today_date)
            
            # ตรวจสอบรูปแบบวันที่ (Optional: ใน HTML input type="date" จัดการให้อยู่แล้ว)
            datetime.strptime(date_str, '%Y-%m-%d') 
        except ValueError:
            error_message = "กรุณาป้อนข้อมูลน้ำหนักและส่วนสูงเป็นตัวเลขที่ถูกต้อง และตรวจสอบรูปแบบวันที่"
            return render_template('index.html', records=health_records, error=error_message, today=today_date, chart_data={'dates': [], 'bmis': []})
        
        # --- 2. Input Validation (Range Check) ---
        if not (20.0 <= weight_kg <= 300.0):
            error_message = "น้ำหนักต้องอยู่ระหว่าง 20 ถึง 300 กิโลกรัม"
        elif not (50.0 <= height_cm <= 250.0):
            error_message = "ส่วนสูงต้องอยู่ระหว่าง 50 ถึง 250 เซนติเมตร"
        
        if error_message:
            return render_template('index.html', records=health_records, error=error_message, today=today_date, chart_data={'dates': [], 'bmis': []})

        # --- 3. Business Logic & Data Storage ---
        height_m = height_cm / 100.0  # แปลง cm เป็น meter
        bmi = calculate_bmi(weight_kg, height_m)
        category = get_bmi_category(bmi)

        new_record = {
            'date': date_str,
            'height_m': height_m,
            'weight_kg': weight_kg,
            'bmi': bmi,
            'category': category
        }
        health_records.append(new_record)
        
        # เรียงลำดับตามวันที่ (ล่าสุดอยู่บนสุด)
        health_records.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'), reverse=True)

        # ใช้ POST-Redirect-GET Pattern เพื่อป้องกันการซ้ำซ้อนของข้อมูล
        return redirect(url_for('index')) 

    # --- 4. Basic Reporting (Data Preparation) ---
    # เตรียมข้อมูลสำหรับกราฟเส้น (Chart.js)
    # ต้องเรียงลำดับจากเก่าไปใหม่สำหรับกราฟ
    sorted_records = sorted(health_records, key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'), reverse=False)
    
    chart_data = {
        'dates': [record['date'] for record in sorted_records],
        'bmis': [record['bmi'] for record in sorted_records]
    }
    
    return render_template(
        'index.html', 
        records=health_records, 
        today=today_date, 
        chart_data=chart_data
    )

if __name__ == '__main__':
    # รันในโหมด debug
    app.run(debug=True)