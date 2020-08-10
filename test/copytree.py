import os
import shutil
def cp(source_path, target_path):
    for file in os.listdir(source_path):
        source_file = os.path.join(source_path, file)
        target_file = os.path.join(target_path, file)
        if os.path.isfile(source_file):
            #print('{0} is file'.format(source_file))
            shutil.copyfile(source_file, target_file)
        else:
            #print('{0} is dir'.format(source_file))
            shutil.copytree(source_file, target_file)
    return


cp('/Users/sengled-mac/workspace/test', '/Users/sengled-mac/workspace/test1')