import json
import streamlit as st

st.set_page_config(page_title="Scholarship Advisory Rule-Based System")

st.title("Scholarship Advisory Rule-Based System")
st.write(
    "This app uses a rule-based engine to help the university decide "
    "scholarship eligibility based on applicant data."
)



DEFAULT_RULES_JSON = """
[
    {
        "name": "Top merit candidate",
        "priority": 100,
        "conditions": [
            ["cgpa", ">=", 3.7],
            ["co_curricular_score", ">=", 80],
            ["family_income", "<=", 8000],
            ["disciplinary_actions", "==", 0]
        ],
        "action": {
            "decision": "AWARD_FULL",
            "reason": "Excellent academic & co-curricular performance, with acceptable need"
        }
    },
    {
        "name": "Good candidate - partial scholarship",
        "priority": 80,
        "conditions": [
            ["cgpa", ">=", 3.3],
            ["co_curricular_score", ">=", 60],
            ["family_income", "<=", 12000],
            ["disciplinary_actions", "<=", 1]
        ],
        "action": {
            "decision": "AWARD_PARTIAL",
            "reason": "Good academic & involvement record with moderate need"
        }
    },
    {
        "name": "Need-based review",
        "priority": 70,
        "conditions": [
            ["cgpa", ">=", 2.5],
            ["family_income", "<=", 4000]
        ],
        "action": {
            "decision": "REVIEW",
            "reason": "High need but borderline academic score"
        }
    },
    {
        "name": "Low CGPA – not eligible",
        "priority": 95,
        "conditions": [
            ["cgpa", "<", 2.5]
        ],
        "action": {
            "decision": "REJECT",
            "reason": "CGPA below minimum scholarship requirement"
        }
    },
    {
        "name": "Serious disciplinary record",
        "priority": 90,
        "conditions": [
            ["disciplinary_actions", ">=", 2]
        ],
        "action": {
            "decision": "REJECT",
            "reason": "Too many disciplinary records"
        }
    }
]
"""

st.subheader("Scholarship Rules (JSON)")
st.caption("You may view or adjust the rules here. The default matches the lab question exactly.")

rules_json_input = st.text_area(
    "Edit rules as JSON:",
    value=DEFAULT_RULES_JSON.strip(),
    height=400
)


rules = []
try:
    rules = json.loads(rules_json_input)
    st.success("Rules loaded successfully.")
except json.JSONDecodeError as e:
    st.error(f"JSON error: {e}")
    st.stop()


st.subheader("Applicant Information")

col1, col2 = st.columns(2)

with col1:
    cgpa = st.number_input("Cumulative GPA (CGPA)", min_value=0.0, max_value=4.0, step=0.01, value=3.5)
    family_income = st.number_input("Monthly family income (RM)", min_value=0.0, step=100.0, value=5000.0)
    co_curricular_score = st.number_input("Co-curricular involvement score (0–100)", min_value=0, max_value=100, value=70)

with col2:
    community_service_hours = st.number_input("Community service hours", min_value=0, step=1, value=10)
    current_semester = st.number_input("Current semester of study", min_value=1, step=1, value=3)
    disciplinary_actions = st.number_input("Number of disciplinary actions", min_value=0, step=1, value=0)

facts = {
    "cgpa": cgpa,
    "family_income": family_income,
    "co_curricular_score": co_curricular_score,
    "community_service_hours": community_service_hours,
    "current_semester": current_semester,
    "disciplinary_actions": disciplinary_actions
}



def check_condition(facts_dict, field, op, value):
    """Evaluate a single condition like [\"cgpa\", \">=\", 3.7]."""
    v = facts_dict.get(field)

    if v is None:
        return False

    if op == ">=":
        return v >= value
    elif op == "<=":
        return v <= value
    elif op == ">":
        return v > value
    elif op == "<":
        return v < value
    elif op == "==":
        return v == value
    elif op == "!=":
        return v != value
    else:
        return False


def evaluate_rules(rules_list, facts_dict):
    """
    Forward-chaining style: check each rule's conditions.
    Return the highest-priority rule that matches all its conditions.
    """
    
    sorted_rules = sorted(rules_list, key=lambda r: r.get("priority", 0), reverse=True)

    fired_rule = None
    for rule in sorted_rules:
        conditions = rule.get("conditions", [])
        if all(check_condition(facts_dict, c[0], c[1], c[2]) for c in conditions):
            fired_rule = rule
            break

    return fired_rule



if st.button("Evaluate Scholarship Eligibility"):
    rule = evaluate_rules(rules, facts)

    st.subheader("Decision")

    if rule is None:
        st.warning("No rule matched. Please send this case for manual review.")
    else:
        action = rule.get("action", {})
        decision = action.get("decision", "UNKNOWN")
        reason = action.get("reason", "No reason provided.")

        st.write(f"*Fired rule:* {rule.get('name', 'Unnamed rule')}")
        st.write(f"*Decision:* {decision}")
        st.write(f"*Reason:* {reason}")

    st.subheader("Applicant Facts Used")
    st.json(facts)