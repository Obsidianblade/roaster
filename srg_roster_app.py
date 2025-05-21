# [Previous imports remain the same]
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
from io import BytesIO
import base64
from streamlit_calendar import calendar

# Enhanced 3D UI Styling
st.markdown("""
    <style>
        /* 3D Glowing UI */
        .stApp {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        }
        
        .css-1r6slb0, .css-12oz5g7, .stDataFrame {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
            box-shadow: 
                0 8px 32px 0 rgba(31, 38, 135, 0.37),
                0 0 10px rgba(0, 102, 204, 0.5);
            backdrop-filter: blur(4px);
            border: 1px solid rgba(255, 255, 255, 0.18);
            padding: 1.5rem;
            margin: 1rem 0;
            transition: all 0.3s ease;
        }
        
        .css-1r6slb0:hover, .css-12oz5g7:hover {
            transform: translateY(-5px);
            box-shadow: 
                0 12px 40px 0 rgba(31, 38, 135, 0.45),
                0 0 15px rgba(0, 102, 204, 0.6);
        }
        
        .stButton > button {
            background: linear-gradient(135deg, #0066cc 0%, #0052a3 100%);
            color: white;
            border-radius: 8px;
            padding: 10px 24px;
            border: none;
            box-shadow: 0 4px 15px rgba(0, 102, 204, 0.3);
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 102, 204, 0.4);
        }
        
        /* Calendar Styling */
        .fc {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 
                0 8px 32px 0 rgba(31, 38, 135, 0.37),
                0 0 10px rgba(0, 102, 204, 0.5);
        }
        
        .fc-timegrid-slot, .fc-timegrid-axis-cushion {
            font-weight: bold;
            color: #0066cc;
        }
        
        .fc-theme-standard td, .fc-theme-standard th {
            border-color: #e6e6e6;
        }
        
        .fc-header-toolbar {
            background: linear-gradient(135deg, #0066cc 0%, #0052a3 100%);
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px !important;
        }
        
        .fc-button {
            background: white !important;
            color: #0066cc !important;
            border: none !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        
        .fc-button:hover {
            background: #f8f9fa !important;
            transform: translateY(-1px);
        }
    </style>
""", unsafe_allow_html=True)

# [Previous helper functions remain the same]

# Modified calendar configuration
def create_calendar_config(events, default_view="timeGridWeek"):
    return {
        "events": events,
        "options": {
            "initialView": default_view,
            "headerToolbar": {
                "left": "prev,next today",
                "center": "title",
                "right": "timeGridWeek,dayGridMonth"
            },
            "slotMinTime": "06:00:00",
            "slotMaxTime": "22:00:00",
            "slotDuration": "00:30:00",
            "allDaySlot": False,
            "height": "auto",
            "expandRows": True,
            "stickyHeaderDates": True,
            "nowIndicator": True,
            "slotEventOverlap": False,
            "businessHours": {
                "daysOfWeek": [0, 1, 2, 3, 4, 5, 6],
                "startTime": "06:00",
                "endTime": "22:00",
            }
        }
    }

# [Previous code remains the same until Lecturer Portal section]

# Modified Lecturer Portal calendar view
elif page == "Lecturer Portal":
    # [Previous lecturer portal code remains the same until the calendar tab]
    
    with tab2:
        st.subheader("📆 Complete Roster Calendar")
        all_events = []
        for sid, data in st.session_state.users.items():
            for sh in data.get("shifts", []):
                all_events.append({
                    "title": f"{data['name']} ({sh['display']})",
                    "start": f"{sh['date']}T{sh['start']}",
                    "end": f"{sh['date']}T{sh['end']}",
                    "color": status_colors[sh['status']],
                    "extendedProps": {
                        "student_id": sid,
                        "status": sh['status']
                    }
                })
        
        # Calendar view controls
        col1, col2 = st.columns([2, 1])
        with col2:
            view_type = st.selectbox(
                "Calendar View",
                ["Week View", "Month View"],
                index=0
            )
        
        # Configure calendar based on selected view
        calendar_config = create_calendar_config(
            all_events,
            "timeGridWeek" if view_type == "Week View" else "dayGridMonth"
        )
        
        # Render enhanced calendar
        st.markdown("""
            <div style='background: white; padding: 20px; border-radius: 12px; box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);'>
        """, unsafe_allow_html=True)
        calendar(**calendar_config)
        st.markdown("</div>", unsafe_allow_html=True)

        # Add legend
        st.markdown("### 📋 Status Legend")
        legend_cols = st.columns(3)
        for i, (status, color) in enumerate(status_colors.items()):
            with legend_cols[i]:
                st.markdown(f"""
                    <div style='
                        background: {color};
                        color: white;
                        padding: 8px 15px;
                        border-radius: 6px;
                        text-align: center;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                    '>
                        {status}
                    </div>
                """, unsafe_allow_html=True)

# [Rest of the code remains the same]
