import time
from random import shuffle
from pylsl import StreamInfo, StreamOutlet, cf_string

def main():
    # 1. Set up the Stream Information
    # Name, Type, Channel Count, Sampling Rate (0 = irregular), Data Format, Unique ID
    info = StreamInfo(
        name='MyMarkerStream', 
        type='Markers', 
        channel_count=1, 
        nominal_srate=0, 
        channel_format=cf_string, 
        source_id='marker_sender_id_1223'
    )

    # 2. Create the Stream Outlet
    outlet = StreamOutlet(info)
    
    print("Publishing to Marker stream... Press Ctrl+C to stop.")

    try:
        # 3. Enter the publishing loop
        while True:
            # LSL expects data as a list, even for a single channel
            marker = ['lol']
            shuffle(marker)  # Shuffle the marker values
            outlet.push_sample(marker)
            
            # Optional: Print to console to verify it's running
            print(f"Published: {marker[0]}")
            
            # Sleep for 250 ms (0.25 seconds)
            time.sleep(0.25)
            
    except KeyboardInterrupt:
        print("\nPublishing stopped by user.")

if __name__ == '__main__':
    main()