from datetime import datetime, timezone

def get_last_run_time(file_path: str = "last_run.txt") -> datetime:
    try:
        with open(file_path, 'r') as f:
            last_run_time_str = f.read().strip()
            return datetime.fromisoformat(last_run_time_str)
    except FileNotFoundError:
        return datetime.min.replace(tzinfo=timezone.utc)
    except ValueError:
        print(f"Invalid date format in {file_path}.")
        return datetime.min.replace(tzinfo=timezone.utc)

def save_current_run_time(file_path: str = "last_run.txt"):
    with open(file_path, 'w') as f:
        f.write(datetime.now(timezone.utc).isoformat())
    print(f"Saved current run time to {file_path}.")

def filter_new_entries(entries: list[tuple[str, str]], last_run_time: datetime) -> list[tuple[str, str]]:
    new_entries = []
    for url, lastmod in entries:
        try:
            lastmod_date = datetime.fromisoformat(lastmod)
            if lastmod_date > last_run_time:
                new_entries.append((url, lastmod))
        except ValueError:
            print(f"Invalid date format for URL {url}: {lastmod}")
            pass
    return new_entries

def get_latest_entries(entries: list[tuple[str, str]], top_n: int = 1) -> list[tuple[str, str]]:
    valid_entries = []
    for url, lastmod in entries:
        try:
            lastmod_date = datetime.fromisoformat(lastmod)
            valid_entries.append((url, lastmod_date))
        except ValueError:
            print(f"Invalid date format for URL {url}: {lastmod}")
            pass

    return sorted(valid_entries, key=lambda x: x[1], reverse=True)[:top_n]
