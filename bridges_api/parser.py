from csv import DictReader

def parseEmployerNames(file):
    with file.open(mode='r') as csv:
        data = DictReader(csv)
        # Mapping from dictionary keys to column names:
        params = {
            'wage' : 'Starting Wage', # NOTE: starting vs ending wage?
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
        avgs = {k : 0 for k in keys}
        counts = {k : 0 for k in keys}

        for row in data:
            salary = rows[params['wage']]

            for key in sets.keys():
                val = rows[params[key]]
                sets[key].add(val)

            for key in avgs.keys():
                val = rows[params[key]]
                avgs[key] += salary
                count[key] += 1

        for key in params.keys():
            if count[key] > 0:
                avgs[key] /= count[key]

        return sets, avgs
