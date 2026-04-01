def compatibility_score(viewer_profile , listing_profile):
    IMPORTANCE_POINTS = {0: 0 , 1: 5 , 2: 10, 3: 0}

    total_possible = 0
    total_earned = 0

    factors = [
        ('cleanliness' , 'cleanliness_importance'),
        ('sleep_schedule' , 'sleep_schedule_importance'),
        ('is_smoker' , 'smoker_importance'),
        ('has_pets' , 'pets_importance'),
        ('noise_level', 'noise_level_importance'),
    ]

    for field, importance_field in factors:
        importance = getattr(viewer_profile, importance_field)
        viewer_val = getattr(viewer_profile , field)
        listing_val = getattr(listing_profile , field)
        match = viewer_val == listing_val

        if importance == 3 and not match:
            return 0, True

        points = IMPORTANCE_POINTS[importance]
        total_possible += points
        if match:
            total_earned += points
        
    budget_importance = viewer_profile.budget_importance
    v_min = viewer_profile.budget_min
    v_max = viewer_profile.budget_max
    l_min = listing_profile.budget_min
    l_max = listing_profile.budget_max

    if v_min is not None and v_max is not None and l_min is not None and l_max is not None:
        budget_match = v_min <= l_max and l_min <= v_max
        if budget_importance == 3 and not budget_match:
            return 0,True
        points = IMPORTANCE_POINTS[budget_importance]
        total_possible += points
        if budget_match:
            total_earned += points

    if total_possible == 0:
        return 100, False
    
    score = round((total_earned / total_possible) * 100)
    return score, False
