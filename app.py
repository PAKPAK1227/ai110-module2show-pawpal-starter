import streamlit as st

# Step 1: bring the logic-layer classes into the UI.
from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Plan the day's pet care around the time you have.")

# Step 2: application memory.
# Streamlit reruns this whole script on every interaction, so we keep the
# Owner (with its pets and tasks) in st.session_state instead of rebuilding it.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan", available_minutes=90)

owner: Owner = st.session_state.owner

st.divider()

# --- Owner + time budget -----------------------------------------------------
st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)
owner.available_minutes = st.number_input(
    "Time available today (minutes)",
    min_value=0,
    max_value=1440,
    value=owner.available_minutes,
    step=15,
)

st.divider()

# --- Step 3a: add a pet ------------------------------------------------------
st.subheader("Pets")
with st.form("add_pet", clear_on_submit=True):
    new_pet_name = st.text_input("Pet name", value="")
    c1, c2 = st.columns(2)
    with c1:
        new_species = st.selectbox("Species", ["dog", "cat", "other"])
    with c2:
        new_breed = st.text_input("Breed", value="")
    add_pet_clicked = st.form_submit_button("Add pet")

if add_pet_clicked:
    if new_pet_name.strip():
        owner.add_pet(Pet(new_pet_name.strip(), species=new_species, breed=new_breed.strip()))
        st.success(f"Added {new_pet_name.strip()}.")
    else:
        st.warning("Please enter a pet name.")

if not owner.pets:
    st.info("No pets yet. Add one above to start planning.")

st.divider()

# --- Step 3b: add a task to a pet -------------------------------------------
if owner.pets:
    st.subheader("Add a task")
    with st.form("add_task", clear_on_submit=True):
        target_pet_name = st.selectbox("For which pet?", [p.name for p in owner.pets])
        task_desc = st.text_input("Task", value="")
        d1, d2, d3 = st.columns(3)
        with d1:
            task_duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
        with d2:
            task_priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        with d3:
            task_frequency = st.selectbox("Frequency", ["daily", "weekly"])
        add_task_clicked = st.form_submit_button("Add task")

    if add_task_clicked:
        if task_desc.strip():
            pet = owner.find_pet(target_pet_name)
            pet.add_task(
                Task(
                    task_desc.strip(),
                    duration=int(task_duration),
                    priority=task_priority,
                    frequency=task_frequency,
                )
            )
            st.success(f"Added '{task_desc.strip()}' for {pet.name}.")
        else:
            st.warning("Please enter a task description.")

    # Show each pet's current tasks; checkboxes toggle completion in place.
    for pet in owner.pets:
        label = pet.name + (f" ({pet.breed})" if pet.breed else "")
        st.markdown(f"**{label}**")
        if not pet.tasks:
            st.caption("No tasks yet.")
        for task in pet.tasks:
            done = st.checkbox(str(task), value=task.completed, key=f"done_{task.id}")
            if done:
                task.mark_complete()
            else:
                task.mark_incomplete()

st.divider()

# --- Step 3c: generate the schedule -----------------------------------------
st.subheader("Today's Schedule")
if st.button("Generate schedule", type="primary", disabled=not owner.pets):
    scheduler = Scheduler()
    plan = scheduler.build_plan(owner)

    if plan["scheduled"]:
        rows = [
            {
                "Start": f"{entry['start']:%H:%M}",
                "End": f"{entry['end']:%H:%M}",
                "Task": entry["task"].description,
                "Pet": entry["pet"].name,
                "Priority": entry["task"].priority,
                "Min": entry["task"].duration,
            }
            for entry in plan["scheduled"]
        ]
        st.table(rows)
    else:
        st.info("Nothing could be scheduled. Add tasks or increase the available time.")

    if plan["skipped"]:
        st.markdown("**Skipped (ran out of time):**")
        for entry in plan["skipped"]:
            st.write(f"- {entry['task'].description} for {entry['pet'].name}")

    st.caption(plan["reasoning"])
