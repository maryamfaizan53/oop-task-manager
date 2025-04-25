import streamlit as st
import json
from datetime import datetime, date
import pandas as pd

# Task Class
class Task:
    def __init__(self, title, description, category, priority, due_date, status="Pending"):
        self.title = title
        self.description = description
        self.category = category  # e.g., Work, Personal, Study
        self.priority = priority  # e.g., High, Medium, Low
        self.due_date = due_date  # e.g., YYYY-MM-DD
        self.status = status  # e.g., Pending, Completed
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "priority": self.priority,
            "due_date": self.due_date,
            "status": self.status,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["title"],
            data["description"],
            data["category"],
            data["priority"],
            data["due_date"],
            data["status"]
        )

# TaskManager Class
class TaskManager:
    def __init__(self, filename="tasks.json"):
        self.tasks = []
        self.filename = filename
        self.load_tasks()

    def add_task(self, task):
        self.tasks.append(task)
        self.save_tasks()

    def view_tasks(self, category=None, priority=None, status=None):
        filtered_tasks = self.tasks
        if category and category != "All":
            filtered_tasks = [t for t in filtered_tasks if t.category == category]
        if priority and priority != "All":
            filtered_tasks = [t for t in filtered_tasks if t.priority == priority]
        if status and status != "All":
            filtered_tasks = [t for t in filtered_tasks if t.status == status]
        return filtered_tasks

    def update_task(self, index, **kwargs):
        if 0 <= index < len(self.tasks):
            task = self.tasks[index]
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            self.save_tasks()
            return True
        return False

    def delete_task(self, index):
        if 0 <= index < len(self.tasks):
            self.tasks.pop(index)
            self.save_tasks()
            return True
        return False

    def save_tasks(self):
        try:
            with open(self.filename, 'w') as f:
                json.dump([task.to_dict() for task in self.tasks], f, indent=4)
        except Exception as e:
            st.error(f"Error saving tasks: {e}")

    def load_tasks(self):
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                self.tasks = [Task.from_dict(item) for item in data]
        except FileNotFoundError:
            self.tasks = []
        except Exception as e:
            st.error(f"Error loading tasks: {e}")

