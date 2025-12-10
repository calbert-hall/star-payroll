#TODO make the logging nice
from logging import DEBUG

import numpy as np
import pandas as pd

SINGLE_INSTRUCTOR_BONUS = .5
DOUBLE_INSTRUCTOR_BONUS = .25

validation_savings = 0

def set_instructor_bonus(instructor_pay, instructor_name, total_reservations, bonus_rate, additive=False):
    global validation_savings
    exceptions_list = ['Hayley Hall', 'Hayley Smith', 'Kayla Neal', 'Kayla Johnson']
    if instructor_name not in exceptions_list:
        old_bonus = instructor_pay[instructor_name]['bonus']
        new_bonus = bonus_rate * total_reservations
        if additive:
           new_bonus = old_bonus + new_bonus
        else:
            validation_savings += old_bonus - new_bonus
        instructor_pay[instructor_name]['bonus'] = new_bonus
        print("Instructor {0} bonus adjusted from  {1} --> {2}".format(instructor_name, old_bonus, new_bonus))
    else:
        # Set 0 for bonus-exempt employees
        try:
            instructor_pay[instructor_name]['bonus'] = 0
            print("{0} bonus set to 0".format(instructor_name))
        except KeyError as e:
            print("Error: could not find instructor {0} to set bonus.".format(instructor_name))

def validate_bonus(instructor_pay, reservations_df, staff_names, output_path):
    print("Validating Reservations...")
    filtered_reservations = reservations_df[(~reservations_df['Customer Name'].isin(staff_names)) & \
                                            ~reservations_df['Class Type'].isin(['RockStar Free Ride', 'StarKids Lounge (45 mins)'])]
    filtered_reservations.to_csv(output_path + '/reservations-filtered.csv')
    grouped_reservations = filtered_reservations.groupby('Instructor Names').agg(checked_in_count=('Reservation ID', 'count'))
    print("Filtered and Validated Reservations by Instructor: ")
    print(grouped_reservations)
    for instructor, group in grouped_reservations.iterrows():
        instructor_list = instructor.split(",")
        if len(instructor_list) > 1:
            # A dual teaching scenario
            print("Multiple Instructor session: " + str(instructor_list))
            for name in instructor_list:
                #TODO fix bug since this breaks w/Kayla
                set_instructor_bonus(instructor_pay, name, group['checked_in_count'], DOUBLE_INSTRUCTOR_BONUS, True)
                instructor_pay[name]['hours'] += 1 # we increment hours since they need to both get the base pay. TODO maybe split elsewhere. This is wonky
        else:
            set_instructor_bonus(instructor_pay, instructor, group['checked_in_count'], SINGLE_INSTRUCTOR_BONUS)


# Should output a dataframe in Gusto format, and write a report of some kind. Text file?
def instructor_payroll(payroll_input, reservations_input, output_path):
    print("Getting Instructor Payroll data...")
    csvfile = pd.read_csv(payroll_input)
    #print(csvfile)
    ins_groups = csvfile.groupby('Instructor Display Name(s)')
    instructor_pay = {}
    staff_names = ['Hayley Hall', 'Casey Hall', 'Kayla Johnson', 'George Tharakan'] # Free riders, no bonuses for these

    #create a dataframe based on the payroll template.
    gusto_df = pd.read_csv('Gusto_Payroll_Template.csv')
    # Looping through the template names to exclude other staff members.
    for index, row in gusto_df.iterrows():
        name = row.first_name + " " +  row.last_name
        staff_names.append(name)

    print("Getting Reservation data...")
    reservations_df = pd.read_csv(reservations_input)
    for name, group in ins_groups:
        #print("Instructor: " + str(name))
        # While we're doing this already, this way we have all names and their variations covered.
        staff_names.append(str(name))
        classes_taught = group['Class ID'].count()
        #print("Classes Taught: " + str(classes_taught))

        if str(name) in ['Kayla Johnson', 'Kayla Neal']:
            #print("Setting Kayla's rider count to 0 .............")
            checked_in_riders = 0
        else:
            checked_in_riders = group['Checked In Reservations'].sum()

        #print("Sum of Checked-In Riders (Pre-validation): " + str(checked_in_riders))
        #print("Bonus (before validation): " + str(.5 * checked_in_riders))
        instructor_pay[str(name)] = {'hours': classes_taught, 'bonus': .5 * checked_in_riders}

    validate_bonus(instructor_pay, reservations_df, staff_names, output_path)

    print("~~~~~~ Validation Savings: ${0} ~~~~~~~~~~~".format(validation_savings))
    # Consider removing columns, since Gusto is allegedly "Smart" and can filter some of them out. ex. reimbursement will be in-app
    print("Setting Instructor Values in Gusto...")
    #TODO - filter by "Instructor" in gusto_df so you don't get the annoying errors
    for index, row in gusto_df.iterrows():
        rowname = row.first_name + " " +  row.last_name
        try:
            instructor_exists = instructor_pay[rowname]
            print("Setting instructor pay: {0} worked {1} hours, bonus: {2} ".format(rowname, instructor_pay[rowname]['hours'], instructor_pay[rowname]['bonus']))
            gusto_df.at[index,'regular_hours'] = instructor_pay[rowname]['hours']
            gusto_df.at[index,'bonus'] = instructor_pay[rowname]['bonus']
        except KeyError as e:
            #print(f"Error: Template employee '{e}' not an instructor.")
            gusto_df.drop(index, inplace=True)

    gusto_df.to_csv(output_path + '/instructors_output.csv', index=False)
    return gusto_df
