import os


def get_retrofile_name(channel_id):
    return "ch_" + str(channel_id) + ".txt"


def is_file_exists(filename):
    try:
        f = open(filename, 'r')
        f.close()
    except FileNotFoundError:
        return False
    return True


def get_file_content(filename):
    if is_file_exists(filename):
        with open(filename, "r") as f:
            file_content = f.read()
        return file_content
    else:
        return None


def remove_file(filename):
    if is_file_exists(filename):
        os.remove(filename)
        return True
    else:
        return False


def add_content_to_file(content, filename):
    with open(filename, "a") as f:
        f.write(content)
    return content
