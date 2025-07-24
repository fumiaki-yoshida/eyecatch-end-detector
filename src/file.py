import glob

def get_files(path:str) -> list[str]:
    filelist = glob.glob(path + '/**/*', recursive=True)
    return filelist
