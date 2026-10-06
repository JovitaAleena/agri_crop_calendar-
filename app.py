"""AgriPlan: Digital Crop Calendar & Action Scheduler.

A Streamlit web application for farmers to schedule and track crop activities.
"""

from datetime import date, datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.calculator import generate_crop_schedule, get_crop_list, load_crops_data
from utils.fertilizer import calculate_fertilizer_and_seeds

# Page configuration
st.set_page_config(
    page_title="AgriPlan - Digital Crop Calendar & Scheduler",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for polished, modern agricultural styling
st.markdown(
    """
    <style>
    /* Global styles */
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1b5e20;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4b6b50;
        margin-bottom: 1.5rem;
    }
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #f1f8e9 0%, #ffffff 100%);
        border: 1px solid #c8e6c9;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px -2px rgba(0, 0, 0, 0.08);
    }
    .metric-label {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #558b2f;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #1b5e20;
        line-height: 1.2;
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #689f38;
        margin-top: 4px;
    }

    /* Timeline Task Cards */
    .timeline-card {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-left: 6px solid #2e7d32;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 14px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }
    .timeline-card.due-today {
        border-left-color: #f57c00;
        background: #fffdf9;
    }
    .timeline-card.completed {
        border-left-color: #388e3c;
        background: #fcfdfc;
    }
    .timeline-card.upcoming {
        border-left-color: #1976d2;
        background: #ffffff;
    }
    .badge-chip {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 8px;
    }
    .badge-completed {
        background-color: #e8f5e9;
        color: #2e7d32;
        border: 1px solid #a5d6a7;
    }
    .badge-due-today {
        background-color: #fff3e0;
        color: #e65100;
        border: 1px solid #ffcc80;
    }
    .badge-upcoming {
        background-color: #e3f2fd;
        color: #1565c0;
        border: 1px solid #90caf9;
    }
    .category-chip {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 500;
        background-color: #eceff1;
        color: #37474f;
    }
    .action-text {
        font-size: 1.05rem;
        font-weight: 600;
        color: #212121;
        margin: 8px 0 4px 0;
    }
    .details-text {
        font-size: 0.92rem;
        color: #555555;
        margin-bottom: 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def get_cached_crops():
    """Load and cache the crops database."""
    return load_crops_data()


# Main Application Logic
def main():
    crops_db = get_cached_crops()
    crop_names = get_crop_list(crops_db)

    # Sidebar Navigation & Inputs
    with st.sidebar:
        st.markdown("## 🌾 AgriPlan")
        st.markdown("**Digital Crop Calendar & Action Scheduler**")
        st.caption("Plan, monitor, and optimize your farm operations from sowing to harvest.")
        st.divider()

        st.subheader("⚙️ Farm & Crop Settings")

        selected_crop = st.selectbox(
            "Select Crop",
            options=crop_names,
            index=0,
            help="Choose your target crop from verified agronomic templates.",
        )

        col_date_reset, col_quick_today = st.columns([2, 1])
        with col_date_reset:
            default_sowing = date.today() - timedelta(days=20)
            sowing_date = st.date_input(
                "Sowing / Planting Date",
                value=default_sowing,
                max_value=date.today() + timedelta(days=120),
                min_value=date.today() - timedelta(days=365),
                help="The date seeds were sown in nursery or planted in field.",
            )
        with col_quick_today:
            st.write("")
            st.write("")
            if st.button("Set Today", use_container_width=True):
                sowing_date = date.today()

        col_area, col_unit = st.columns([1.4, 1.2])
        with col_area:
            land_area = st.number_input(
                "Land Area",
                min_value=0.1,
                max_value=10000.0,
                value=2.5,
                step=0.5,
                help="Total cultivated field area.",
            )
        with col_unit:
            area_unit = st.selectbox(
                "Unit",
                options=["Acres", "Hectares"],
                index=0,
            )

        st.divider()

        # Crop Quick Facts in sidebar
        crop_data = crops_db[selected_crop]
        st.markdown(f"**About {selected_crop}:**")
        st.caption(crop_data.get("description", "Standard agronomic crop."))
        st.caption(f"⏱️ **Total Cycle:** {crop_data.get('growth_duration_days', 0)} days")
        st.caption(f"🌱 **Seed Rate:** {crop_data.get('seed_rate_kg_per_acre', 0)} {crop_data.get('seed_unit', 'kg')}/acre")

        st.markdown("---")
        st.caption("💡 *Tip: Keep notifications in sync with local weather forecasts.*")

    # Generate calculations
    df_schedule, summary = generate_crop_schedule(
        crop_name=selected_crop,
        sowing_date=sowing_date,
        crops_data=crops_db,
    )

    fert_data = calculate_fertilizer_and_seeds(
        crop_info=crop_data,
        land_area=land_area,
        area_unit=area_unit,
    )

    # Top Header
    st.markdown(
        f'<div class="main-header">🌾 {selected_crop} — Crop Calendar & Schedule</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="sub-header">Field Plan for <strong>{fert_data["area_display"]}</strong> | Sown on <strong>{sowing_date.strftime("%B %d, %Y")}</strong> | Harvest on <strong>{summary["harvest_date"].strftime("%B %d, %Y")}</strong></div>',
        unsafe_allow_html=True,
    )

    # Top Metric Cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">⏱️ Total Duration</div>
                <div class="metric-value">{summary["total_duration_days"]} <span style="font-size:1rem; font-weight:normal;">Days</span></div>
                <div class="metric-sub">Sown: {summary["sowing_date"].strftime("%b %d, %Y")}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">🌾 Est. Harvest Date</div>
                <div class="metric-value">{summary["harvest_date"].strftime("%b %d")}</div>
                <div class="metric-sub">{summary["harvest_date"].strftime("%Y")} ({max(0, (summary["harvest_date"] - date.today()).days)} days left)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">📅 Days Elapsed</div>
                <div class="metric-value">{summary["days_elapsed"]} <span style="font-size:1rem; font-weight:normal;">Days</span></div>
                <div class="metric-sub">{summary["progress_pct"]}% cycle completed</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        next_task = summary["next_task"]
        if next_task:
            if next_task["days_diff"] == 0:
                due_badge = "🔴 Due Today"
            elif next_task["days_diff"] > 0:
                due_badge = f"In {next_task['days_diff']} days"
            else:
                due_badge = "Completed"

            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">🔔 Next Immediate Task</div>
                    <div class="metric-value" style="font-size: 1.25rem;">{next_task["stage"]}</div>
                    <div class="metric-sub"><strong>{next_task["target_date"].strftime("%b %d")}</strong> ({due_badge})</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div class="metric-card">
                    <div class="metric-label">🔔 Next Immediate Task</div>
                    <div class="metric-value" style="font-size: 1.2rem;">All Done</div>
                    <div class="metric-sub">Crop ready for harvest</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")

    # Crop Growth Progress Bar
    prog_pct = min(100.0, max(0.0, summary["progress_pct"]))
    col_prog_label, col_prog_stats = st.columns([3, 1])
    with col_prog_label:
        st.markdown(f"**Crop Lifecycle Progress: `{prog_pct}%`**")
    with col_prog_stats:
        st.caption(f"Completed: **{summary['completed_tasks']}/{summary['total_tasks']}** stages")
    st.progress(prog_pct / 100.0)

    st.write("")

    # Tabs definition
    tab1, tab2, tab3 = st.tabs([
        "📋 Action Timeline",
        "📊 Gantt Schedule View",
        "🌱 Fertilizer & Seed Estimator",
    ])

    # ------------------ TAB 1: ACTION TIMELINE ------------------
    with tab1:
        st.subheader("📅 Stage-by-Stage Field Action Schedule")
        st.caption("Review chronological activities, mandatory agronomic inputs, and key pest/disease warnings.")

        # Filter bar
        filter_col1, filter_col2, filter_col3 = st.columns([2, 2, 2])
        with filter_col1:
            status_filter = st.multiselect(
                "Filter by Status",
                options=["Completed", "Due Today", "Upcoming"],
                default=["Completed", "Due Today", "Upcoming"],
            )
        with filter_col2:
            available_categories = sorted(df_schedule["category"].unique().tolist())
            category_filter = st.multiselect(
                "Filter by Category",
                options=available_categories,
                default=available_categories,
            )
        with filter_col3:
            search_query = st.text_input("🔍 Search Actions or Advice", "")

        # Filter dataframe
        filtered_df = df_schedule[
            (df_schedule["status"].isin(status_filter))
            & (df_schedule["category"].isin(category_filter))
        ]
        if search_query:
            q = search_query.lower()
            filtered_df = filtered_df[
                filtered_df["stage"].str.lower().str.contains(q)
                | filtered_df["action"].str.lower().str.contains(q)
                | filtered_df["details"].str.lower().str.contains(q)
            ]

        if filtered_df.empty:
            st.info("No stages match the selected filters.")
        else:
            for _, row in filtered_df.iterrows():
                status_class = row["status"].lower().replace(" ", "-")
                badge_class = f"badge-{status_class}"

                # Render custom card
                st.markdown(
                    f"""
                    <div class="timeline-card {status_class}">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
                            <div>
                                <span class="badge-chip {badge_class}">{row["status_badge"]}</span>
                                <span class="category-chip">🏷️ {row["category"]}</span>
                                <span style="margin-left: 8px; font-weight: 600; font-size: 1.1rem; color: #1b5e20;">
                                    Day {row["day_offset"]} — {row["stage"]}
                                </span>
                            </div>
                            <div style="font-weight: 600; color: #37474f; font-size: 0.95rem;">
                                📅 {row["target_date"].strftime("%A, %B %d, %Y")}
                            </div>
                        </div>
                        <div class="action-text">⚡ {row["action"]}</div>
                        <div class="details-text">💡 <strong>Agronomic Advice:</strong> {row["details"]}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # Tabular View Expander
        with st.expander("🔍 View Schedule in Spreadsheet Format"):
            display_cols = [
                "stage",
                "category",
                "day_offset",
                "target_date",
                "status_badge",
                "action",
                "details",
            ]
            st.dataframe(
                filtered_df[display_cols].rename(
                    columns={
                        "stage": "Stage Name",
                        "category": "Category",
                        "day_offset": "Day Offset",
                        "target_date": "Scheduled Date",
                        "status_badge": "Status",
                        "action": "Action Required",
                        "details": "Advice & Details",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )

        # Export Feature
        st.write("")
        st.subheader("📥 Export Schedule")
        export_csv = df_schedule[[
            "stage_id",
            "stage",
            "category",
            "day_offset",
            "target_date",
            "status",
            "action",
            "details",
        ]].rename(columns={
            "stage_id": "Stage #",
            "stage": "Stage Name",
            "category": "Category",
            "day_offset": "Day Offset",
            "target_date": "Target Date",
            "status": "Current Status",
            "action": "Action",
            "details": "Agronomic Advice",
        }).to_csv(index=False).encode("utf-8")

        st.download_button(
            label=f"⬇️ Download {selected_crop} Schedule (.CSV)",
            data=export_csv,
            file_name=f"agriplan_{selected_crop.lower().replace(' ', '_')}_schedule.csv",
            mime="text/csv",
            help="Download the complete farming schedule for offline tracking or spreadsheet import.",
        )

    # ------------------ TAB 2: GANTT SCHEDULE VIEW ------------------
    with tab2:
        st.subheader("📊 Interactive Crop Timeline (Gantt Chart)")
        st.caption("Visual distribution of agricultural operations across months.")

        gantt_df = df_schedule.copy()
        gantt_df["Start"] = pd.to_datetime(gantt_df["target_date"])
        gantt_df["Finish"] = pd.to_datetime(gantt_df["end_date"])

        # Plotly timeline chart
        fig = px.timeline(
            gantt_df,
            x_start="Start",
            x_end="Finish",
            y="stage",
            color="category",
            hover_name="stage",
            hover_data={
                "Start": "|%B %d, %Y",
                "Finish": "|%B %d, %Y",
                "action": True,
                "status": True,
                "category": False,
                "stage": False,
            },
            labels={
                "stage": "Growth Stage",
                "category": "Category",
                "action": "Required Action",
                "status": "Status",
            },
            title=f"Crop Stage Operations — {selected_crop}",
            color_discrete_sequence=px.colors.qualitative.Dark24,
        )

        fig.update_yaxes(autorange="reversed")  # First stage at the top

        # Add vertical line for Today
        today_ts = pd.to_datetime(date.today())
        fig.add_vline(
            x=today_ts,
            line_width=2,
            line_dash="dash",
            line_color="#d32f2f",
            annotation_text=f" Today ({date.today().strftime('%b %d')})",
            annotation_position="top left",
            annotation_font=dict(color="#d32f2f", size=11, family="Arial"),
        )

        fig.update_layout(
            xaxis_title="Calendar Date",
            yaxis_title="Stage",
            height=460,
            margin=dict(l=20, r=20, t=50, b=20),
            hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            ),
        )

        st.plotly_chart(fig, use_container_width=True)

        st.info(
            "💡 **Chart Guide:** The red dashed line highlights **Today's date**. "
            "Stages to the left are completed; stages to the right are upcoming."
        )

    # ------------------ TAB 3: FERTILIZER & SEED ESTIMATOR ------------------
    with tab3:
        st.subheader("🌱 Fertilizer & Seed Quantity Estimator")
        st.caption(f"Precision agronomic inputs calculated specifically for **{fert_data['area_display']}** of {selected_crop}.")

        # Seed requirement card
        seed_info = fert_data["seed"]
        st.markdown("#### 🌾 Certified Seed Requirement")
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            st.metric(
                label="Total Seed Quantity",
                value=seed_info["display"],
                delta=f"For {fert_data['area_display']}",
            )
        with col_s2:
            st.metric(
                label="Recommended Seed Rate",
                value=f"{seed_info['rate_per_acre']} {seed_info['unit']}/acre",
            )
        with col_s3:
            st.metric(
                label="Effective Cultivation Area",
                value=f"{fert_data['area_in_acres']} Acres",
            )

        st.divider()

        # Pure Nutrients summary
        st.markdown("#### 🧪 Elemental Nutrient Needs (Pure N - P - K)")
        pure_n = fert_data["nutrients_pure_kg"]
        col_n1, col_n2, col_n3 = st.columns(3)
        with col_n1:
            st.metric(label="Nitrogen (N)", value=f"{pure_n['Nitrogen (N)']} Kg")
        with col_n2:
            st.metric(label="Phosphorus (P₂O₅)", value=f"{pure_n['Phosphorus (P2O5)']} Kg")
        with col_n3:
            st.metric(label="Potassium (K₂O)", value=f"{pure_n['Potassium (K2O)']} Kg")

        st.write("")
        st.markdown("#### 🛍️ Commercial Fertilizer Bags to Purchase (50 Kg Bags)")
        st.caption("Calculated using standard Di-Ammonium Phosphate (DAP), Urea, and Muriate of Potash (MOP) distribution.")

        col_f1, col_f2, col_f3 = st.columns(3)
        com_fert = fert_data["commercial_fertilizers"]

        with col_f1:
            dap = com_fert["DAP (18:46:0)"]
            st.markdown(
                f"""
                <div class="metric-card" style="border-left: 5px solid #1976d2;">
                    <div class="metric-label">Phosphorus Source</div>
                    <div class="metric-value">DAP: {dap["bags_needed"]} <span style="font-size:1rem; font-weight:normal;">Bags</span></div>
                    <div style="font-size:0.9rem; color:#455a64; margin-top:4px;"><strong>Total:</strong> {dap["kg_needed"]} Kg</div>
                    <p style="font-size:0.82rem; color:#616161; margin-top:8px;">📌 {dap["application_tip"]}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_f2:
            urea = com_fert["Urea (46% N)"]
            st.markdown(
                f"""
                <div class="metric-card" style="border-left: 5px solid #388e3c;">
                    <div class="metric-label">Nitrogen Source</div>
                    <div class="metric-value">Urea: {urea["bags_needed"]} <span style="font-size:1rem; font-weight:normal;">Bags</span></div>
                    <div style="font-size:0.9rem; color:#455a64; margin-top:4px;"><strong>Total:</strong> {urea["kg_needed"]} Kg</div>
                    <p style="font-size:0.82rem; color:#616161; margin-top:8px;">📌 {urea["application_tip"]}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_f3:
            mop = com_fert["MOP (60% K2O)"]
            st.markdown(
                f"""
                <div class="metric-card" style="border-left: 5px solid #f57c00;">
                    <div class="metric-label">Potassium Source</div>
                    <div class="metric-value">MOP: {mop["bags_needed"]} <span style="font-size:1rem; font-weight:normal;">Bags</span></div>
                    <div style="font-size:0.9rem; color:#455a64; margin-top:4px;"><strong>Total:</strong> {mop["kg_needed"]} Kg</div>
                    <p style="font-size:0.82rem; color:#616161; margin-top:8px;">📌 {mop["application_tip"]}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.write("")
        st.success(
            "🌿 **Agri-Tip:** Always perform a soil health card test before bulk purchasing. "
            "For organic options, replace chemical NPK with well-rotted farmyard manure (FYM) or vermicompost."
        )

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #78909c; font-size: 0.85rem;'>"
        "🌾 <strong>AgriPlan Digital Crop Calendar</strong> | Designed for Farmers, Agronomists & Extension Officers."
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
