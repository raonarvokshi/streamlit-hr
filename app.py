import streamlit as st
from streamlit_option_menu import option_menu as om
import pandas as pd
import requests


def display_metrics(df):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="Total Employees", value=len(df))

    with col2:
        st.metric(label="Average Salary", value=f"${df['salary'].mean():.2f}")

    with col3:
        st.metric(label="Highest Salary", value=f"${df['salary'].max():.2f}")

    with col4:
        st.metric(label="Lowest Salary", value=f"${df['salary'].min():.2f}")


def gender_pie_chart(df):
    gender_counts = df['gender'].value_counts()
    gender_data = pd.DataFrame({
        'Gender': gender_counts.index,
        'Count': gender_counts.values
    })
    st.bar_chart(gender_data.set_index('Gender'))


def job_title_bar_chart(df):
    job_counts = df['job_title'].value_counts()
    job_data = pd.DataFrame({
        'Job Title': job_counts.index,
        'Count': job_counts.values
    })
    st.bar_chart(job_data.set_index('Job Title'))


def salary_distribution_chart(df):
    salary_data = df[['job_title', 'salary']].groupby('job_title').mean()
    st.bar_chart(salary_data['salary'])


def add_employee(full_name, email, gender, job_title, salary):
    data = {
        "full_name": full_name,
        "email": email,
        "gender": gender,
        "job_title": job_title,
        "salary": salary
    }
    response = requests.post(
        "https://fastapi-hr.onrender.com/add/employee", json=data)
    return response.json()


def get_all_employees():
    response = requests.get("https://fastapi-hr.onrender.com/employees")
    return response.json()


def update_employee(employee_id, full_name, email, gender, job_title, salary):
    data = {
        "full_name": full_name,
        "email": email,
        "gender": gender,
        "job_title": job_title,
        "salary": salary
    }

    response = requests.put(
        f"https://fastapi-hr.onrender.com/update/employee/{employee_id}", json=data)

    return response.json()


def delete_employee(employee_id):
    response = requests.delete(
        f"https://fastapi-hr.onrender.com/delete/employee/{employee_id}")

    return response.json()


with st.sidebar:
    st.title("Employee Managment")
    selected_menu = om(
        "Menu",
        options=["Employees Dashboard", "Add Employee",
                 "Edit Employee", "Delete Employee"],
        icons=["bar-chart-fill fs-4", "person-fill-add fs-4",
               "person-lines-fill fs-4", "person-x-fill fs-4"],
        menu_icon="bi-list fs-1",
        orientation="vertical",
    )

# selected_menu = st.sidebar.selectbox(
#     "Menu", options=["Employee Dashboard", "Add Employee", "Edit Employee", "Delete Employee"])

# with st.sidebar:
#     st.logo("logo.png", size="large")

if selected_menu == "Employees Dashboard":
    st.header("Employees managment dashboard")

    st.markdown("---")

    all_employees = get_all_employees()
    if all_employees:
        employees_df = pd.DataFrame(all_employees)
        if "id" in employees_df.columns:
            employees_df = employees_df.drop(columns=["id"])
        employees_df.reset_index(drop=True, inplace=True)

        st.subheader("📋 Employees Data")
        st.dataframe(employees_df, use_container_width=True, hide_index=True)

        st.markdown("---")

        st.subheader("📊 Metrics")
        display_metrics(employees_df)

        st.markdown("---")

        st.subheader("📈 Charts")
        st.markdown("### Gender Distribution")
        gender_pie_chart(employees_df)

        st.markdown("---")

        st.markdown("### Employees per Job Title")
        job_title_bar_chart(employees_df)

        st.markdown("---")

        st.markdown("### Salary Distribution by Job Title")
        salary_distribution_chart(employees_df)
    else:
        st.info("No employee in database")


elif selected_menu == "Add Employee":
    st.header("Add New Employee")
    st.markdown("---")
    full_name_input = st.text_input("Full Name", placeholder="Full Name...")
    email_input = st.text_input("Email", placeholder="Email...")
    gender_input = st.selectbox("Gender", options=["Male", "Female"])
    job_title_input = st.text_input("Job Title", placeholder="Job Title...")
    salary_input = st.number_input(
        "Salary", min_value=300.0, max_value=1000000.0, step=0.1)
    if st.button("Add New Employee"):
        if full_name_input and email_input and gender_input and job_title_input and salary_input:
            new_employee = add_employee(full_name=full_name_input, email=email_input,
                                        gender=gender_input, job_title=job_title_input, salary=salary_input)
            st.success(f"New employee added successfully!")
        else:
            st.error("All fields must be filled!")

elif selected_menu == "Edit Employee":
    st.header("Edit Employee")
    st.markdown("---")

    all_employees = get_all_employees()

    if all_employees:
        employee_names = [employee["full_name"] for employee in all_employees]
        edit_employee_select = st.selectbox(
            "**Select Employee to edit**", options=employee_names)
        st.markdown("---")
        selected_employee = next(
            employee for employee in all_employees if employee["full_name"] == edit_employee_select)

        if edit_employee_select:
            full_name_edit = st.text_input(
                "Full Name", placeholder="Full Name...", value=selected_employee["full_name"])

            email_edit = st.text_input(
                "Email", placeholder="Email...", value=selected_employee["email"])

            if selected_employee["gender"] == "Male":
                gender_edit = st.selectbox(
                    "Gender", options=["Male", "Female"])
            else:
                gender_edit = st.selectbox(
                    "Gender", options=["Female", "Male"])

            job_title_edit = st.text_input(
                "Job Title", placeholder="Job Title...", value=selected_employee["job_title"])

            salary_edit = st.number_input(
                "Salary", min_value=300.0, max_value=1000000.0, step=0.1, value=selected_employee["salary"])

            if st.button("Update Employee"):
                if full_name_edit and email_edit and gender_edit and job_title_edit and salary_edit:
                    new_employee = update_employee(employee_id=selected_employee["id"], full_name=full_name_edit, email=email_edit,
                                                   gender=gender_edit, job_title=job_title_edit, salary=salary_edit)
                    st.success(f"New employee added successfully!")
                else:
                    st.error("All fields must be filled!")
    else:
        st.info("No employee in database")

else:
    st.header("Delete Employee")
    st.write("You can delete an employee by selecting the name of the employee")
    st.markdown("---")

    all_employees = get_all_employees()
    if all_employees:
        employee_names = [employee["full_name"] for employee in all_employees]
        employee_to_delete = st.selectbox(
            "Select Employee to delete", employee_names)
        if employee_to_delete:
            selected_employee = next(
                employee for employee in all_employees if employee["full_name"] == employee_to_delete)

            if st.button(f"Delete {selected_employee["full_name"]}"):
                delete_employee(employee_id=selected_employee["id"])
                st.success(f"Employee deleted successfully!")
    else:
        st.info("No employee in database")
