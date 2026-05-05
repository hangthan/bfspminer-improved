import os
import csv
from collections import Counter

def perform_eda(csv_path="data/redd_house1_0.csv", txt_path="data/redd_sequence.txt"):
    print("="*60)
    print(" Exploratory Data Analysis: REDD Dataset ")
    print("="*60)
    
    # 1. Analyze original CSV if it exists
    if os.path.exists(csv_path):
        print(f"\n[*] Analyzing raw CSV: {csv_path}")
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            header = next(reader)
            print(f"Columns: {header}")
            
            row_count = 0
            active_counts = {col.strip().replace(' ', '_').lower(): 0 for col in header[1:]}
            
            for row in reader:
                if not row: continue
                row_count += 1
                for i, val_str in enumerate(row[1:]):
                    try:
                        if float(val_str) > 30.0:
                            active_counts[header[i+1].strip().replace(' ', '_').lower()] += 1
                    except ValueError:
                        pass
                        
        print(f"Total records: {row_count}")
        print("\nActive Time Percentage (Threshold > 30W):")
        for col, active_count in active_counts.items():
            pct = (active_count / row_count) * 100 if row_count > 0 else 0
            print(f"  - {col:25}: {active_count:6} records ({pct:5.2f}%)")
    else:
        print(f"\n[-] CSV not found at {csv_path}")

    # 2. Analyze processed sequence
    if os.path.exists(txt_path):
        print(f"\n[*] Analyzing processed stream: {txt_path}")
        with open(txt_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        events = [line.strip() for line in lines if line.strip()]
        print(f"Total discrete events (timesteps): {len(events)}")
        
        event_counter = Counter(events)
        
        print("\nTop 10 Most Frequent Events:")
        for event, count in event_counter.most_common(10):
            print(f"  - {event:30}: {count:6} ({count/len(events)*100:5.2f}%)")
            
        # Co-occurrences
        lengths = [len(e.split()) for e in events]
        multi_device_events = sum(1 for l in lengths if l > 1)
        print(f"\nMulti-device events (co-occurrences): {multi_device_events} ({multi_device_events/len(events)*100:.2f}%)")
        
        # Analyze individual devices in the events
        all_devices = []
        for e in events:
            all_devices.extend(e.split())
        device_counter = Counter(all_devices)
        print("\nDevice Frequencies in Stream:")
        for dev, count in device_counter.most_common():
            print(f"  - {dev:25}: {count:6} ({count/len(events)*100:5.2f}% of events)")
            
        # Gap analysis for the second most frequent device (to show usefulness of gap mining)
        if len(device_counter) > 1:
            target_dev = device_counter.most_common(2)[1][0] # 2nd most common
            print(f"\nGap analysis for '{target_dev}':")
            indices = [i for i, e in enumerate(events) if target_dev in e.split()]
            if len(indices) > 1:
                gaps = [indices[i] - indices[i-1] - 1 for i in range(1, len(indices))]
                avg_gap = sum(gaps) / len(gaps)
                max_gap = max(gaps)
                print(f"  - Avg gap between uses : {avg_gap:.2f} events")
                print(f"  - Max gap              : {max_gap} events")
                print(f"  - Times gap > 0        : {sum(1 for g in gaps if g > 0)}")
                print(f"  - Times gap > 2        : {sum(1 for g in gaps if g > 2)}")
        
    else:
        print(f"\n[-] Sequence TXT not found at {txt_path}")

if __name__ == "__main__":
    perform_eda()
