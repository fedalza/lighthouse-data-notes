"""
 - Connect to the hr.db (stored in supporting-files directory) with sqlite3 
 - Write a query to get the department name and number of employees in the department.
 - Sort the data by number of employees starting from the highest.



Expected columns:
    - department_name
    - number_of_employees

Notes:
    - Use tables employees and departments
    - You can connect to DB from Jupyter Lab/Notebook, explore the table and try different queries
    - In the variable 'SQL' store only the final query ready for validation 
"""



import sqlite3 as sqlite
from sqlalchemy import create_engine
import pandas as pd

SQL = """ SELECT d.department_name, count(e.employee_id) as number_of_employees from departments as d
            JOIN employees as e
                ON d.department_id = e.department_id
                GROUP BY department_name
                ORDER BY number_of_employees DESC
            """
with create_engine('sqlite:///supporting_files/hr.db').connect() as con:
    df = pd.read_sql(SQL, con)

con.close()