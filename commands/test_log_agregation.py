from telemetry_logs import calculate_log_agregates

LOG_NAME = '2024-07-21T02:04:30.147284.log'
START = 1721509472
END = 1721522829

def test_calculate_log_agregates():
    result = calculate_log_agregates(LOG_NAME, START, END)
    print('Records', result.total_records)
    print('Human watt hours', result.total_human_watt_hours)
    print('Motor watt hours', result.total_motor_watt_hours)
    print('Regen watt hours', result.total_regen_watt_hours)
