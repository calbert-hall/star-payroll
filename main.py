import csv
import sys
import instructors
import non_instructors
from datetime import datetime
from pathlib import Path

instructor_payroll_path = "inputs/report-instructor-payroll.csv"
reservations_path = "inputs/report-reservations.csv"
employee_payroll_path = "inputs/report-employee-payroll.csv"

def validate_args():
    valid = True
    if len(sys.argv) == 1:
        print("no params detected. Setting default values.")
        #sys.argv[1] = "inputs/report-instructor-payroll.csv"
        #sys.argv[2] = "inputs/report-reservations.csv"
        #sys.argv[3] = "inputs/report-employee-payroll.csv"

        return valid

    elif len(sys.argv) == 4:
        print("three args detected.")
        try:
            if not str(sys.argv[1]).endswith(".csv"):
                print("instructor payroll .csv file required for argument 1")
                valid = False
            if not str(sys.argv[2]).endswith(".csv"):
                print("reservations .csv file required for argument 2")
                valid = False
            if not str(sys.argv[3]).endswith(".csv"):
                print("staff payroll .csv file required for argument 3")
                valid = False
            instructor_payroll_path = sys.argv[1]
            reservations_path = sys.argv[2]
            employee_payroll_path = sys.argv[3]
        except IndexError:
            print("Three arguments required:\n1 - Instructor Payroll \n2 - Reservations \n3 - Staff Payroll")
    else:
        print("Weird number of args, should be 0 or 3.")
        valid = False

    return valid

print("Argv length: " + str(len(sys.argv)))
# Take in the 3 CSV files. Init the Gusto and Report CSVs.
validate_args()

#TODO validate the template itself. this thing needs to be the golden document. Warnings/logs for employees with no shift.
# Also flag employee names (in other files?) that are not listed in the template! Maybe in the other py files

# 1. Get the current date and time
now = datetime.now()
output_path = 'outputs/' + now.strftime("%Y-%m-%d_%H-%M-%S")
Path(output_path).mkdir(exist_ok=True)
print(f"Directory '{output_path}' created successfully! ✅")

gusto_instructor_payroll = instructors.instructor_payroll(instructor_payroll_path, reservations_path, output_path)
gusto_staff_payroll = non_instructors.non_instructor_payroll(employee_payroll_path, output_path)

# Merges Staff and Instructor Payroll
gusto_payroll_df = gusto_staff_payroll.merge(gusto_instructor_payroll, how='outer')

gusto_payroll_df.to_csv(output_path + '/final_gusto.csv')
# do any final tidying / validations, export CSV