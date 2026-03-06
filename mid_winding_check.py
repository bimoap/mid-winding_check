import streamlit as st
import math
import matplotlib.pyplot as plt

# --- PAGE SETUP ---
st.set_page_config(page_title="Pancake Winding Checker", layout="wide")
st.title("Pancake Winding Checker")

# --- SIDEBAR: GLOBAL SPECIFICATIONS ---
st.sidebar.header("Coil Specifications")
req_turns = st.sidebar.number_input("Target Turns", min_value=1, value=172, step=1)

# 1. Dynamic Geometry Input Selection
spec_mode = st.sidebar.selectbox(
    "Dimension Input Method", 
    ["Direct Winding Window", "Cooling Plate ID & OD", "Cooling Plate Inner & Outer Radius"]
)

st.sidebar.markdown("---")

if spec_mode == "Direct Winding Window":
    former_od = st.sidebar.number_input("Winding Former OD (mm)", min_value=1.0, value=100.5, step=0.5)
    available_radial_build = st.sidebar.number_input("Available Radial Build Space (mm)", min_value=0.1, value=78.75, step=0.1)
    max_coil_od = former_od + (available_radial_build * 2.0)

elif spec_mode == "Cooling Plate ID & OD":
    cooling_plate_od = st.sidebar.number_input("Cooling Plate OD (mm)", min_value=1.0, value=259.0, step=1.0)
    cooling_plate_id = st.sidebar.number_input("Cooling Plate ID (mm)", min_value=1.0, value=100.0, step=1.0)
    max_coil_od = cooling_plate_od - 0.5
    former_od = cooling_plate_id + 0.5
    available_radial_build = (max_coil_od - former_od) / 2.0

else: # Cooling Plate Inner & Outer Radius
    cooling_plate_outer_rad = st.sidebar.number_input("Cooling Plate Outer Radius (mm)", min_value=1.0, value=129.5, step=0.5)
    cooling_plate_inner_rad = st.sidebar.number_input("Cooling Plate Inner Radius (mm)", min_value=1.0, value=50.0, step=0.5)
    max_coil_od = (cooling_plate_outer_rad * 2.0) - 0.5
    former_od = (cooling_plate_inner_rad * 2.0) + 0.5
    available_radial_build = (max_coil_od - former_od) / 2.0

# 2. Dynamic Material Input Selection
st.sidebar.subheader("Materials")
unit_mode = st.sidebar.radio("Measurement Unit", ["Metric (mm)", "Imperial (thou)"], horizontal=True)

if unit_mode == "Imperial (thou)":
    st.sidebar.caption("Enter values in 'thou'. The script auto-converts to mm.")
    
    nominal_cu_thou = st.sidebar.number_input("Nominal Cu Thickness (thou)", min_value=0.1, value=15.0, format="%.1f")
    nominal_cu = nominal_cu_thou * 0.0254
    st.sidebar.caption(f"↳ Metric equivalent: **{nominal_cu:.4f} mm**")
    
    mylar_thick_thou = st.sidebar.number_input("Primary Mylar (thou)", min_value=0.1, value=3.0, format="%.1f")
    mylar_thick = mylar_thick_thou * 0.0254
    st.sidebar.caption(f"↳ Metric equivalent: **{mylar_thick:.4f} mm**")
    
    mylar_thin_thou = st.sidebar.number_input("Thin Mylar (thou)", min_value=0.1, value=2.0, format="%.1f")
    mylar_thin = mylar_thin_thou * 0.0254
    st.sidebar.caption(f"↳ Metric equivalent: **{mylar_thin:.4f} mm**")

else:
    st.sidebar.caption("Enter values in 'mm'. The script auto-converts to thou for reference.")
    
    nominal_cu = st.sidebar.number_input("Nominal Cu Thickness (mm)", min_value=0.001, value=0.381, format="%.3f")
    st.sidebar.caption(f"↳ Imperial equivalent: **{nominal_cu / 0.0254:.1f} thou**")
    
    mylar_thick = st.sidebar.number_input("Primary Mylar (mm)", min_value=0.001, value=0.0762, format="%.4f")
    st.sidebar.caption(f"↳ Imperial equivalent: **{mylar_thick / 0.0254:.1f} thou**")
    
    mylar_thin = st.sidebar.number_input("Thin Mylar (mm)", min_value=0.001, value=0.0508, format="%.4f")
    st.sidebar.caption(f"↳ Imperial equivalent: **{mylar_thin / 0.0254:.1f} thou**")

