import os
import xlrd
import csv

def convert_excel_to_csv(excel_file_obj):
    workbook = xlrd.open_workbook(file_contents=excel_file_obj.read())
    sheet_names = workbook.sheet_names()
    sheet = workbook.sheet_by_name(sheet_names[0])
    excel_file_obj.name = excel_file_obj.name.replace('xlsx', 'csv').replace('xls', 'csv')
    excel_file_obj.open('w+')
    csv_writer = csv.writer(excel_file_obj, quoting=csv.QUOTE_ALL)
    for row_number in xrange(sheet.nrows):
        csv_writer.writerow(sheet.row_values(row_number))
    return (excel_file_obj, excel_file_obj.path.replace('xlsx', 'csv').replace('xls', 'csv'))


def parse_demographic_data(csvFile):
    data = csv.DictReader(csvFile)

    # Mapping from dictionary keys to column names:
    params = {
        'wage' : 'Ending Wage', # NOTE: starting vs ending wage?
        'employer' : 'Employer Name',
        'position' : 'Position Title',
        'ethnicity' : 'Ethnicity',
        'gender' : 'Gender'
    }
    keys = {
        'employer',
        'position',
        'ethnicity',
        'gender'
    }
    sets = {k : set() for k in keys}
    avgs = {k : {} for k in keys}
    counts = {k : {} for k in keys}

    for row in data:
        for key in sets.keys():
            val = row[params[key]]
            if len(val) > 0:
                sets[key].add(val)

            if len(row[params['wage']]) > 0:
                try:
                    salary = float(row[params['wage']])
                except ValueError:
                    continue
                for key in avgs.keys():
                    val = row[params[key]]
                    if val in avgs[key].keys():
                        avgs[key][val] += salary
                        counts[key][val] += 1
                    else:
                        avgs[key][val] = salary
                        counts[key][val] = 1

    for k in counts.keys():
        for l in counts[k].keys():
            if counts[k][l] > 0:
                avgs[k][l] /= counts[k][l]

    return sets, avgs, counts

def get_barriers(csvFile):
    data = csv.DictReader(csvFile)
    barrierSet = set()
    for row in data:
        if row["Barrier"] != '':
            barrierSet.add(row["Barrier"])
    return barrierSet

def get_disabilities(csvFile):
    data = csv.DictReader(csvFile)
    disabilitySet = set()
    for row in data:
        if row["Disability"] != '':
            disabilitySet.add(row["Disability"])
    return disabilitySet
