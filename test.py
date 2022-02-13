from Coordinator.main import call_coordinator

# return info_str, len(urls_all), len(urls_todo), len(keys_done), len(keys_forfeit), len(keys_error)
tmp= call_coordinator(info_only=True, batch=1, total_batches=2)
print(tmp[0])