# --- SIGNATURE BLOCK ---
st.sidebar.markdown("---")
st.sidebar.markdown("<div style='text-align: center; color: gray; padding-top: 20px;'>"
                    "<em>App developed & maintained by:</em><br>"
                    "<strong>Bimo Adhi Prastya</strong><br>"
                    "<span style='font-size: 0.8em;'>Coil Shop Technician</span>"
                    "</div>", unsafe_allow_html=True)

# --- TABS ---
tab1, tab2 = st.tabs(["📋 Pre-winding check", "🔍 Mid-Winding Check"])

# ==========================================
# TAB 1: PRE-WINDING CHECK
# ==========================================
with tab1:
    st.header("Pre-winding check")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Max Allowable OD", f"{max_coil_od:.2f} mm")
        st.caption(f"↳ Radius: **{max_coil_od / 2.0:.2f} mm**")
    with col2:
        st.metric("Winding Former OD", f"{former_od:.2f} mm")
        st.caption(f"↳ Radius: **{former_od / 2.0:.2f} mm**")
    with col3:
        st.metric("Available Radial Space", f"{available_radial_build:.3f} mm")
    
    st.markdown("---")
    
    if available_radial_build <= 0:
        st.error("🚨 **GEOMETRY CONFLICT:** The Winding Former OD is larger than the Max Allowable Coil OD.")
    else:
        cu_build = req_turns * nominal_cu
        mylar_build = req_turns * mylar_thick
        total_required_build = cu_build + mylar_build
        
        st.subheader("Required Winding Build")
        rc1, rc2, rc3 = st.columns(3)
        rc1.metric("Total Nominal Copper Build", f"{cu_build:.3f} mm")
        rc2.metric("Total Mylar Build", f"{mylar_build:.3f} mm")
        rc3.metric("Total Required Build", f"{total_required_build:.3f} mm")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if total_required_build > available_radial_build:
            shortfall = total_required_build - available_radial_build
            st.error(f"🚨 **WINDING EXCEEDS SPACE:** The coil needs {total_required_build:.3f} mm but only has {available_radial_build:.3f} mm. (Shortfall: {shortfall:.3f} mm)")
        else:
            clearance = available_radial_build - total_required_build
            st.success(f"✅ **WINDING FEASIBLE:** The coil will fit. Remaining theoretical clearance is {clearance:.3f} mm.")

