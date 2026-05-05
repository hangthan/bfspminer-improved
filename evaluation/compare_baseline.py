import sys
import os
import time

# Add root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.bfspminer import BFSPMiner
import subprocess

def print_header(title):
    print("\n" + "="*70)
    print(f" {title:^68} ")
    print("="*70)

def evaluate_on_toy_data():
    print_header("PYTHON BFSPMINER IMPROVED (OPTIMIZED)")
    miner = BFSPMiner(max_pattern_length=5, pruning=False)
    
    stream = ['a', 'b', 'c', 'a', 'b', 'd', 'a', 'b', 'c', 'e', 'a', 'b']
    
    print(f"[*] Processing Toy Stream (Length: {len(stream)})")
    start_time = time.time()
    for item in stream:
        miner.feed_item(item)
    
    patterns = miner.get_frequent_patterns(min_support=0.1)
    end_time = time.time()
    
    print(f"[*] Time Taken: {end_time - start_time:.4f}s")
    print(f"[*] Total Frequent Patterns Found: {len(patterns)}")
    
    print("\n" + "-"*70)
    print(f"{'No.':<5} | {'Pattern':<20} | {'Support':<10} | {'Count':<10}")
    print("-" * 70)
    for i, p in enumerate(patterns[:10], 1):
        pattern_str = "(" + ", ".join([f"'{x}'" for x in p['pattern']])
        if len(p['pattern']) == 1:
            pattern_str += ","
        pattern_str += ")"
        
        print(f"{i:<5} | {pattern_str:<20} | {p['support']:<10.3f} | {p['count']:<10}")
    print("-" * 70)
        
    print("\n[*] Next 3 Predictions (Context: 'a' -> 'b'):")
    preds = miner.predict_next(k=3)
    preds_str = "[" + ", ".join([f"'{x}'" for x in preds]) + "]"
    print(f"    => {preds_str}")
    print("=" * 70 + "\n")
    
    
    print_header("COMPILING JAVA BASELINE")
    java_src_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                "reference", "BFSPMiner-java", "BFSPMiner", "src", "main", "java"))
    eval_dir = os.path.normpath(os.path.dirname(os.path.abspath(__file__)))
    test_runner_path = os.path.normpath(os.path.join(eval_dir, "TestRunner.java"))
    
    # We compile the Java TestRunner along with the needed algorithm and model files
    compile_cmd = f'javac -cp "{java_src_dir}" -d "{eval_dir}" "{test_runner_path}" "{java_src_dir}/algorithm/BFSPMiner.java" "{java_src_dir}/algorithm/PatternBuilder.java" "{java_src_dir}/algorithm/Predictor.java" "{java_src_dir}/model/TreeObject.java" "{java_src_dir}/model/StatusObject.java" "{java_src_dir}/model/PatternObject.java" "{java_src_dir}/model/TreeObjectList.java" "{java_src_dir}/utils/PatternMetrics.java" "{java_src_dir}/utils/Util.java"'
    # Ensure forward slashes for cross platform compatibility inside quotes or normalize them.
    compile_cmd = compile_cmd.replace("\\", "/")
    
    try:
        print("[*] Compiling TestRunner and Baseline sources (this may take a few seconds)...")
        compile_result = subprocess.run(compile_cmd, shell=True, capture_output=True, text=True)
        if compile_result.returncode != 0:
            print("[-] Compilation failed!")
            print(compile_result.stderr)
            return
            
        print("[+] Compilation Successful.")
        run_cmd = f'java -cp "{eval_dir}" TestRunner'
        result = subprocess.run(run_cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print("[-] Running Java failed!")
            print(result.stderr)
        else:
            print(result.stdout)
    except Exception as e:
        print(f"[-] Failed to run Java baseline. Error: {e}")

if __name__ == "__main__":
    evaluate_on_toy_data()
