import os
from collections import defaultdict


def get_file_info(filename):
    # Ensure the file has the .txt extension
    if not filename.endswith('.txt'):
        return None, None

    # Remove the .txt extension
    filename = filename[:-4]

    # Split filename from the end to get the timestamp
    parts = filename.rsplit('-', 1)
    if len(parts) != 2 or not parts[1].isdigit():
        return None, None
    return parts[0], int(parts[1])


def delete_smaller_duplicate(files_info, current_dir):
    for filename, timestamps in files_info.items():
        # If we have more than one version of the file
        if len(timestamps) > 1:
            timestamps.sort()

            for i in range(len(timestamps) - 1):
                file1_path = os.path.join(current_dir, f"{filename}-{timestamps[i]}.txt")
                file2_path = os.path.join(current_dir, f"{filename}-{timestamps[i + 1]}.txt")

                # Check file size difference
                size_diff = abs(os.path.getsize(file1_path) - os.path.getsize(file2_path))

                # If the size difference is less than 1KB
                if size_diff < 1024:
                    os.remove(file1_path)
                    print(f"Deleted: {file1_path}")
                    break  # Break after deleting one to avoid unnecessary deletions


if __name__ == "__main__":
    target_dir = os.path.expanduser('~/Library/CloudStorage/OneDrive-123/文件/resources/p_toplist')

    # Check if the provided directory path exists
    if os.path.isdir(target_dir):
        os.chdir(target_dir)
    else:
        print("Directory not found. Exiting...")
        exit()

    current_dir = os.getcwd()
    files = os.listdir(current_dir)

    # Store files with their timestamp {filename: [timestamps]}
    files_info = defaultdict(list)

    # Filter the files by the given format and store in the dictionary
    for file in files:
        if file == '.DS_Store':
            continue  # Skip the .DS_Store file
        name, timestamp = get_file_info(file)
        if name and timestamp:
            files_info[name].append(timestamp)

    delete_smaller_duplicate(files_info, current_dir)