# ==========================================
# TAB 2: MID-WINDING CHECK
# ==========================================
with tab2:
    st.header("Mid-Winding check")
    st.write("Enter actual mid-winding measurements below.")
    st.caption("*Assumption: Mylar thickness is exact and uniform. All pitch deviation is attributed solely to uniform copper thickness tolerance.*")
    
    qc_col1, qc_col2 = st.columns(2)
    with qc_col1:
        current_turn = st.number_input("Current Turn Count", min_value=1, max_value=int(req_turns), value=45, step=1)
    with qc_col2:
        current_radial_build = st.number_input("Current Radial Build Measurement (mm)", min_value=0.1, value=21.5, step=0.1, format="%.2f")

    st.markdown("---")

    if current_turn > 0 and available_radial_build > 0:
        remaining_radial_space = available_radial_build - current_radial_build
        remaining_turns = req_turns - current_turn
        
        # Calculate real-world physics based on uniform copper tolerance
        actual_pitch = current_radial_build / current_turn
        calculated_actual_cu = actual_pitch - mylar_thick
        cu_deviation = calculated_actual_cu - nominal_cu
        
        projected_remaining_build = actual_pitch * remaining_turns
        projected_total_build = current_radial_build + projected_remaining_build
        projected_final_od = former_od + (2 * projected_total_build)

        # ----------------------------------------
        # Visual Progress Bar Generation
        # ----------------------------------------
        st.subheader("Radial Build Progress")
        
        fig, ax = plt.subplots(figsize=(10, 1.5))
        
        # Background bar (Total Available Space)
        ax.barh(0, available_radial_build, color='#e0e0e0', edgecolor='black', height=0.5, label='Available Space')
        
        # Current Build bar
        ax.barh(0, current_radial_build, color='#4CAF50', height=0.5, label='Current Build')
        
        # Projected Build bar (stacked on current)
        projected_color = '#FFC107' if projected_total_build <= available_radial_build else '#F44336'
        ax.barh(0, projected_remaining_build, left=current_radial_build, color=projected_color, alpha=0.8, height=0.5, label='Projected Remaining')

        # Add limit line
        ax.axvline(x=available_radial_build, color='red', linestyle='--', linewidth=2, label='Max Allowable Limit')

        ax.set_yticks([]) # Hide y axis
        ax.set_xlabel('Radial Space (mm)')
        ax.set_xlim(0, max(available_radial_build, projected_total_build) * 1.1) # Scale x-axis with 10% padding
        ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.8), ncol=4)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        
        st.pyplot(fig)
        # ----------------------------------------

        st.subheader("Current Metrics & Derived Tolerances")
        m1, m2, m3 = st.columns(3)
        m1.metric("Calculated Actual Cu", f"{calculated_actual_cu:.4f} mm", delta=f"{cu_deviation:+.4f} mm vs nominal", delta_color="inverse")
        m2.metric("Projected Total Build", f"{projected_total_build:.3f} mm")
        
        if projected_total_build <= available_radial_build:
            m3.metric("Projected Final OD", f"{projected_final_od:.2f} mm", delta=f"Limit: {max_coil_od:.2f}", delta_color="normal")
        else:
            m3.metric("Projected Final OD", f"{projected_final_od:.2f} mm", delta=f"Limit: {max_coil_od:.2f}", delta_color="inverse")

        st.markdown("<br>", unsafe_allow_html=True)

        # Decision Logic
        if projected_total_build <= available_radial_build:
            st.success("✅ **ON TRACK:** The current copper tolerance is within limits. Continue winding with primary mylar.")
            next_check = current_turn + math.floor(remaining_turns / 2)
            if next_check < req_turns:
                st.info(f"💡 **Recommendation:** Take the next measurement around turn **{next_check}**.")
        else:
            oversize_amount = projected_total_build - available_radial_build
            st.warning(f"⚠️ **COIL OVERSIZED:** Due to copper running thick, projected to exceed space by {oversize_amount:.3f} mm.")
            
            # Rescue Plan Calculation
            mylar_difference = mylar_thick - mylar_thin
            new_expected_pitch = calculated_actual_cu + mylar_thin 
            
            max_thick_turns_left = (remaining_radial_space - (remaining_turns * new_expected_pitch)) / mylar_difference
            max_thick_turns_left = math.floor(max_thick_turns_left)
            
            st.subheader("Rescue Plan")
            if max_thick_turns_left < 0:
                st.error("🚨 **CRITICAL:** Switching to thin mylar immediately will NOT save the coil. The copper is running too thick to fit the required turns in this space.")
            else:
                switch_turn = current_turn + max_thick_turns_left
                if switch_turn >= req_turns:
                    st.info("The math suggests it will fit with the primary mylar. Please verify your measurements.")
                else:
                    st.warning(f"🔧 **ACTION:** Change to thin mylar ({mylar_thin:.4f} mm) at **TURN {switch_turn}**.")
                    st.write(f"This allows {max_thick_turns_left} more turns with the primary mylar.")
                    
                    if max_thick_turns_left > 10:
                        measurement_turn = current_turn + math.floor(max_thick_turns_left / 2)
                        st.info(f"💡 **Recommendation:** Verify radial build again at turn **{measurement_turn}** to confirm the copper tolerance hasn't drifted before making the switch.")
                    else:
                        st.info("💡 **Recommendation:** Winding space is tight. Verify radial build every 5 turns.")
