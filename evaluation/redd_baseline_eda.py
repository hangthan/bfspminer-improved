import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

# ==========================================
# 1. KHÁM PHÁ DỮ LIỆU (EDA)
# ==========================================
def perform_eda(sequences):
    """
    Thực hiện EDA cho dữ liệu chuỗi.
    Input: sequences (List of lists) - Ví dụ: [['Fridge', 'Lighting'], ['Fridge', 'Microwave'], ...]
    """
    print("--- BÁO CÁO EXPLORATORY DATA ANALYSIS (EDA) ---")
    
    # Làm phẳng danh sách các sự kiện để đếm
    all_events = [item for seq in sequences for item in seq]
    total_events = len(all_events)
    unique_items = set(all_events)
    
    print(f"Tổng số sự kiện (events): {total_events}")
    print(f"Tổng số thiết bị duy nhất (unique items): {len(unique_items)}")
    
    # Đếm tần suất
    item_counts = Counter(all_events)
    
    # Hiển thị Top 5 thiết bị
    print("\nTop 5 thiết bị xuất hiện nhiều nhất:")
    for item, count in item_counts.most_common(5):
        print(f" - Thiết bị '{item}': {count} lần ({count/total_events:.2%})")
        
    # Trực quan hóa Bar chart
    items, counts = zip(*item_counts.most_common(20))
    plt.figure(figsize=(10, 6))
    sns.barplot(x=list(counts), y=list(items), palette="viridis")
    plt.title("Tần suất xuất hiện của các thiết bị trong dữ liệu", fontsize=14, pad=15)
    plt.xlabel("Số lần xuất hiện", fontsize=12)
    plt.ylabel("Thiết bị", fontsize=12)
    os.makedirs('evaluation/results/charts', exist_ok=True)
    plt.savefig(f'evaluation/results/charts/eda_{dataset_name}.png', dpi=300)
    plt.close()
    print(f"Đã lưu biểu đồ tại evaluation/results/charts/eda_{dataset_name}.png")

# ==========================================
# 2. TÍNH TOÁN BASELINE (MAJORITY & RANDOM)
# ==========================================
def calculate_baselines(train_sequences, test_ground_truth_list):
    """
    Tính Precision@3 cho Majority Predictor và Random Predictor.
    - train_sequences: Tập huấn luyện (dùng để tìm ra 3 thiết bị chiếm đa số).
    - test_ground_truth_list: Tập nhãn thực tế cần dự đoán trong tập Test.
    """
    # 1. Tìm Top 3 thiết bị xuất hiện nhiều nhất từ tập Train
    train_events = [item for seq in train_sequences for item in seq]
    total_appliances = len(set(train_events))
    
    counts = Counter(train_events)
    top_3_majority = [item[0] for item in counts.most_common(3)]
    
    print(f"\n--- KẾT QUẢ BASELINE (Precision@3) ---")
    print(f"Mô hình Majority Predictor sẽ luôn đưa ra dự đoán: {top_3_majority}")
    
    majority_hits = 0
    total_tests = len(test_ground_truth_list)
    
    if total_tests == 0:
        print("Tập test rỗng!")
        return
        
    # 2. Đánh giá độ chính xác trên tập Test
    for ground_truth in test_ground_truth_list:
        # Số lượng đoán đúng = Số lượng thiết bị vừa nằm trong top_3 vừa nằm trong ground_truth
        correct_majority = len(set(top_3_majority) & set(ground_truth))
        
        # Công thức Precision@k = Số lượng đúng / k (ở đây k=3)
        majority_hits += (correct_majority / 3.0)
        
    # Tính trung bình Precision@3
    majority_precision_3 = majority_hits / total_tests
    
    # Đối với Random Predictor: Chọn bừa 3 thiết bị từ tổng số thiết bị
    random_precision_3 = 3.0 / total_appliances if total_appliances > 0 else 0
    
    print("-" * 40)
    print(f"1. Random Predictor Precision@3   : {random_precision_3:.2%}")
    print(f"2. Majority Predictor Precision@3 : {majority_precision_3:.2%}")
    print("-" * 40)
    
    return majority_precision_3, random_precision_3

# ==========================================
# 3. CHẠY THỬ NGHIỆM VỚI DỮ LIỆU THỰC TẾ
# ==========================================
if __name__ == "__main__":
    import os
    import sys
    
    file_path = "data/redd_full_sequence.txt"
    dataset_name = "redd"
    
    if len(sys.argv) > 1:
        if sys.argv[1].lower() == "msnbc":
            file_path = "data/msnbc_sequence.txt"
            dataset_name = "msnbc"
            
    if not os.path.exists(file_path):
        print(f"File {file_path} không tồn tại!")
        exit(1)
        
    print(f"Đang tải dữ liệu từ {file_path}...")
    stream = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            items = line.strip().split()
            if items:
                event = "|".join(items)
                stream.append([event])  # wrap in list to match perform_eda expected format
                
    print("\nTHỰC THI EDA TẬP DỮ LIỆU:")
    perform_eda(stream)
    
    # ---------------------------------------------
    # TÍNH TOÁN ONLINE BASELINE HIT RATE 
    # (Khớp với logic test trong run_experiments.py)
    # ---------------------------------------------
    print("\nTHỰC THI TÍNH BASELINE HIT RATE (ONLINE STREAM)...")
    
    # Simulate the online streaming evaluation
    hits_majority = 0
    hits_random = 0
    total_preds = 0
    
    # Warmup and test
    from collections import Counter
    import random
    
    history_counter = Counter()
    
    for i, seq in enumerate(stream):
        item = seq[0]
        
        # Đánh giá mỗi 500 items giống BFSPMiner
        if i > 1000 and i % 500 == 0:
            total_preds += 1
            
            # Majority Predictor: Lấy 3 item xuất hiện nhiều nhất trong lịch sử
            top_3 = [x[0] for x in history_counter.most_common(3)]
            if item in top_3:
                hits_majority += 1
                
            # Random Predictor: Lấy ngẫu nhiên 3 item từ vocabulary
            vocab = list(history_counter.keys())
            if len(vocab) >= 3:
                rand_3 = random.sample(vocab, 3)
            else:
                rand_3 = vocab
            if item in rand_3:
                hits_random += 1
                
        # Cập nhật lịch sử sau khi dự đoán
        history_counter[item] += 1
        
    majority_hit_rate = (hits_majority / total_preds) * 100 if total_preds > 0 else 0
    random_hit_rate = (hits_random / total_preds) * 100 if total_preds > 0 else 0
    
    print("-" * 50)
    print(f"Tổng số lượt test (cứ mỗi 500 items): {total_preds}")
    print(f"1. Random Predictor Hit Rate   : {random_hit_rate:.2f}%")
    print(f"2. Majority Predictor Hit Rate : {majority_hit_rate:.2f}%")
    print("-" * 50)

