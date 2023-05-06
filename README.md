# ID-Card-Based-Attendance-System

Python code for a barcode-based attendance system using OpenCV and the pyzbar library. 
The code captures the video stream from the default camera, detects barcodes in the video stream, and decodes the barcode data using the pyzbar library.
It then displays the barcode data on the screen along with two options for the user to select 'in_time' or 'out_time'.
Once the user selects an option, the system sends an HTTP request to an API endpoint, 
with the barcode data, and the timestamp of the selected option (in_time or out_time).
If the barcode is not already present in the API database for the current date and has no 'out_time' entry, 
the system adds the entry with the selected timestamp.
If the barcode is already present and has an 'in_time' entry, the system adds an 'out_time' entry with the selected timestamp.
The code uses multi-processing to handle HTTP requests asynchronously. The attendance details are logged to a text file named 'logging.txt'.
