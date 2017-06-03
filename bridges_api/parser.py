from csv import DictReader

def parse_demographic_data(csvFile):
    data = DictReader(csvFile)

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
            sets[key].add(val)

            if row[params['wage']] != "":
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

    return sets, avgs

def get_barriers(csvFile):
    data = DictReader(csvFile)
    barrierSet = set()
    for row in data:
        if row["Barrier"] != '':
            barrierSet.add(row["Barrier"])
    return barrierSet

def get_disabilities(csvFile):
    data = DictReader(csvFile)
    disabilitySet = set()
    for row in data:
        if row["Disability"] != '':
            disabilitySet.add(row["Disability"])
    return disabilitySet
