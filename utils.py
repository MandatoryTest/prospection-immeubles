def filtrer_mutations_par_date(mutations, date_min, date_max):
    return [
        m for m in mutations
        if date_min <= m["date_mutation"] <= date_max
    ]
