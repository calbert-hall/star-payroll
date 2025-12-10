import pandas as pd
from datetime import datetime
from pathlib import Path

def non_instructor_payroll(non_instructor_payroll_csv, output_path):

    print("Getting non-instructor payroll...")
    non_instructor_df = pd.read_csv(non_instructor_payroll_csv)
    grouped_employees = non_instructor_df.groupby('Employee Name').agg(sum_hours=('Total Shift Time', 'sum')).round(2)
    grouped_employees.to_csv(output_path + '/employee_hours.csv')

    print(grouped_employees)
    gusto_df = pd.read_csv('Gusto_Payroll_Template.csv')
    print("Setting Staff Values in Gusto...")

    #TODO - filter out "Instructor" in gusto_df so you don't get the annoying errors
    for index, row in gusto_df.iterrows():
        row_name = row.first_name + " " + row.last_name
        try:
            staff_group = grouped_employees.loc[row_name]
            gusto_df.at[index, 'regular_hours'] = staff_group['sum_hours']
        except KeyError as e:
            #print(f"Warning: Template employee '{e}' not on staff (non-instructors).")
            gusto_df.drop(index, inplace=True)

    #print(gusto_df)
    return gusto_df