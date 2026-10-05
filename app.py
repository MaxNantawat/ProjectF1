import streamlit as st
import pandas as pd
import plotly.express as px
import json

# 1. ตั้งชื่อหัวข้อแดชบอร์ด
st.title("🏎️ F1 Telemetry Dashboard (Max Verstappen)")
st.write("กราฟวิเคราะห์ข้อมูล Telemetry จากไฟล์ของคุณ")

# 2. จำลองการอ่านข้อมูล (ให้เปลี่ยนเป็นวิธีโหลดไฟล์จริงด้านล่าง)
# สมมติว่าคุณเซฟไฟล์ตัวอย่างนั้นไว้ในชื่อ 'f1_data.json' ในโฟลเดอร์เดียวกัน
try:
    with open('f1_data.json', 'r') as f:
        raw_data = json.load(f)
    
    # ดึงข้อมูลย่อยในคีย์ "tel" ออกมาแปลงเป็นตาราง (DataFrame)
    df = pd.DataFrame(raw_data['tel'])
    
    # 3. สร้างเมนูให้เลือกดูตัวแปรที่สนใจ
    option = st.selectbox(
        'เลือกข้อมูลที่ต้องการแสดงในกราฟ Y-Axis:',
        ('speed', 'rpm', 'throttle', 'gear')
    )

    # 4. สร้างกราฟเส้นโดยใช้ Plotly (แกน X เป็นเวลา, แกน Y เป็นข้อมูลที่เลือก)
    fig = px.line(
        df, 
        x='time', 
        y=option, 
        title=f'กราฟแสดง {option.upper()} เปรียบเทียบกับเวลา (Time)',
        labels={'time': 'เวลา (วินาที)', option: option.upper()}
    )
    
    # ปรับแต่งกราฟให้สวยงามขึ้น
    fig.update_layout(hovermode="x unified")
    
    # 5. แสดงกราฟบนหน้าเว็บ
    st.plotly_chart(fig)
    
    # แสดงตารางข้อมูลดิบด้านล่างกราฟให้ผู้ใช้ดูได้ด้วย
    st.subheader("📋 ตารางข้อมูลดิบ (Data Table)")
    st.dataframe(df)

except FileNotFoundError:
    st.error("❌ ไม่พบไฟล์ f1_data.json กรุณาตรวจสอบว่าชื่อไฟล์ถูกต้องและอยู่ในโฟลเดอร์เดียวกันกับโค้ด")
