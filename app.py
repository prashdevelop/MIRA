import streamlit as st
import pandas as pd

# Configure mobile-first responsive viewport
st.set_page_config(
    page_title="Refractory Pre-Bid Intelligence",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Enterprise Mobile CSS
st.markdown("""
<style>
    .main { background-color: #f8fafc; }
    .card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        color: #ffffff;
        margin-bottom: 6px;
    }
    .badge-l1 { background-color: #dc2626; }
    .badge-bal { background-color: #2563eb; }
    .badge-eco { background-color: #16a34a; }
    .badge-jit { background-color: #d97706; }
    .badge-sla { background-color: #7c3aed; }
</style>
""", unsafe_allow_html=True)

# ----------------- DATA REPOSITORY -----------------
SIGNALS = [
    {
        "lead_id": "LEAD-101",
        "client": "Tata Steel (Kalinganagar)",
        "project": "Blast Furnace #2 Hearth Expansion",
        "engine": "Idea #13: Statutory Parivesh NLP",
        "lead_time": "120 Days Pre-RFQ",
        "volume_tons": 4200,
        "equipment_default": "Steel Ladle (150T - 300T)"
    },
    {
        "lead_id": "LEAD-102",
        "client": "AM/NS India (Hazira)",
        "project": "150T Ladle Fleet Maintenance Cycle",
        "engine": "Idea #10: Consumable Wear Telemetry",
        "lead_time": "5 Days Pre-RFQ",
        "volume_tons": 1200,
        "equipment_default": "Steel Ladle (150T - 300T)"
    },
    {
        "lead_id": "LEAD-103",
        "client": "JSW Steel (Vijayanagar)",
        "project": "BOF Converter Shop #3 Augmentation",
        "engine": "Idea #13: Corporate CAPEX Filing",
        "lead_time": "60 Days Pre-RFQ",
        "volume_tons": 3800,
        "equipment_default": "BOF Converter (160T - 250T)"
    },
    {
        "lead_id": "LEAD-104",
        "client": "SAIL (Bokaro Steel)",
        "project": "320T Torpedo Ladle Car Fleet Reline",
        "engine": "Idea #10: Consumable Wear Telemetry",
        "lead_time": "32 Days Pre-RFQ",
        "volume_tons": 2400,
        "equipment_default": "Torpedo Ladle Car (320T)"
    }
]

EQUIPMENT_ZONE_SPEC = {
    "Steel Ladle (150T - 300T)": {
        "Slagline": {"virgin_base": 793.40, "ref_bid": 930.0, "req_ccs": 45.0, "req_hmor": 10.0, "req_ap": 4.2, "req_tsr": 28},
        "Barrel & Sidewall": {"virgin_base": 715.20, "ref_bid": 820.0, "req_ccs": 40.0, "req_hmor": 8.0, "req_ap": 5.0, "req_tsr": 25},
        "Impact Bottom": {"virgin_base": 760.50, "ref_bid": 880.0, "req_ccs": 48.0, "req_hmor": 11.0, "req_ap": 4.0, "req_tsr": 30}
    },
    "BOF Converter (160T - 250T)": {
        "Trunnion & Taphole Area": {"virgin_base": 796.45, "ref_bid": 920.0, "req_ccs": 55.0, "req_hmor": 12.0, "req_ap": 3.8, "req_tsr": 32},
        "Vessel Bottom & Tuyeres": {"virgin_base": 780.00, "ref_bid": 890.0, "req_ccs": 50.0, "req_hmor": 11.0, "req_ap": 4.0, "req_tsr": 30},
        "Upper Cone / Lip": {"virgin_base": 740.00, "ref_bid": 840.0, "req_ccs": 45.0, "req_hmor": 9.0, "req_ap": 4.5, "req_tsr": 26}
    },
    "Consteel / AC EAF (120T - 150T)": {
        "Hotspot / Sidewall Panels": {"virgin_base": 730.00, "ref_bid": 830.0, "req_ccs": 46.0, "req_hmor": 9.5, "req_ap": 4.3, "req_tsr": 27},
        "Delta Roof & Electrode Ring": {"virgin_base": 890.00, "ref_bid": 980.0, "req_ccs": 58.0, "req_hmor": 13.0, "req_ap": 3.6, "req_tsr": 35}
    },
    "Torpedo Ladle Car (320T)": {
        "ASC Impact Pad": {"virgin_base": 1083.20, "ref_bid": 1190.0, "req_ccs": 50.0, "req_hmor": 12.5, "req_ap": 3.9, "req_tsr": 32},
        "Main Belly / Shell Lining": {"virgin_base": 960.00, "ref_bid": 1060.0, "req_ccs": 45.0, "req_hmor": 10.0, "req_ap": 4.4, "req_tsr": 28}
    },
    "AOD Vessel (120T Stainless)": {
        "Tuyere Master Lining": {"virgin_base": 1050.00, "ref_bid": 1220.0, "req_ccs": 60.0, "req_hmor": 14.0, "req_ap": 3.5, "req_tsr": 36},
        "Main Cone / Bath": {"virgin_base": 940.00, "ref_bid": 1090.0, "req_ccs": 52.0, "req_hmor": 11.5, "req_ap": 4.0, "req_tsr": 30}
    }
}

SCRAP_ASSAYS = {
    "LOT_001 (Tata Steel Core - 92.4% MgO, 1.8% SiO2)": {"cost": 127.0, "sio2": 1.8, "mgo": 92.4},
    "LOT_004 (Tata Steel BOF - 93.1% MgO, 1.4% SiO2)": {"cost": 131.0, "sio2": 1.4, "mgo": 93.1},
    "LOT_011 (AM/NS Hazira - 92.2% MgO, 1.8% SiO2)": {"cost": 128.0, "sio2": 1.8, "mgo": 92.2},
    "LOT_014 (SAIL Bokaro - 86.5% MgO, 4.4% SiO2)": {"cost": 108.0, "sio2": 4.4, "mgo": 86.5}
}

# ----------------- SIDEBAR SELECTION PANEL -----------------
st.sidebar.markdown("### 1. Market Intercept Signal")
signal_options = [f"{s['lead_id']} | {s['client']} - {s['project']}" for s in SIGNALS]
selected_signal_str = st.sidebar.selectbox("Active Pipeline Opportunity", signal_options)
selected_signal = next(s for s in SIGNALS if s["lead_id"] == selected_signal_str.split(" | ")[0])

st.sidebar.markdown("---")
st.sidebar.markdown("### 2. Equipment & Zone Architecture")
selected_equipment = st.sidebar.selectbox("Target Equipment", list(EQUIPMENT_ZONE_SPEC.keys()))
available_zones = list(EQUIPMENT_ZONE_SPEC[selected_equipment].keys())
selected_zone = st.sidebar.selectbox("Application Zone", available_zones)
zone_spec = EQUIPMENT_ZONE_SPEC[selected_equipment][selected_zone]

st.sidebar.markdown("---")
st.sidebar.markdown("### 3. Customer Rate-Wise 'What-If'")
customer_rate_target = st.sidebar.slider(
    "Target Budget / Price Cap ($/Mt)",
    min_value=500.0,
    max_value=1300.0,
    value=float(round(zone_spec["ref_bid"] * 0.85, -1)),
    step=10.0
)

selected_scrap_str = st.sidebar.selectbox("Allocated Yard Inventory", list(SCRAP_ASSAYS.keys()))
active_scrap = SCRAP_ASSAYS[selected_scrap_str]

# ----------------- MAIN UI BANNER -----------------
st.title("Refractory Pre-Bidding & Autonomous Formulation Platform")
st.markdown(
    f"**Pipeline Signal:** `{selected_signal['client']}` | "
    f"**Asset:** `{selected_equipment}` ({selected_zone}) | "
    f"**Detected Via:** `{selected_signal['engine']}` ({selected_signal['lead_time']})"
)

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("Intercept Lead Time", selected_signal["lead_time"], delta="Pre-RFQ Head Start")
col_m2.metric("Project Scope", f"{selected_signal['volume_tons']:,} Mt")
col_m3.metric("Customer Rate Cap", f"${customer_rate_target:.2f}/t")
col_m4.metric("Competitor Market Rate", f"${zone_spec['ref_bid']:.2f}/t")

st.markdown("---")

# ----------------- IDEA #8 FORMULATION ENGINE -----------------
def generate_offerings(spec, scrap, budget_target):
    fixed_conversion = 160.0
    s_cost = scrap["cost"]
    s_sio2 = scrap["sio2"]

    catalog_blueprint = [
        {"id": "OPT 1", "name": "Ultra-Aggressive Disruptor", "badge": "badge-l1", "scrap_pct": 38.0, "virgin_pct": 46.0, "rate_rule": "l1", "lead": "10 Days", "sla": "Guaranteed L1 Price (Tender Baseline)"},
        {"id": "OPT 2", "name": "Value-Optimized Balanced", "badge": "badge-bal", "scrap_pct": 25.0, "virgin_pct": 59.0, "rate_rule": "bal", "lead": "12 Days", "sla": "Optimal Margin & Campaign Life (+15%)"},
        {"id": "OPT 3", "name": "Eco-Circularity Green BOM", "badge": "badge-eco", "scrap_pct": 30.0, "virgin_pct": 54.0, "rate_rule": "eco", "lead": "12 Days", "sla": "Scope 3 Decarbonization Certified"},
        {"id": "OPT 4", "name": "Fast-Track JIT Clearance", "badge": "badge-jit", "scrap_pct": 35.0, "virgin_pct": 49.0, "rate_rule": "jit", "lead": "3 Days", "sla": "Immediate Mobilization from Yard Stock"},
        {"id": "OPT 5", "name": "Performance SLA Premium", "badge": "badge-sla", "scrap_pct": 0.0, "virgin_pct": 82.0, "rate_rule": "sla", "lead": "14 Days", "sla": "Guaranteed Zero-Breakout Performance SLA"}
    ]

    offerings = []
    for item in catalog_blueprint:
        # Physical Reality Equations: Reclaimed aggregate surface area penalty
        resin_pct = 4.0 + (item["scrap_pct"] / 10.0) * 0.4
        alumina_compensator = 2.5 if (s_sio2 > 2.0 and item["scrap_pct"] > 20) else 0.0
        graphite_pct = 100.0 - (item["scrap_pct"] + item["virgin_pct"] + resin_pct + alumina_compensator)

        # Landed Raw Material Cost
        rm_cost = (
            (item["scrap_pct"] / 100.0 * s_cost) +
            (item["virgin_pct"] / 100.0 * 650.0) +
            (resin_pct / 100.0 * 2150.0) +
            (alumina_compensator / 100.0 * 980.0) +
            (graphite_pct / 100.0 * 950.0)
        )
        total_landed = rm_cost + fixed_conversion

        # Dynamic Pricing Logic
        if item["rate_rule"] == "l1":
            unit_quote = min(budget_target * 0.96, total_landed * 1.10)
        elif item["rate_rule"] == "eco":
            unit_quote = budget_target
        elif item["rate_rule"] == "sla":
            unit_quote = max(budget_target * 1.25, spec["ref_bid"])
            total_landed = spec["virgin_base"] + fixed_conversion
            item["scrap_pct"] = 0.0
            item["virgin_pct"] = 82.0
            resin_pct = 4.0
        elif item["rate_rule"] == "jit":
            unit_quote = budget_target * 0.98
        else:
            unit_quote = budget_target * 1.05

        unit_quote = round(unit_quote, 2)
        total_landed = round(total_landed, 2)
        gross_margin = round(((unit_quote - total_landed) / unit_quote) * 100, 1)

        # Predicted Metallurgical Properties
        ccs_calc = round(spec["req_ccs"] + 8.0 - (item["scrap_pct"] * 0.28) - (s_sio2 * 1.1) + (alumina_compensator * 1.2), 1)
        hmor_calc = round(spec["req_hmor"] + 2.5 - (item["scrap_pct"] * 0.12) - (s_sio2 * 0.4), 1)
        ap_calc = round(spec["req_ap"] - 0.4 + (item["scrap_pct"] * 0.03) + (s_sio2 * 0.08), 2)
        tsr_calc = int(spec["req_tsr"] + 4 - (item["scrap_pct"] * 0.15))
        co2_cut = round((item["scrap_pct"] / 100.0) * 82.0, 1)

        qc_pass = (ccs_calc >= spec["req_ccs"]) and (hmor_calc >= spec["req_hmor"]) and (ap_calc <= spec["req_ap"])

        offerings.append({
            **item,
            "resin_pct": round(resin_pct, 1),
            "unit_quote": unit_quote,
            "total_landed": total_landed,
            "gross_margin": gross_margin,
            "ccs": ccs_calc,
            "hmor": hmor_calc,
            "ap": ap_calc,
            "tsr": tsr_calc,
            "co2_cut": co2_cut,
            "qc_pass": qc_pass
        })
    return offerings

catalog = generate_offerings(zone_spec, active_scrap, customer_rate_target)

# ----------------- 5-OPTION STOREFRONT (AMAZON LAYOUT) -----------------
st.subheader("Select Commercial Bidding Package")
cols = st.columns(5)

for idx, opt in enumerate(catalog):
    with cols[idx]:
        st.markdown(f"<span class='badge {opt['badge']}'>{opt['id']}</span>", unsafe_allow_html=True)
        st.markdown(f"**{opt['name']}**")
        st.caption(opt["sla"])

        st.metric("Unit Bid Quote", f"${opt['unit_quote']}/t", f"{opt['gross_margin']}% Margin")
        st.markdown(f"**Landed Cost:** `${opt['total_landed']}/t`")
        st.markdown(f"**Blend:** `{opt['scrap_pct']}% Scrap / {opt['virgin_pct']}% Virgin`")
        
        st.markdown("---")
        st.markdown("**Key Parameters:**")
        st.write(f"- CCS: **{opt['ccs']} MPa** (Req: ≥{zone_spec['req_ccs']})")
        st.write(f"- HMOR: **{opt['hmor']} MPa** (Req: ≥{zone_spec['req_hmor']})")
        st.write(f"- Porosity (AP): **{opt['ap']}%** (Req: ≤{zone_spec['req_ap']})")
        st.write(f"- Thermal Shock: **>{opt['tsr']} cycles**")
        st.write(f"- Scope 3 CO₂: **-{opt['co2_cut']}%**")
        st.write(f"- Lead Time: **{opt['lead']}**")

        if opt["qc_pass"]:
            st.success("✅ Specification Compliant")
        else:
            st.error("❌ High-Temp Risk")

        if st.button(f"Configure {opt['id']}", key=f"btn_{idx}", use_container_width=True):
            st.session_state["selected_opt"] = opt

# ----------------- TECHNICAL DOSSIER & PROPOSAL MEMO -----------------
if "selected_opt" not in st.session_state:
    st.session_state["selected_opt"] = catalog[0]

chosen = st.session_state["selected_opt"]

st.markdown("---")
st.subheader(f"Engineering Audit & Executive Memo: {chosen['id']} - {chosen['name']}")

tab_memo, tab_bom = st.tabs(["📄 Leadership Proposal Memo", "🔬 Recipe Chemistry Breakdown"])

with tab_memo:
    total_rev = chosen['unit_quote'] * selected_signal['volume_tons']
    total_cost = chosen['total_landed'] * selected_signal['volume_tons']
    net_profit = total_rev - total_cost

    memo = f"""EXECUTIVE PRE-BID PROPOSAL
TO: Commercial Leadership & Plant Operations Team
CLIENT: {selected_signal['client']}
PROJECT: {selected_signal['project']}
EQUIPMENT: {selected_equipment} ({selected_zone})
ORDER VOLUME: {selected_signal['volume_tons']:,} Metric Tons

COMMERCIAL POSITIONING:
- Selected Strategy: {chosen['id']} - {chosen['name']}
- Quoted Bid Price: ${chosen['unit_quote']:.2f} / Mt (Matches Target Cap: ${customer_rate_target:.2f}/Mt)
- Competitor Reference Price: ${zone_spec['ref_bid']:.2f} / Mt (Undercut: ${zone_spec['ref_bid'] - chosen['unit_quote']:.2f}/Mt)
- Total Landed Cost: ${chosen['total_landed']:.2f} / Mt
- Net Gross Profit: ${net_profit:,.2f} ({chosen['gross_margin']}% Margin)
- Delivery Lead Time: {chosen['lead']}

METALLURGICAL QUALITY VALIDATION (ASTM COMPLIANT):
- Cold Crushing Strength (CCS @ 25°C): {chosen['ccs']} MPa (Tender Min: {zone_spec['req_ccs']} MPa)
- Hot Modulus of Rupture (HMOR @ 1400°C): {chosen['hmor']} MPa (Tender Min: {zone_spec['req_hmor']} MPa)
- Apparent Porosity (AP): {chosen['ap']}% (Tender Max: {zone_spec['req_ap']}%)
- Thermal Shock Resistance: >{chosen['tsr']} Cycles

CIRCULAR ECONOMY IMPACT:
- Secondary Scrap Aggregate Blended: {chosen['scrap_pct']}%
- Yard Inventory Liquidated: {(chosen['scrap_pct']/100.0)*selected_signal['volume_tons']:,.0f} Metric Tons
- Scope 3 CO2 Footprint Reduction: -{chosen['co2_cut']}%
"""
    st.text_area("Pre-Bid Proposal Memo", memo, height=260)
    st.download_button(
        "Download Executive Dossier (.txt)",
        data=memo,
        file_name=f"PreBid_Proposal_{selected_signal['lead_id']}_{chosen['id']}.txt",
        mime="text/plain"
    )

with tab_bom:
    col_b1, col_b2 = st.columns([3, 2])
    with col_b1:
        bom_data = [
            {"Material Layer": "Secondary Aggregate", "Component": f"Reclaimed Scrap ({selected_scrap_str.split(' ')[0]})", "Batch %": f"{chosen['scrap_pct']}%", "Base Cost": f"${active_scrap['cost']:.2f}/t"},
            {"Material Layer": "Virgin Mineral", "Component": "Electrofused Magnesia (FM 98)", "Batch %": f"{chosen['virgin_pct']}%", "Base Cost": "$650.00/t"},
            {"Material Layer": "Binder Matrix", "Component": "Novolac Phenolic Resin", "Batch %": f"{chosen['resin_pct']}%", "Base Cost": "$2,150.00/t"},
            {"Material Layer": "Carbon & Additives", "Component": "Flake Graphite & Antioxidants", "Batch %": f"{round(100 - chosen['scrap_pct'] - chosen['virgin_pct'] - chosen['resin_pct'], 1)}%", "Base Cost": "$950.00/t"},
            {"Material Layer": "Fixed Operational", "Component": "Hydraulic Pressing & Firing", "Batch %": "Fixed Factor", "Base Cost": "$160.00/t"}
        ]
        st.table(pd.DataFrame(bom_data))
    with col_b2:
        st.write(f"**Gross Revenue:** `${total_rev:,.2f}`")
        st.write(f"**Total Landed Cost:** `${total_cost:,.2f}`")
        st.write(f"**Gross Profit:** `${net_profit:,.2f}`")
        st.write(f"**Scrap Consumed:** `{(chosen['scrap_pct']/100.0)*selected_signal['volume_tons']:,.0f} Tons`")
