import os


def init(storage_dir_name='storage'):
    cwd = os.getcwd()
    storage_path = os.path.join(cwd, storage_dir_name)

    if not os.path.exists(storage_path):
        try:
            os.makedirs(storage_path)
            print(f"Storage directory created: {storage_path}")
        except OSError as e:
            print(f"Error creating directory: {e}")
            return None, None
        
    return storage_dir_name, storage_path