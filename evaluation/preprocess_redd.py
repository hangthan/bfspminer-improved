import os
import csv
import logging
import glob
from typing import List, Optional

logger = logging.getLogger(__name__)

def preprocess_redd(input_path: str, output_path: str, threshold: float = 30.0, ignore_devices: Optional[List[str]] = None) -> bool:
    """
    Reads the REDD dataset (CSV format), extracts active devices per timestamp,
    and writes them as a discrete event sequence to a text file.
    If input_path is a directory, it processes all CSV files inside it and merges.
    """
    if ignore_devices is None:
        ignore_devices = ['main', 'mains', '']
        
    if not os.path.exists(input_path):
        logger.error(f"REDD dataset not found at {input_path}")
        return False

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    if os.path.isdir(input_path):
        csv_files = sorted(glob.glob(os.path.join(input_path, "*.csv")))
    else:
        csv_files = [input_path]
        
    if not csv_files:
        logger.error(f"No CSV files found in {input_path}")
        return False
        
    logger.info(f"Preprocessing {len(csv_files)} files to {output_path} (Threshold: {threshold}W, Ignore: {ignore_devices})...")
    
    total_sequence_count = 0
    with open(output_path, 'w', encoding='utf-8') as f_out:
        for file in csv_files:
            logger.info(f"  -> Processing {os.path.basename(file)}...")
            with open(file, 'r', encoding='utf-8-sig') as f_in:
                reader = csv.reader(f_in)
                try:
                    header = next(reader)
                except StopIteration:
                    continue
                    
                devices = [col.strip().replace(' ', '_').lower() for col in header[1:]]
                
                for row in reader:
                    if not row:
                        continue
                        
                    active_devices = []
                    for i, val_str in enumerate(row[1:]):
                        if i >= len(devices):
                            continue
                        device_name = devices[i]
                        if device_name in ignore_devices:
                            continue
                            
                        try:
                            val = float(val_str)
                            if val > threshold:
                                active_devices.append(device_name)
                        except ValueError:
                            pass
                    
                    if active_devices:
                        active_devices.sort()
                        f_out.write(" ".join(active_devices) + "\n")
                        total_sequence_count += 1
                        
    logger.info(f"Preprocess successful! Generated {total_sequence_count} events total.")
    return True

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    if os.path.isdir("data/redd"):
        input_csv = "data/redd"
        output_txt = "data/redd_full_sequence.txt"
    else:
        input_csv = "data/redd_house1_0.csv"
        output_txt = "data/redd_sequence.txt"
    preprocess_redd(input_csv, output_txt, threshold=30.0)
