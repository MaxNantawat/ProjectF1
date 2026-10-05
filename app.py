import streamlit as st
import pandas as pd
import plotly.express as px
import json

st.set_page_config(layout="wide")

# ปรับธีมดุดันสไตล์ 1RaceClub เหมือนเดิม
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1 { color: #FF1801 !important; font-family: 'Arial Black', sans-serif; }
    h3 { color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏎️ 1RaceClub Studio: Telemetry Analyzer Pro")

# --- ระบบเก็บความจำระยะทางที่ถูกคลิก (Session State) ---
if 'selected_distance' not in st.session_state:
    st.session_state.selected_distance = None

# อัปโหลดไฟล์จากเครื่องคอมพิวเตอร์
st.subheader("📂 นำเข้าข้อมูลรอบสนาม (Data Input)")
driver_name = st.text_input("ชื่อนักแข่ง:", "Max Verstappen")
file1 = st.file_uploader(f"อัปโหลดไฟล์ JSON ของ {driver_name}", type=['json'])

if file1 is not None:
    try:
        data1 = json.load(file1)
        df = pd.DataFrame(data1['tel'])
        df['Driver'] = driver_name

        # --- ส่วนควบคุมแถบสไลด์ขยายแกน X ---
        st.markdown("---")
        st.subheader("🔍 ควบคุมระยะช่วงความกว้างของแกน X (Zoom Control)")
        
        max_dist = int(df['distance'].max())
        
        # กล่องสไลเดอร์ให้ผู้ใช้เลือกความกว้าง (Window Size) ในการขยายดู เช่น จะดูทีละ 200 เมตร หรือ 500 เมตร
        zoom_window = st.slider("เลือกความกว้างของระยะทางที่จะขยายดู (เมตร):", min_value=100, max_value=2000, value=300, step=50)

        # ----------------------------------------------------------------------
        # กราฟที่ 1: แผนที่สนามแข่ง (Track Map) - วางไว้ด้านบนเพื่อให้ผู้ใช้คลิกก่อน
        # ----------------------------------------------------------------------
        st.subheader("📍 1. คลิกเลือกจุดบนแผนที่สนาม (Track Map)")
        st.write("เมาส์ชี้ดูข้อมูลพิกัด หรือคลิกจุดใดก็ได้บนสนาม เส้นกราฟด่านล่างจะซูมไปที่ระยะตรงนั้นให้ทันที")

        fig_track = px.scatter(
            df, 
            x='x', 
            y='y', 
            color='speed',
            hover_data=['distance', 'speed'], # แสดงข้อมูลระยะทางเวลาเอาเมาส์ชี้
            color_continuous_scale='turbo',
            template="plotly_dark",
            title='จิ้มเลือกโค้งที่สนใจบนแทร็กสนาม'
        )
        fig_track.update_yaxes(scaleanchor="x", scaleratio=1)
        fig_track.update_layout(clickmode='event+select', plot_bgcolor='#161a24', paper_bgcolor='#0e1117')
        
        # ตรวจสอบว่าผู้ใช้คลิกจุดไหนบนกราฟ Map หรือไม่ (ฟังก์ชันพิเศษของ Streamlit ในเวอร์ชันปัจจุบัน)
        selected_points = st.plotly_chart(fig_track, use_container_width=True, on_select="rerun")

        # ถ้าระบบตรวจจับได้ว่าผู้ใช้คลิกเลือกจุดบนจุด Scatter
        if selected_points and "points" in selected_points and len(selected_points["points"]) > 0:
            # ดึงข้อมูลระยะทาง (distance) ของจุดที่โดนคลิกออกมาเก็บไว้
            point_data = selected_points["points"][0]
            # ในกรณีนี้ดึงค่าที่แฝงอยู่ในตาราง (ตรวจสอบโครงสร้างจาก hover_data)
            st.session_state.selected_distance = df.iloc[point_data["point_index"]]['distance']

        # ----------------------------------------------------------------------
        # กราฟที่ 2: กราฟความเร็วรถ (Telemetry Profile) - ขยายแกน X ตามตำแหน่งที่คลิก
        # ----------------------------------------------------------------------
        st.markdown("---")
        st.subheader(f"📊 2. กราฟวิเคราะห์ความเร็ว (Speed Telemetry) - ซูมเฉพาะช่วง")

        # คำนวณช่วงการซูมของแกน X อัตโนมัติ
        if st.session_state.selected_distance is not None:
            current_dist = st.session_state.selected_distance
            st.success(f"🎯 กำลังโฟกัสพิกัดสนามแข่งที่ระยะทางสะสม: {current_dist:,.2f} เมตร")
            
            # กำหนดขอบเขตแกน X บนกราฟ (ซูมเข้าไปรอบ ๆ จุดที่คลิก)
            xmin = max(0, current_dist - (zoom_window / 2))
            xmax = min(max_dist, current_dist + (zoom_window / 2))
        else:
            st.info("💡 แนะนำ: ลองคลิกจุดบนแผนที่ด้านบนดูครับ! ตอนนี้ระบบกำลังแสดงภาพรวมทั้งรอบสนาม")
            xmin = 0
            xmax = max_dist

        # พล็อตกราฟแกน Y เป็นความเร็ว (Speed) เสมอตามที่คุณต้องการ
        fig_telemetry = px.line(
            df, 
            x='distance', 
            y='speed',
            template="plotly_dark",
            title=f'ความเร็วของรถย่อยเฉพาะเซกเตอร์ในช่วงระยะ {xmin:,.0f} ม. ถึง {xmax:,.0f} ม.',
            labels={'distance': 'ระยะทางในสนาม (เมตร)', 'speed': 'ความเร็ว (km/h)'}
        )
        
        # สั่งกำหนดขอบเขตแกน X (ขยายสเกลตามตัวแปร xmin, xmax ที่เราคำนวณไว้)
        fig_telemetry.update_xaxes(range=[xmin, xmax])
        
        # ตกแต่งสไตล์ 1RaceClub เส้นสีแดงหนา คมชัด
        fig_telemetry.update_traces(line=dict(color='#FF1801', width=3))
        fig_telemetry.update_layout(hovermode="x unified", plot_bgcolor='#161a24', paper_bgcolor='#0e1117')
        
        # เพิ่มเส้นแนวตั้งสีขาวมาร์กจุดที่ผู้ใช้เลือกคลิกไว้ เพื่อให้หาได้ง่าย
        if st.session_state.selected_distance is not None:
            fig_telemetry.add_vline(x=st.session_state.selected_distance, line_dash="dash", line_color="white")

        st.plotly_chart(fig_telemetry, use_container_width=True)

        # ปุ่มกดรีเซ็ตกลับไปดูภาพรวมทั้งสนาม
        if st.button("🔄 รีเซ็ตการซูมกลับไปดูทั่งสนาม"):
            st.session_state.selected_distance = None
            st.rerun()

    except Exception as e:
        st.error(f"❌ รูปแบบไฟล์ข้อมูลมีปัญหา หรือระบบดึงพิกัดผิดพลาด: {e}")
else:
    st.info("🏁 ยินดีต้อนรับสู่โปรแกรมวิเคราะห์ข้อมูล F1 Telemetry กรุณาโยนไฟล์ JSON เข้ามาเพื่อเริ่มพล็อตกราฟครับ")
