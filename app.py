import streamlit as st
import pandas as pd
import plotly.express as px
import json

st.title("🏎️ F1 Telemetry Comparison Dashboard")
st.subheader("เปรียบเทียบข้อมูล Telemetry ระหว่างนักแข่งสองคน")

try:
    # 1. โหลดข้อมูลชุดที่ 1 (ตัวอย่าง: Max Verstappen)
    with open('f1_data.json', 'r') as f:
        data1 = json.load(f)
    df1 = pd.DataFrame(data1['tel'])
    df1['Driver'] = 'VER' # เพิ่มคอลัมน์ระบุชื่อนักแข่งคนแรก

    # 2. โหลดข้อมูลชุดที่ 2 (ตัวอย่าง: Lewis Hamilton)
    # หากยังไม่ได้อัปโหลดไฟล์ที่ 2 โค้ดจะข้ามไปทำงานส่วนถัดไปไม่ให้เว็บพัง
    try:
        with open('f1_data_2.json', 'r') as f:
            data2 = json.load(f)
        df2 = pd.DataFrame(data2['tel'])
        df2['Driver'] = 'HAM' # เพิ่มคอลัมน์ระบุชื่อนักแข่งคนที่สอง
        
        # นำตารางของนักแข่งทั้งสองคนมาต่อรวมกันเป็นตารางเดียว
        df_combined = pd.concat([df1, df2], ignore_index=True)
        multi_driver = True
    except FileNotFoundError:
        df_combined = df1
        multi_driver = False
        st.warning("⚠️ โหลดข้อมูลได้เฉพาะคนแรก เนื่องจากยังไม่พบไฟล์ f1_data_2.json ใน GitHub")

    # 3. เมนูเลือกตัวแปรที่จะดูบนกราฟ
    metrics = st.selectbox(
        'เลือกข้อมูล Telemetry ที่ต้องการเปรียบเทียบ:',
        ['speed', 'rpm', 'throttle', 'gear']
    )

    # 4. สร้างกราฟเส้นเปรียบเทียบ (ถ้ามี 2 คน จะมีเส้นขึ้นมา 2 สีสลับกันให้เห็นชัดเจน)
    # เราใช้สีจากคอลัมน์ 'Driver' ในการแยกเส้น
    fig_telemetry = px.line(
        df_combined, 
        x='distance', 
        y=metrics, 
        color='Driver' if multi_driver else None,
        title=f'กราฟเปรียบเทียบ {metrics.upper()} บนระยะทางสนาม (Distance)',
        labels={'distance': 'ระยะทางในสนาม (เมตร)', metrics: metrics.upper(), 'Driver': 'นักแข่ง'}
    )
    fig_telemetry.update_layout(hovermode="x unified")
    st.plotly_chart(fig_telemetry)

    # 5. พลอตแผนที่สนามแข่ง ( Racing Line ) เปรียบเทียบตำแหน่ง
    if multi_driver:
        st.markdown("---")
        st.subheader("📍 เปรียบเทียบแผนที่สนามแข่ง (Track Map)")
        
        fig_track = px.scatter(
            df_combined, 
            x='x', 
            y='y', 
            color='Driver',
            title='เปรียบเทียบ Racing Line เส้นทางการวิ่งของนักแข่งทั้งสองคน',
            labels={'x': 'พิกัด X', 'y': 'พิกัด Y', 'Driver': 'นักแข่ง'}
        )
        fig_track.update_yaxes(scaleanchor="x", scaleratio=1)
        st.plotly_chart(fig_track)

except FileNotFoundError:
    st.error("❌ ไม่พบไฟล์ข้อมูลหลัก f1_data.json กรุณาตรวจสอบชื่อไฟล์บน GitHub")
