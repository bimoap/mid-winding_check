import streamlit as st
import math

# --- PAGE SETUP ---
st.set_page_config(page_title="Pancake Coil Winding Tool", layout="wide")
st.title("Pancake Coil Winding Calculator & QC")

# --- SIDEBAR: GLOBAL SPECIFICATIONS ---
st.sidebar.header("Coil Specifications")
req_turns = st.sidebar.number_input("Target Turns", min_value=1, value=100, step=1)
cooling_plate_od = st.sidebar.number_input("Cooling Plate OD (mm)", min_value=1.0, value=259.0, step=1.0)
cooling_plate_id = st.sidebar.number_input("Cooling Plate ID (mm)", min_value=1.0, value=120.0, step=1.0)

st.sidebar.markdown("---")
st.sidebar.subheader("Materials")
nominal_cu = st.sidebar.number_input("Nominal Cu Thickness (mm)", min_value=0.001, value=0.381, format="%.3f")
mylar_thick = st.sidebar.number_input("Primary Mylar (mm)", min_value=0.001, value=0.0762, format="%.4f")
mylar_thin = st.sidebar.number_input("Thin Mylar (mm)", min_value=0.001, value=0.0508, format="%.4f")

# --- GLOBAL GEOMETRY CALCULATIONS ---
max_coil_od = cooling_plate_od - 0.5
bobbin_od = cooling_plate_id + 0.5
available_radial_build = (max_coil_od - bobbin_od) / 2.0

# --- TABS ---
tab1, tab2 = st.tabs(["📋 Winding Planning", "🔍 Mid-Winding QC"])

# ==========================================
# TAB 1: WINDING PLANNING
# ==========================================
with tab1:
    st.header("Initial Feasibility Analysis")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Max Allowable OD", f"{max_coil_od:.2f} mm")
    col2.metric("Bobbin OD", f"{bobbin_od:.2f} mm")
    col3.metric("Available Radial Space", f"{available_radial_build:.3f} mm")
    
    st.markdown("---")
    
    if available_radial_build < 0:
        st.error("🚨 **GEOMETRY CONFLICT:** The Bobbin OD is larger than the Max Allowable Coil OD.")
    else:
        cu_build = req_turns * nominal_cu
        mylar_build = req_turns * mylar_thick
        total_required_build = cu_build + mylar_build
        
        st.subheader("Required Winding Build")
        rc1, rc2, rc3 = st.columns(3)
        rc1.metric("Total Copper Build", f"{cu_build:.3f} mm")
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
# TAB 2: MID-WINDING QC
# ==========================================
with tab2:
    st.header("Shop Floor Quality Control")
    st.write("Enter your actual mid-winding measurements below to project final dimensions.")
    
    qc_col1, qc_col2 = st.columns(2)
    with qc_col1:
        current_turn = st.number_input("Current Turn Count", min_value=1, max_value=int(req_turns), value=45, step=1)
    with qc_col2:
        current_radial_build = st.number_input("Current Radial Build Measurement (mm)", min_value=0.1, value=21.5, step=0.1, format="%.2f")

    st.markdown("---")

    if current_turn > 0:
        remaining_radial_space = available_radial_build - current_radial_build
        remaining_turns = req_turns - current_turn
        actual_pitch = current_radial_build / current_turn
        
        projected_remaining_build = actual_pitch * remaining_turns
        projected_total_build = current_radial_build + projected_remaining_build
        projected_final_od = bobbin_od + (2 * projected_total_build)

        st.subheader("Current Metrics & Projections")
        m1, m2, m3 = st.columns(3)
        m1.metric("Actual Average Pitch", f"{actual_pitch:.4f} mm/turn")
        m2.metric("Projected Total Build", f"{projected_total_build:.3f} mm")
        
        # Color the Final OD metric based on whether it passes or fails
        if projected_total_build <= available_radial_build:
            m3.metric("Projected Final OD", f"{projected_final_od:.2f} mm", delta=f"Limit: {max_coil_od:.2f}", delta_color="normal")
        else:
            m3.metric("Projected Final OD", f"{projected_final_od:.2f} mm", delta=f"Limit: {max_coil_od:.2f}", delta_color="inverse")

        st.markdown("<br>", unsafe_allow_html=True)

        # Decision Logic
        if projected_total_build <= available_radial_build:
            st.success("✅ **ON TRACK:** You are within tolerances. Continue winding with current mylar.")
            next_check = current_turn + math.floor(remaining_turns / 2)
            if next_check < req_turns:
                st.info(f"💡 **Recommendation:** Take the next measurement around turn **{next_check}**.")
        else:
            oversize_amount = projected_total_build - available_radial_build
            st.warning(f"⚠️ **COIL OVERSIZED:** Projected to exceed physical space by {oversize_amount:.3f} mm. Intervention required.")
            
            # Rescue Plan Calculation
            mylar_difference = mylar_thick - mylar_thin
            new_expected_pitch = actual_pitch - mylar_difference
            
            max_thick_turns_left = (remaining_radial_space - (remaining_turns * new_expected_pitch)) / mylar_difference
            max_thick_turns_left = math.floor(max_thick_turns_left)
            
            st.subheader("Rescue Plan")
            if max_thick_turns_left < 0:
                st.error("🚨 **CRITICAL:** Switching to thin mylar immediately will NOT save the coil. Unwind and apply more tension.")
            else:
                switch_turn = current_turn + max_thick_turns_left
                if switch_turn >= req_turns:
                    st.info("The math suggests it will fit with the current mylar. Please verify your inputs.")
                else:
                    st.warning(f"🔧 **ACTION:** Change to thin mylar ({mylar_thin:.4f} mm) at **TURN {switch_turn}**.")
                    st.write(f"This allows {max_thick_turns_left} more turns with the primary mylar.")
                    
                    if max_thick_turns_left > 10:
                        measurement_turn = current_turn + math.floor(max_thick_turns_left / 2)
                        st.info(f"💡 **Recommendation:** Verify pitch again at turn **{measurement_turn}** before making the switch.")
                    else:
                        st.info("💡 **Recommendation:** Winding space is tight. Verify pitch every 5 turns.")