# Custom CSS for professional and eye-catching UI
st.markdown("""
<style>
body {
    font-family: 'Arial', sans-serif;
}
.stApp {
    background-color: #f1c40f;
    text:black;
}
.sidebar .sidebar-content {
    background-color: #2c3e50;
    color: white;
    padding: 20px;
}
.stButton>button {
    background-color: #3498db;
    color: white;
    border-radius: 8px;
    padding: 10px 20px;
    transition: all 0.3s ease;
}
.stButton>button:hover {
    background-color: #2980b9;
    transform: scale(1.05);
}
.task-table th {
    background-color: #3498db;
    color: white;
    padding: 10px;
}
.task-table tr:nth-child(even) {
    background-color: #ecf0f1;
}
.task-table tr:hover {
    background-color: #dfe6e9;
}
.priority-high {
    color: #e74c3c;
    font-weight: bold;
}
.priority-medium {
    color: #27ae60;
    font-weight: bold;
}
.priority-low {
    color: #2ecc71;
    font-weight: bold;
}
.status-completed {
    color: #27ae60;
    font-style: italic;
}
@keyframes fadeIn {
    0% { opacity: 0; }
    100% { opacity: 1; }
}
.fade-in {
    animation: fadeIn 1s ease-in;
}
.stForm {
    background-color: #e74c3c;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# App title with emoji
st.title("📋 Personal Task Manager")
st.markdown('<div class="fade-in">Organize your tasks with ease!</div>', unsafe_allow_html=True)

# Initialize TaskManager in session state
if "manager" not in st.session_state:
    st.session_state.manager = TaskManager()

manager = st.session_state.manager

# Sidebar for adding tasks
with st.sidebar:
    st.header("➕ Add New Task")
    with st.form(key="add_task_form"):
        title = st.text_input("Title", max_chars=100, placeholder="Enter task title")
        description = st.text_area("Description", max_chars=500, placeholder="Enter task details")
        category = st.selectbox("Category", ["Work", "Personal", "Study"], help="Select task category")
        priority = st.selectbox("Priority", ["High", "Medium", "Low"], help="Select task priority")
        due_date = st.date_input("Due Date", min_value=date.today(), help="Select due date")
        submit_button = st.form_submit_button("Add Task")

        if submit_button:
            if title.strip():
                task = Task(title, description, category, priority, str(due_date))
                manager.add_task(task)
                st.success("Task added successfully! 🎉")
            else:
                st.error("Title is required.")

# Main section for viewing tasks
st.header("📋 Your Tasks")
col1, col2, col3 = st.columns(3)
with col1:
    filter_category = st.selectbox("Filter by Category", ["All", "Work", "Personal", "Study"])
with col2:
    filter_priority = st.selectbox("Filter by Priority", ["All", "High", "Medium", "Low"])
with col3:
    filter_status = st.selectbox("Filter by Status", ["All", "Pending", "Completed"])

# Sort option
sort_by = st.selectbox("Sort by", ["Created At", "Due Date", "Priority"], help="Sort tasks by selected field")

# Get and sort tasks
tasks = manager.view_tasks(filter_category, filter_priority, filter_status)
if sort_by == "Due Date":
    tasks.sort(key=lambda x: x.due_date)
elif sort_by == "Priority":
    tasks.sort(key=lambda x: {"High": 1, "Medium": 2, "Low": 3}[x.priority])
elif sort_by == "Created At":
    tasks.sort(key=lambda x: x.created_at)

# Display tasks in a table
if tasks:
    task_data = []
    for i, task in enumerate(tasks):
        priority_class = f"priority-{task.priority.lower()}"
        status_class = f"status-{task.status.lower()}"
        task_data.append({
            "Index": i,
            "Title": task.title,
            "Category": task.category,
            "Priority": f'<span class="{priority_class}">{task.priority}</span>',
            "Due Date": task.due_date,
            "Status": f'<span class="{status_class}">{task.status}</span>',
            "Created At": task.created_at
        })
    df = pd.DataFrame(task_data)
    st.markdown(df.to_html(escape=False, index=False, classes="task-table"), unsafe_allow_html=True)
else:
    st.info("No tasks match the filters.")

# Section for updating or deleting tasks
st.header("🛠️ Manage Tasks")
with st.expander("Update or Delete Task", expanded=False):
    task_index = st.number_input("Task Index", min_value=0, max_value=len(tasks)-1 if tasks else 0, step=1, help="Select task index from table")
    if tasks and 0 <= task_index < len(tasks):
        selected_task = tasks[task_index]
        st.write(f"Selected Task: **{selected_task.title}**")
        with st.form(key="update_task_form"):
            new_title = st.text_input("New Title", value=selected_task.title, max_chars=100)
            new_description = st.text_area("New Description", value=selected_task.description, max_chars=500)
            new_category = st.selectbox("New Category", ["Work", "Personal", "Study"], index=["Work", "Personal", "Study"].index(selected_task.category))
            new_priority = st.selectbox("New Priority", ["High", "Medium", "Low"], index=["High", "Medium", "Low"].index(selected_task.priority))
            new_status = st.selectbox("New Status", ["Pending", "Completed"], index=["Pending", "Completed"].index(selected_task.status))
            new_due_date = st.date_input("New Due Date", value=date.fromisoformat(selected_task.due_date), min_value=date.today())
            update_button = st.form_submit_button("Update Task")
            delete_button = st.form_submit_button("Delete Task")

            if update_button:
                if new_title.strip():
                    manager.update_task(
                        task_index,
                        title=new_title,
                        description=new_description,
                        category=new_category,
                        priority=new_priority,
                        status=new_status,
                        due_date=str(new_due_date)
                    )
                    st.success("Task updated successfully! ✅")
                else:
                    st.error("Title is required.")
            
            if delete_button:
                manager.delete_task(task_index)
                st.success("Task deleted successfully! 🗑️")
                st.experimental_rerun()  # Refresh to update task list
    else:
        st.warning("Select a valid task index.")

# Footer
st.markdown("---")
st.markdown('<div class="fade-in">Built by Maryam Faizan ❤️ using Streamlit</div>', unsafe_allow_html=True)
