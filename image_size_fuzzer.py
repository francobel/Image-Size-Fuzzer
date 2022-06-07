import os
import glob
import mmap
import pykd

# The goal of this program is to edit the dimensions on an image within its header.
# The height and width will be edited iteratively ranging from 0x0000 - 0xFFFF
# This is done to crash an image processing program that parses this image. 
# After a program crash, a dump file is created.The dump file is then analyzed and 
# the location that the program wrongfully tried to write to due to a buffer overflow 
# is extracted. This information is the written to a file.

# Note: The start and end image sizes are hard coded along with their 
#       locations within the image header. You might need to edit these 
#       manually to accomplish your goal. Another hardcoded piece of 
#       data you will have to edit is the executable that will be processing your image.
if __name__ == '__main__':

    # Retrieve information from the user
    folder_path = input('Enter folder containing dump files: ') # C:\\Users\\User\\Desktop\\dumps\\*
    image_name = input('Enter image we will be modifying: ') # image.jpg
    step_size = input('Enter the image dimension step size (min 1): ') # 100

    with open(image_name, 'r+b') as image:

        # Iterate over range of width and heights
        for a in range(0x0000, 0xffff, int(step_size)):
            for b in range(0x0000, 0xffff, int(step_size)):

                # Edit image header to alter width and height
                mm = mmap.mmap(image.fileno(), 0)
                mm.seek(92)
                mm.write(a.to_bytes(2, 'big'))
                mm.seek(94)
                mm.write(b.to_bytes(2, 'big'))

                # Run program that your image will crash
                os.system('image_processor.exe input.jpg output.jpg')

                # Select the most recent dump file in the folder
                files = glob.glob(folder_path)
                newest_file = max(files, key=os.path.getctime)
                print(newest_file)

                # Write address is extracted from windows dump file
                pykd.loadDump(newest_file)
                write_address = pykd.dbgCommand(".exr -1").split()[-1]

                # Print information
                dimensions = hex(a) + ", " + hex(b) + ": "
                info = dimensions + "Attempt to write at address: " + write_address
                print(info)

                # Write information to file
                ouput = open("output.txt", "a")
                ouput.write(info + "\n")
                ouput.close()
