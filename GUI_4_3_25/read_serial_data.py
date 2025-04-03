from datetime import datetime

def read_serial_data(ser, pin, csv_writer_sensor):
    # Read data from the serial port and write to CSV
    pin.on()
    value = ser.readline()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    pin.off()

    # Check if we have data
    if value:
        try:
            value_in_string = value.decode('UTF-8', errors='ignore') 
        except UnicodeDecodeError as e:
            print(f"Error decoding data: {e}")
            value_in_string = "Error decoding"  
    else:
        value_in_string = "No data" 
    
    # Split the values based on the comma and space
    #print("Received data:", value_in_string)
    values = value_in_string.split(", ")
    extracted_values = [timestamp]
    
    # Iterate over the values and extract the necessary data (assuming 'key: value' format)
    for value in values:
        if ': ' in value:
            try:
                key, val = value.split(": ")
                extracted_values.append(val.strip())  # Store the extracted value
            except ValueError:
                print(f"Error splitting value: {value}")
    
    #print("Extracted values:", extracted_values) 

    # Check if the number of extracted values matches the expected columns
    if len(extracted_values) == 8: 
        csv_writer_sensor.writerow(extracted_values)
    else:
        print(f"Error: Incorrect number of extracted values. Expected 8, got {len(extracted_values)}.")