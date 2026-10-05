import streamlit as st
import pandas as pd
import plotly.express as px
import json

# --- 1. ตั้งค่าธีมและหน้าเว็บให้เป็นโทนดุดันสไตล์ 1RaceClub ---
st.set_page_config(layout="wide")

# ใส่ CSS ตกแต่งให้พื้นหลังมืดและตัวหนังสือสีขาวแดงสะดุดตา
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1 { color: #FF1801 !important; font-family: 'Arial Black', sans-serif; }
    h3 { color: #ffffff !important; }
    div.stActionButton > button { background-color: #FF1801; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏎️ 1RaceClub Style - F1 Telemetry Studio")
st.write("ระบบวิเคราะห์และเปรียบเทียบข้อมูล Telemetry ยินดีต้อนรับชาว 1RaceClub ทุกคนครับ!")

# --- 2. ส่วนอินพุตและตั้งชื่อนักแข่งแบบ Dynamic ---
st.subheader("📂 คลังข้อมูลและรายชื่อนักแข่ง (Drivers Setup)")

col_input1, col_input2 = st.columns(2)

with col_input1:
    driver1_name = st.text_input("พิมพ์ชื่อนักแข่งคนที่ 1:", "Max Verstappen")
    file1 = st.file_uploader(f"อัปโหลดไฟล์ JSON ของ {driver1_name}", type=['json'])

with col_input2:
    driver2_name = st.text_input("พิมพ์ชื่อนักแข่งคนที่ 2:", "Lewis Hamilton")
    file2 = st.file_uploader(f"อัปโหลดไฟล์ JSON ของ {driver2_name} (ตัวเลือกเปรียบเทียบ)", type=['json'])

# ตรวจสอบการอัปโหลดไฟล์แรก
if file1 is not None:
    try:
        # โหลดข้อมูลนักแข่งคนแรก
        data1 = json.load(file1)
        df1 = pd.DataFrame(data1['tel'])
        df1['Driver'] = driver1_name

        # ตรวจสอบและโหลดข้อมูลนักแข่งคนที่สอง
        if file2 is not None:
            data2 = json.load(file2)
            df2 = pd.DataFrame(data2['tel'])
            df2['Driver'] = driver2_name
            
            df_combined = pd.concat([df1, df2], ignore_index=True)
            multi_driver = True
        else:
            df_combined = df1
            multi_driver = False

        # --- 3. ส่วนควบคุมกราฟและตัวแปร ---
        st.markdown("---")
        
        # เมนูเลือกตัวแปร Telemetry
        metrics = st.selectbox(
            'เลือกข้อมูล Telemetry ที่ต้องการดูบนกราฟ:',
            ['speed', 'rpm', 'throttle', 'gear']
        )

        # 4. พล็อตกราฟ Telemetry (ใช้ธีมมืดและสีสันสะดุดตา)
        # กำหนดสีเฉพาะตัว: ให้คนแรกเป็นสีแดงสด (สไตล์ Red Bull) คนที่สองเป็นสีเหลืองนีออน หรือตามชอบ
        color_map = {driver1_name: '#FF1801', driver2_name: '#00FFFF'}
        
        fig_telemetry = px.line(
            df_combined, 
            x='distance', 
            y=metrics, 
            color='Driver' if multi_driver else None,
            color_discrete_map=color_map if multi_driver else None,
            title=f'📊 กราฟวิเคราะห์ {metrics.upper()} เปรียบเทียบบนระยะทางสนาม',
            template="plotly_dark", # เปิดใช้งานธีมมืดของ Plotly 
            labels={'distance': 'ระยะทางในสนาม (เมตร)', metrics: metrics.upper(), 'Driver': 'นักแข่ง'}
        )
        
        # ปรับแต่งเส้นและจุดชี้บนกราฟให้คมชัดสไตล์เกมแข่งรถ
        fig_telemetry.update_layout(hovermode="x unified", plot_bgcolor='#161a24', paper_bgcolor='#0e1117')
        fig_telemetry.update_traces(line=dict(width=3))
        st.plotly_chart(fig_telemetry, use_container_width=True)

        # 5. พล็อตกราฟ Track Map และ Racing Line แยกสัดส่วนหน้าจอ
        st.markdown("---")
        col_track, col_table = st.columns([2, 1]) # แยกฝั่งซ้ายเป็นแผนที่ ฝั่งขวาเป็นตารางตัวเลข

        with col_track:
            st.subheader("📍 แผนที่สนามและ Racing Line")
            
            fig_track = px.scatter(
                df_combined, 
                x='x', 
                y='y', 
                color='Driver' if multi_driver else 'speed',
                color_continuous_scale='turbo' if not multi_driver else None,
                template="plotly_dark",
                labels={'x': 'พิกัด X', 'y': 'พิกัด Y', 'Driver': 'นักแข่ง', 'speed': 'ความเร็ว (km/h)'}
            )
            fig_track.update_yaxes(scaleanchor="x", scaleratio=1)
            fig_track.update_layout(plot_bgcolor='#161a24', paper_bgcolor='#0e1117')
            st.plotly_chart(fig_track, use_container_width=True)
            
        with col_table:
            st.subheader("📋 สรุปข้อมูลดิบ")
            st.write("ตารางแสดงค่า Telemetry ในแต่ละเซกเตอร์")
            st.dataframe(df_combined[['time', 'distance', metrics, 'Driver']].head(50), height=400)

    except Exception as e:
        st.error(f"❌ โครงสร้างไฟล์ JSON ไม่ถูกต้อง หรือเกิดข้อผิดพลาด: {e}")

else:
    st.info("💡 ชาว 1RaceClub กรุณาอัปโหลดไฟล์ JSON ข้อมูลนักแข่งในกล่องด้านบนเพื่อเริ่มต้นระบบครับ")
