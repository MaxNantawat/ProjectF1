import streamlit as st
import pandas as pd
import plotly.express as px
import json

st.title("🏎️ F1 Telemetry Upload & Comparison Dashboard")
st.write("อัปโหลดไฟล์ JSON จากคอมพิวเตอร์ของคุณเพื่อนำมาพล็อตกราฟเปรียบเทียบได้ทันที")

# --- ส่วนของการสร้างปุ่มอัปโหลดไฟล์จากเครื่อง ---
st.subheader("📂 อัปโหลดไฟล์ข้อมูล (Upload JSON Files)")

# 1. ปุ่มสำหรับอัปโหลดข้อมูลนักแข่งคนที่ 1
file1 = st.file_uploader("เลือกไฟล์ข้อมูลนักแข่งคนแรก (เช่น f1_data.json)", type=['json'])

# 2. ปุ่มสำหรับอัปโหลดข้อมูลนักแข่งคนที่ 2 (ตัวเลือกเสริม)
file2 = st.file_uploader("เลือกไฟล์ข้อมูลนักแข่งคนที่สอง เพื่อนำมาเปรียบเทียบ (ถ้ามี)", type=['json'])

# ตรวจสอบว่ามีการอัปโหลดไฟล์แรกหรือยังก่อนที่จะเริ่มทำงาน
if file1 is not None:
    try:
        # โหลดและแปลงข้อมูลไฟล์ที่ 1 จากเครื่อง
        data1 = json.load(file1)
        df1 = pd.DataFrame(data1['tel'])
        df1['Driver'] = 'Driver 1' # ตั้งชื่อเล่นให้นักแข่งคนแรก

        # ตรวจสอบและโหลดไฟล์ที่ 2 จากเครื่อง (ถ้ามีการอัปโหลด)
        if file2 is not None:
            data2 = json.load(file2)
            df2 = pd.DataFrame(data2['tel'])
            df2['Driver'] = 'Driver 2' # ตั้งชื่อเล่นให้นักแข่งคนที่สอง
            
            # รวมตารางข้อมูลเข้าด้วยกัน
            df_combined = pd.concat([df1, df2], ignore_index=True)
            multi_driver = True
        else:
            df_combined = df1
            multi_driver = False

        # --- ส่วนการเลือกเมนูและพล็อตกราฟ ---
        st.markdown("---")
        metrics = st.selectbox(
            'เลือกข้อมูล Telemetry ที่ต้องการแสดงผล:',
            ['speed', 'rpm', 'throttle', 'gear']
        )

        # 3. พล็อตกราฟเส้นเปรียบเทียบข้อมูล
        fig_telemetry = px.line(
            df_combined, 
            x='distance', 
            y=metrics, 
            color='Driver' if multi_driver else None,
            title=f'กราฟแสดงผล {metrics.upper()} บนระยะทางสนาม (Distance)',
            labels={'distance': 'ระยะทางในสนาม (เมตร)', metrics: metrics.upper(), 'Driver': 'นักแข่ง'}
        )
        fig_telemetry.update_layout(hovermode="x unified")
        st.plotly_chart(fig_telemetry)

        # 4. พล็อตกราฟเส้นทางวิ่ง (Racing Line) 
        st.markdown("---")
        st.subheader("📍 แผนที่สนามแข่ง (Track Map)")
        
        fig_track = px.scatter(
            df_combined, 
            x='x', 
            y='y', 
            color='Driver' if multi_driver else 'speed',
            title='Track Map & Racing Line',
            labels={'x': 'พิกัด X', 'y': 'พิกัด Y', 'Driver': 'นักแข่ง', 'speed': 'ความเร็ว (km/h)'}
        )
        fig_track.update_yaxes(scaleanchor="x", scaleratio=1)
        st.plotly_chart(fig_track)

    except Exception as e:
        st.error(f"❌ ไฟล์ข้อมูลไม่ถูกต้อง หรือโครงสร้างภายในไฟล์ไม่ตรงตามรูปแบบ: {e}")

else:
    st.info("💡 กรุณาอัปโหลดไฟล์ข้อมูลอย่างน้อย 1 ไฟล์ เพื่อเริ่มต้นแสดงกราฟ Telemetry ครับ")
