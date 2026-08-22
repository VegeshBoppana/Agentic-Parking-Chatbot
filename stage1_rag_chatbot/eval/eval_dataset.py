EVAL_DATASET = [
    # general_info
    {"question": "What zones does SkyPark have?", "expected_policy": "general_info"},
    {"question": "What should I do if I lose an item at the parking facility?", "expected_policy": "general_info"},
    {"question": "Does SkyPark have CCTV surveillance?", "expected_policy": "general_info"},
    # working_hours_pricing
    {"question": "What are SkyPark's working hours?", "expected_policy": "working_hours_pricing"},
    {"question": "How much does it cost to park a motorcycle per hour?", "expected_policy": "working_hours_pricing"},
    {"question": "Is the administrative office open on Sundays?", "expected_policy": "working_hours_pricing"},
    # locations
    {"question": "Which zone has EV charging spots?", "expected_policy": "locations"},
    {"question": "What floor is Zone D on?", "expected_policy": "locations"},
    {"question": "How are parking spots labeled at SkyPark?", "expected_policy": "locations"},
    # booking_process
    {"question": "How do I reserve a parking space?", "expected_policy": "booking_process"},
    {"question": "What happens if I don't arrive within 30 minutes of my reservation start time?", "expected_policy": "booking_process"},
    {"question": "Can I get a monthly parking pass?", "expected_policy": "booking_process"},
    # rules_and_guidelines
    {"question": "What is the speed limit inside the facility?", "expected_policy": "rules_and_guidelines"},
    {"question": "Is smoking allowed in the parking facility?", "expected_policy": "rules_and_guidelines"},
    {"question": "What is the maximum vehicle height allowed?", "expected_policy": "rules_and_guidelines"},
    {"question": "Will SkyPark share my personal information with third parties?", "expected_policy": "rules_and_guidelines"},
]