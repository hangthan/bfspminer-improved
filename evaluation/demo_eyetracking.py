import sys
import os
import argparse
import subprocess

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    parser = argparse.ArgumentParser(description="Run EyeTracking Demo")
    args = parser.parse_args()
    
    print("="*80)
    print(" 🚀 BFSPMiner Demo on EyeTracking Dataset ")
    print("="*80)
    
    # Delegate to compare_baseline script
    script_path = os.path.join(os.path.dirname(__file__), "compare_baseline.py")
    cmd = [sys.executable, script_path, "--dataset", "eyetracking"]
    subprocess.run(cmd)

if __name__ == "__main__":
    main()
