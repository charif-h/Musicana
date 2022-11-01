def getAllFieldValues(tracks, field="genre"):
    field_vals = {}
    for (key, value) in tracks.items():
        if field in value.keys():
            for v in value[field]:
                if v in field_vals:
                    field_vals[v] += 1
                else:
                    field_vals[v] = 1
    print(field_vals)
    return field_vals