# 🎓 Hướng dẫn Demo — BFSPMiner-Improved

> **Môn học:** Khai phá Dữ liệu (Data Mining) — Chương trình Thạc sĩ  
> **Đề tài:** Cải tiến thuật toán BFSPMiner cho khai phá mẫu tuần tự trên luồng dữ liệu  
> **Bài báo gốc:** *BFSPMiner: An Effective and Efficient Batch-Free Algorithm for Mining Sequential Patterns over Data Streams*

---

## Mục lục

1. [Yêu cầu Hệ thống](#1-yêu-cầu-hệ-thống)
2. [Demo 1: Chạy Toy Stream (Cơ bản)](#2-demo-1-chạy-toy-stream-cơ-bản)
3. [Demo 2: Đối chiếu Python vs Java Baseline](#3-demo-2-đối-chiếu-python-vs-java-baseline)
4. [Demo 3: Chạy Full Benchmark Suite](#4-demo-3-chạy-full-benchmark-suite)
5. [Demo 4: Trực quan hóa Kết quả](#5-demo-4-trực-quan-hóa-kết-quả)
6. [Demo 5: Unit Testing](#6-demo-5-unit-testing)
7. [Demo 6: Minh họa từng bước thuật toán (Interactive)](#7-demo-6-minh-họa-từng-bước-thuật-toán-interactive)
8. [Tóm tắt Kết quả Chính](#8-tóm-tắt-kết-quả-chính)
9. [Cấu trúc Source Code](#9-cấu-trúc-source-code)

---

## 1. Yêu cầu Hệ thống

### Phần mềm cần cài đặt

| Yêu cầu       | Phiên bản tối thiểu | Ghi chú                        |
|----------------|----------------------|--------------------------------|
| **Python**     | 3.9+                 | Khuyến nghị 3.10 hoặc 3.11    |
| **pip**        | 21.0+                | Đi kèm Python                 |
| **Java JDK**   | 8+                   | Chỉ cần cho Demo 2 (đối chiếu)|
| **Git**        | 2.x                  | Để clone repository            |

### Cài đặt thư viện Python

```bash
pip install -r requirements.txt
```

Nội dung file `requirements.txt`:

```
psutil==5.9.8
pytest==8.0.0
numpy==1.26.4
pandas==2.2.0
tqdm==4.66.2
```

> **Lưu ý:** Để sinh biểu đồ (Demo 4), cần thêm `matplotlib`. Cài bổ sung:
> ```bash
> pip install matplotlib
> ```

### Kiểm tra nhanh

```bash
python -c "from core.bfspminer import BFSPMiner; print('OK — BFSPMiner sẵn sàng!')"
```

---

## 2. Demo 1: Chạy Toy Stream (Cơ bản)

### Mục tiêu
Chạy nhanh một **luồng dữ liệu mẫu nhỏ** (9 sự kiện) để minh họa toàn bộ pipeline của BFSPMiner-Improved: nhận sự kiện → xây dựng cây Inverted T₀ → trích xuất mẫu phổ biến → dự đoán sự kiện tiếp theo.

### Lệnh chạy

```bash
python main.py
```

### Giải thích chi tiết

Script sẽ thực hiện các bước sau:

1. **Khởi tạo BFSPMiner** với cả 2 tính năng cải tiến được **bật**:
   - ✅ `enable_adaptive=True` — Tự động điều chỉnh `max_pattern_length` theo entropy dữ liệu
   - ✅ `enable_gap=True` — Cho phép khai phá mẫu tuần tự có khoảng cách (non-consecutive patterns)
   - `max_pattern_length=5`, `max_gap=2`, `window_size=5`

2. **Đưa vào luồng dữ liệu mẫu** gồm 9 sự kiện mô phỏng hành vi người dùng:
   ```
   ['click', 'view', 'add_to_cart', 'click', 'scroll', 'add_to_cart', 'click', 'view', 'purchase']
   ```

3. **Trích xuất mẫu phổ biến** với `min_support=0.1` (tối thiểu xuất hiện 10% tổng sự kiện)

4. **Dự đoán 2 sự kiện tiếp theo** dựa trên context hiện tại bằng confidence score

### Output mẫu

```
Initializing BFSPMiner with Adaptive Length and Episode Gap Extension...
Processing toy stream of 9 events...

Found 15 frequent patterns (including patterns with gaps).

Top 5 Patterns:
Pattern: ('click',) | Count: 3 | Support: 0.33 | Confidence: 0.00
Pattern: ('add_to_cart',) | Count: 2 | Support: 0.22 | Confidence: 0.00
Pattern: ('view',) | Count: 2 | Support: 0.22 | Confidence: 0.00
Pattern: ('click', 'view') | Count: 2 | Support: 0.22 | Confidence: 0.67
Pattern: ('click', 'add_to_cart') | Count: 2 | Support: 0.22 | Confidence: 0.67

Predicting next 2 events after current context:
['click', 'view']
```

### Điểm nhấn khi trình bày

- **Pattern `('click', 'view')`**: Xuất hiện 2 lần trong luồng → `Support = 2/9 ≈ 0.22`
- **Confidence** cho biết xác suất `view` xảy ra ngay sau `click` = `Count(click→view) / Count(click) = 2/3 ≈ 0.67`
- Nhờ **Episode Gap Extension**, các mẫu như `('click', 'add_to_cart')` cũng được phát hiện dù giữa 2 sự kiện có sự kiện khác xen vào

---

## 3. Demo 2: Đối chiếu Python vs Java Baseline

### Mục tiêu
Chứng minh tính **chính xác** của bản Python Improved bằng cách đối chiếu trực tiếp kết quả với bản Java gốc trên cùng dữ liệu — đảm bảo **100% khớp** về pattern count và support values.

### Lệnh chạy

```bash
# Đối chiếu trên bộ dữ liệu REDD (IoT - tiêu thụ điện năng)
python main.py --compare --dataset redd

# Đối chiếu trên bộ dữ liệu MSNBC (Clickstream - hành vi web)
python main.py --compare --dataset msnbc
```

### Điều kiện tiên quyết

- File dữ liệu đã được tiền xử lý sẵn:
  - `data/redd_full_sequence.txt` — Chuỗi sự kiện IoT từ bộ REDD
  - `data/msnbc_sequence.txt` — Chuỗi clickstream từ bộ MSNBC
- Java Baseline đã được biên dịch (tự động qua `rebuild_jar.bat`)

### Giải thích

Hệ thống sẽ:
1. Chạy bản **Python Improved** (tắt Adaptive + Gap để so sánh công bằng) trên cùng luồng dữ liệu
2. Gọi bản **Java gốc** qua subprocess
3. So sánh từng pattern: tên, count, support
4. In ra bảng tổng hợp kết quả

### Output mẫu (Toy Stream Verification)

```
======================================================================
                PYTHON BFSPMINER IMPROVED (OPTIMIZED)                 
======================================================================
[*] Processing Toy Stream (Length: 12)
[*] Time Taken: 0.0000s
[*] Total Frequent Patterns Found: 6

----------------------------------------------------------------------
No.   | Pattern              | Support    | Count     
----------------------------------------------------------------------
1     | ('a',)               | 0.333      | 4         
2     | ('b',)               | 0.333      | 4         
3     | ('a', 'b')           | 0.333      | 4         
4     | ('c',)               | 0.167      | 2         
5     | ('b', 'c')           | 0.167      | 2         
6     | ('a', 'b', 'c')      | 0.167      | 2         
----------------------------------------------------------------------

======================================================================
                  JAVA BFSPMINER BASELINE (ORIGINAL)
======================================================================
[*] Processing Toy Stream (Length: 12)
[*] Time Taken: 0.0230s
[*] Total Frequent Patterns Found: 6

----------------------------------------------------------------------
No.   | Pattern              | Support    | Count
----------------------------------------------------------------------
1     | ('a',)               | 0.333      | 4
2     | ('b',)               | 0.333      | 4
3     | ('a', 'b')           | 0.333      | 4
4     | ('c',)               | 0.167      | 2
5     | ('b', 'c')           | 0.167      | 2
6     | ('a', 'b', 'c')      | 0.167      | 2
----------------------------------------------------------------------
```

### Điểm nhấn khi trình bày

- **Kết quả 100% khớp** giữa Python và Java — cùng số pattern, cùng support, cùng count
- Bản Python nhanh hơn nhờ sử dụng **Dictionary (Hash Map)** thay vì **ArrayList** của Java → lookup O(1) thay vì O(N)
- Báo cáo đối chiếu chi tiết được lưu tại `evaluation/results/`

---

## 4. Demo 3: Chạy Full Benchmark Suite

### Mục tiêu
Chạy bộ **4 thí nghiệm** (Experiments) đánh giá toàn diện thuật toán trên dữ liệu thực tế.

### Lệnh chạy

```bash
# ⚡ Chạy nhanh (giới hạn 10,000 events — test nhanh khoảng 2-3 phút)
python main.py --run-experiments --dataset redd --limit 10000

# 🔥 Chạy đầy đủ trên REDD (457K events — khoảng 15-30 phút)
python main.py --run-experiments --dataset redd --full

# 🔥 Chạy đầy đủ trên MSNBC (424K events — khoảng 20-40 phút)  
python main.py --run-experiments --dataset msnbc --full
```

### Chi tiết 4 Thí nghiệm (Chuẩn hoá theo Báo cáo)

| Exp | Tên thí nghiệm | Tương ứng trong báo cáo | Mô tả |
|-----|-------------------------------|------------------------|---------------------------------------------------------------------------|
| 1 | **Overall Comparison** | Mục 5.3 | So sánh Random, Majority, Base và Improved trên toàn bộ dữ liệu |
| 2 | **Scalability** | Mục 5.4, 5.5, 5.7 | Đo số mẫu, Precision@3, runtime, memory theo các mốc (10K → 200K) |
| 3 | **Ablation (Adaptive)** | Mục 5.6.1 | So sánh Fixed-length (3, 5, 8, 12) vs Adaptive về bộ nhớ và số mẫu |
| 4 | **Ablation (Gap Impact)** | Mục 5.6.2 | Tác động của `max_gap` (0, 1, 2, 3, 5) đến Precision@3 và số lượng mẫu |

> **💡 Lưu ý quan trọng về thiết kế thí nghiệm (Python Base vs Java Base):**
> Trong toàn bộ 4 thí nghiệm đánh giá hiệu năng này, phiên bản **"Base"** được sử dụng để làm mốc so sánh là **Python Base** (thuật toán BFSPMiner code bằng Python nhưng tắt cấu hình `adaptive` và `gap`), chứ KHÔNG PHẢI bản Java. 
> - Việc so sánh **Python Improved vs Python Base** đảm bảo sự công bằng tuyệt đối về môi trường chạy (cùng chung cơ chế Garbage Collection và quản lý bộ nhớ của Python), giúp đo đạc chính xác lượng đỉnh RAM (peak memory) và Runtime chênh lệch do chính bản thân thuật toán.
> - Bản **Java Base** (bản gốc) chỉ được sử dụng duy nhất ở **Demo 2** để thực hiện đối chiếu chéo (cross-verification) nhằm chứng minh code Python đã biên dịch đúng 100% logic của thuật toán gốc.

### Kết quả đầu ra

- **Thư mục lưu trữ**: Mặc định lưu tại thư mục `results/` ở thư mục gốc của project (được sinh tự động).
- **Định dạng file**: Tất cả kết quả được xuất dưới dạng **JSON** để dễ dàng truy xuất và vẽ biểu đồ.
  - Ví dụ: `redd_exp1_overall.json`, `redd_exp2_scalability.json`
  - File tổng hợp: `all_experiments.json`

### Output mẫu khi chạy

```text
[*] Running Full Experiment Suite...

======================================================================
Exp1: Overall Comparison — REDD (457833 events)
======================================================================
  Running Naive-Random...
    -> HitRate = 40.48%
  Running Naive-Majority...
    -> HitRate = 81.51%
  Running BFSPMiner-Base...
    -> Patterns=105, HitRate=97.92%, Memory=22.4MB, Time=13.47s
  Running BFSPMiner-Improved...
    -> Patterns=203, HitRate=99.45%, Memory=40.3MB, Time=64.01s

======================================================================
Exp2: Scalability — REDD
======================================================================
  Stream size: 100000
    Base: 2.18s, 74 pats, 97.0%
    Imp:  10.14s, 136 pats, 100.0%
...
======================================================================
ALL EXPERIMENTS COMPLETE
======================================================================
```

---

## 5. Demo 4: Trực quan hóa Kết quả

### Mục tiêu
Tự động sinh các **biểu đồ chất lượng** (publication-quality) từ kết quả thí nghiệm đã chạy.

### Lệnh chạy

```bash
# Sinh biểu đồ từ kết quả standardized (JSON)
python evaluation/generate_figures.py

# Hoặc: Sinh biểu đồ từ CSV (evaluation suite cũ)
python evaluation/plot_results.py
```

### Các biểu đồ được sinh ra

Biểu đồ được lưu tại thư mục `figures/` (dạng PNG + PDF):

| File                            | Nội dung                                                  |
|---------------------------------|-----------------------------------------------------------|
| `fig_scalability_runtime.pdf`   | So sánh runtime Base vs Improved theo kích thước stream   |
| `fig_pattern_comparison.pdf`    | Số pattern phát hiện: Base vs Improved (cả REDD & MSNBC)  |
| `fig_adaptive_memory.pdf`       | Memory tiêu thụ: Fixed-length vs Adaptive                |
| `fig_gap_impact.pdf`            | Tác động của `max_gap` đến pattern count và Precision@3   |
| `fig_overall_comparison.pdf`    | So sánh tổng thể: Random vs Majority vs Base vs Improved |

### Giải thích từng biểu đồ

1. **Scalability Runtime** (Hình 1):
   - Trục X: Kích thước stream (x1000)
   - Trục Y: Thời gian chạy (giây)
   - Kết luận: Cả 2 phiên bản đều tăng tuyến tính, Improved chậm hơn do xử lý thêm gap + adaptive

2. **Pattern Comparison** (Hình 2):
   - Bar chart so sánh số pattern
   - Nhãn phần trăm `+93%`, `+90%` cho thấy Improved phát hiện được gần gấp đôi

3. **Adaptive Memory** (Hình 3):
   - Adaptive tiết kiệm RAM đáng kể so với Fixed-12 trên MSNBC (11.7 MB vs 200.5 MB)
   - Đặc biệt quan trọng cho dữ liệu entropy cao

4. **Gap Impact** (Hình 4):
   - Khi tăng `max_gap`, số pattern và Precision@3 đều tăng
   - Điểm bão hòa ở `max_gap=3` trên MSNBC

5. **Overall Comparison** (Hình 5):
   - Bar chart 4 methods: Random, Majority, Base, Improved
   - Improved vượt trội ở cả REDD (99.45%) và MSNBC (51.89%)

---

## 6. Demo 5: Unit Testing

### Mục tiêu
Xác minh tính đúng đắn logic của từng thành phần thuật toán thông qua **4 bộ test tự động**.

### Lệnh chạy

```bash
# Chạy toàn bộ test với output chi tiết
pytest tests/ -v
```

### Chi tiết các test case

| Test                          | File                   | Kiểm tra                                                         |
|-------------------------------|------------------------|-------------------------------------------------------------------|
| `test_basic_toy_stream`       | `test_toy_stream.py`   | Mining mẫu tuần tự cơ bản — pattern `('a','b')` phải có count=3  |
| `test_episode_mining_with_gaps` | `test_toy_stream.py` | Khai phá có gap — `('a','b')` qua `('a','x','b')` với `max_gap=1`|
| `test_adaptive_max_length`    | `test_toy_stream.py`   | `max_pattern_length` tự tăng khi dữ liệu entropy thấp            |
| `test_predictions`            | `test_toy_stream.py`   | Dự đoán đúng `'c'` sau context `('a','b')` với pattern `('a','b','c')` |

### Output kỳ vọng

```
========================== test session starts ==========================
platform win32 -- Python 3.11.x, pytest-8.0.0
collected 4 items

tests/test_toy_stream.py::test_basic_toy_stream PASSED             [ 25%]
tests/test_toy_stream.py::test_episode_mining_with_gaps PASSED     [ 50%]
tests/test_toy_stream.py::test_adaptive_max_length PASSED          [ 75%]
tests/test_toy_stream.py::test_predictions PASSED                  [100%]

========================== 4 passed in 0.15s ============================
```

### Điểm nhấn khi trình bày

- **4/4 PASSED** — Toàn bộ logic gốc và 2 extensions đều đúng
- Test `test_episode_mining_with_gaps` chứng minh khả năng phát hiện pattern qua khoảng cách
- Test `test_adaptive_max_length` chứng minh cơ chế tự điều chỉnh hoạt động đúng

---

## 7. Demo 6: Minh họa từng bước thuật toán (Interactive)

### Mục tiêu
Chạy thủ công từng bước để quan sát cây Inverted T₀ Tree **lớn dần** sau mỗi sự kiện — giúp hiểu rõ cơ chế hoạt động bên trong.

### Cách chạy

Mở **Python REPL** hoặc **Jupyter Notebook** và chạy đoạn code sau:

```python
from core.bfspminer import BFSPMiner

# Khởi tạo BFSPMiner (tắt adaptive + gap để dễ quan sát)
miner = BFSPMiner(max_pattern_length=3, pruning=False)

# Luồng dữ liệu mẫu
stream = ['a', 'b', 'a', 'b', 'c']

for i, item in enumerate(stream):
    miner.feed_item(item)
    patterns = miner.get_frequent_patterns(min_support=0.01)
    
    # Đếm số node trong cây
    def count_nodes(node):
        total = 1  # đếm node hiện tại
        for child in node.children.values():
            total += count_nodes(child)
        return total
    
    tree_nodes = count_nodes(miner.tree.head) - 1  # trừ root
    
    print(f"\n{'='*60}")
    print(f"Bước {i+1}: Thêm '{item}' vào luồng")
    print(f"{'='*60}")
    print(f"  Luồng hiện tại: {stream[:i+1]}")
    print(f"  Tổng items đã xử lý: {miner.processed_items}")
    print(f"  Số node trong cây: {tree_nodes}")
    print(f"  Số pattern phổ biến: {len(patterns)}")
    
    for p in patterns:
        print(f"    Pattern: {p['pattern']} | Count: {p['count']} | "
              f"Support: {p['support']:.3f} | Confidence: {p['confidence']:.3f}")
```

### Output kỳ vọng

```
============================================================
Bước 1: Thêm 'a' vào luồng
============================================================
  Luồng hiện tại: ['a']
  Tổng items đã xử lý: 1
  Số node trong cây: 1
  Số pattern phổ biến: 1
    Pattern: ('a',) | Count: 1 | Support: 1.000 | Confidence: 0.000

============================================================
Bước 2: Thêm 'b' vào luồng
============================================================
  Luồng hiện tại: ['a', 'b']
  Tổng items đã xử lý: 2
  Số node trong cây: 3
  Số pattern phổ biến: 3
    Pattern: ('a',) | Count: 1 | Support: 0.500 | Confidence: 0.000
    Pattern: ('b',) | Count: 1 | Support: 0.500 | Confidence: 0.000
    Pattern: ('a', 'b') | Count: 1 | Support: 0.500 | Confidence: 1.000

============================================================
Bước 3: Thêm 'a' vào luồng
============================================================
  Luồng hiện tại: ['a', 'b', 'a']
  Tổng items đã xử lý: 3
  Số node trong cây: 5
  Số pattern phổ biến: 5
    Pattern: ('a',) | Count: 2 | Support: 0.667 | Confidence: 0.000
    Pattern: ('b',) | Count: 1 | Support: 0.333 | Confidence: 0.000
    Pattern: ('a', 'b') | Count: 1 | Support: 0.333 | Confidence: 1.000
    Pattern: ('b', 'a') | Count: 1 | Support: 0.333 | Confidence: 1.000
    Pattern: ('a', 'b', 'a') | Count: 1 | Support: 0.333 | Confidence: 1.000

============================================================
Bước 4: Thêm 'b' vào luồng
============================================================
  Luồng hiện tại: ['a', 'b', 'a', 'b']
  Tổng items đã xử lý: 4
  Số node trong cây: 7
  Số pattern phổ biến: 7
    Pattern: ('a',) | Count: 2 | Support: 0.500 | Confidence: 0.000
    Pattern: ('b',) | Count: 2 | Support: 0.500 | Confidence: 0.000
    Pattern: ('a', 'b') | Count: 2 | Support: 0.500 | Confidence: 1.000
    Pattern: ('b', 'a') | Count: 1 | Support: 0.250 | Confidence: 0.500
    Pattern: ('a', 'b', 'a') | Count: 1 | Support: 0.250 | Confidence: 0.500
    Pattern: ('b', 'a', 'b') | Count: 1 | Support: 0.250 | Confidence: 1.000
    Pattern: ('a', 'b', 'a', 'b') | ... (cắt vì max_length=3)

============================================================
Bước 5: Thêm 'c' vào luồng
============================================================
  Luồng hiện tại: ['a', 'b', 'a', 'b', 'c']
  Tổng items đã xử lý: 5
  Số node trong cây: 10
  Số pattern phổ biến: 10+
    Pattern: ('a',) | Count: 2 | Support: 0.400 | Confidence: 0.000
    Pattern: ('b',) | Count: 2 | Support: 0.400 | Confidence: 0.000
    Pattern: ('a', 'b') | Count: 2 | Support: 0.400 | Confidence: 1.000
    Pattern: ('c',) | Count: 1 | Support: 0.200 | Confidence: 0.000
    Pattern: ('b', 'c') | Count: 1 | Support: 0.200 | Confidence: 0.500
    Pattern: ('a', 'b', 'c') | Count: 1 | Support: 0.200 | Confidence: 0.500
    ...
```

### Minh họa cấu trúc cây Inverted T₀ (sau bước 5)

```
                         [root]
                        /  |   \
                      a    b    c
                      |    |    |
                      b    a    b
                      |    |    |
                      a    b    a
```

> **Ghi chú:** Cây lưu theo thứ tự đảo ngược. Nhánh `root → b → a` tương ứng pattern `('a', 'b')`.
> Mỗi node lưu `count`, `batch_count`, `timestamps` để hỗ trợ pruning SSBE.

### Bonus: Thử nghiệm với Gap Extension

```python
# Bật Episode Gap Extension
miner_gap = BFSPMiner(max_pattern_length=3, pruning=False, enable_gap=True, max_gap=1, window_size=4)

stream_gap = ['a', 'x', 'b']
for item in stream_gap:
    miner_gap.feed_item(item)

patterns = miner_gap.get_frequent_patterns(min_support=0.01)
print("\nPatterns tìm được (với gap=1):")
for p in patterns:
    print(f"  {p['pattern']} | Count: {p['count']}")
# → Pattern ('a', 'b') được tìm thấy dù có 'x' xen giữa!
```

---

## 8. Tóm tắt Kết quả Chính

### 8.1. So sánh tổng thể: Baseline vs Improved

| Dataset | Stream Size | Base Patterns | Improved Patterns | Improvement | Base P@3  | Improved P@3 |
|---------|------------|---------------|-------------------|-------------|-----------|--------------|
| **REDD**    | 457,833    | 105           | 203               | **+93.3%**  | 97.92%    | **99.45%**   |
| **MSNBC**   | 423,776    | 523           | 996               | **+90.4%**  | 25.65%    | **51.89%**   |

> **Nhận xét:** Phiên bản Improved phát hiện gần **gấp đôi** số pattern so với Baseline, đồng thời cải thiện đáng kể Precision@3 (đặc biệt trên MSNBC: tăng từ 25.65% lên 51.89%).

### 8.2. Hiệu năng Runtime & Memory

| Dataset | Base Runtime | Imp Runtime | Base Memory | Imp Memory |
|---------|-------------|-------------|-------------|------------|
| **REDD**    | 13.47s      | 64.01s      | 22.35 MB    | 40.28 MB   |
| **MSNBC**   | 22.66s      | 76.65s      | 57.89 MB    | 53.10 MB   |

> **Trade-off:** Improved cần thêm thời gian xử lý (do gap generation + adaptive checking), nhưng đổi lại phát hiện được nhiều pattern hơn và dự đoán chính xác hơn. Đặc biệt, trên MSNBC, Improved thực sự **tiết kiệm RAM hơn** nhờ Adaptive tự giảm `max_pattern_length` khi entropy cao.

### 8.3. So sánh với các Baseline đơn giản

| Method          | REDD P@3 | MSNBC P@3 |
|-----------------|----------|-----------|
| Random Guess    | 40.48%   | 16.55%    |
| Majority Class  | 81.51%   | 49.53%    |
| BFSPMiner Base  | 97.92%   | 25.65%    |
| **BFSPMiner Improved** | **99.45%** | **51.89%** |

### 8.4. Tác động của Adaptive Length (trên MSNBC 100K)

| Chế độ      | Memory (MB) | Patterns | Ghi chú                            |
|-------------|-------------|----------|------------------------------------|
| Fixed-3     | 7.66        | 356      | Quá ngắn, bỏ lỡ pattern dài       |
| Fixed-5     | 21.89       | 525      | Cân bằng                           |
| Fixed-8     | 84.54       | 581      | Tốn RAM                            |
| Fixed-12    | 200.45      | 617      | Rất tốn RAM, ít pattern thêm       |
| **Adaptive** | **11.69**  | **361**  | **Tiết kiệm 94% RAM vs Fixed-12** |

### 8.5. Tác động của Gap Extension (trên MSNBC 100K)

| max_gap | Patterns | Precision@3 | Ghi chú                     |
|---------|----------|-------------|------------------------------|
| 0       | 525      | 25.76%      | Không dùng gap               |
| 1       | 525      | 25.76%      | Gap nhỏ, chưa đủ hiệu quả   |
| 2       | 1,596    | 47.47%      | Bước nhảy lớn!               |
| 3       | 1,895    | 48.99%      | Tiếp tục cải thiện           |
| **5**   | **1,901**| **51.01%**  | **Điểm bão hòa, tối ưu**    |

---

## 9. Cấu trúc Source Code

```
bfspminer-improved/
│
├── main.py                          # 🚀 Entry point — điều phối tất cả demo & experiments
│
├── core/                            # 🧠 Lõi thuật toán
│   ├── __init__.py
│   ├── config.py                    # Cấu hình: BFSPMinerConfig (dataclass)
│   ├── bfspminer.py                 # Class chính: BFSPMiner (feed_item, get_frequent_patterns, predict_next)
│   ├── inverted_t0_tree.py          # Cây Inverted T₀ Tree (TreeObject + InvertedT0Tree)
│   ├── adaptive_max_length.py       # [CẢI TIẾN 1] Tự điều chỉnh max_pattern_length theo entropy + RAM
│   ├── episode_extension.py         # [CẢI TIẾN 2] Khai phá mẫu có khoảng cách (gap constraints)
│   └── utils.py                     # Hàm tiện ích
│
├── evaluation/                      # 📊 Đánh giá & thí nghiệm
│   ├── compare_baseline.py          # So sánh Python vs Java Baseline
│   ├── run_experiments.py           # Bộ 5 thí nghiệm (Scalability, Sensitivity, Gap, Adaptive, Full)
│   ├── run_standardized_experiments.py  # Phiên bản chuẩn hóa (xuất JSON)
│   ├── generate_figures.py          # Sinh biểu đồ PDF/PNG publication-quality
│   ├── plot_results.py              # Sinh biểu đồ từ CSV
│   ├── preprocess_redd.py           # Tiền xử lý dữ liệu REDD
│   ├── demo_eyetracking.py         # Demo trên dữ liệu EyeTracking
│   ├── eda_redd.py                  # Phân tích khám phá dữ liệu REDD
│   ├── redd_baseline_eda.py         # EDA cho Baseline
│   └── results/                     # Báo cáo markdown tự sinh
│       ├── redd_experiment_report.md
│       ├── msnbc_experiment_report.md
│       └── ...
│
├── data/                            # 📁 Dữ liệu đầu vào
│   ├── redd_full_sequence.txt       # Chuỗi sự kiện REDD (457K events)
│   └── msnbc_sequence.txt           # Chuỗi sự kiện MSNBC (424K events)
│
├── results/                         # 📈 Kết quả thí nghiệm (JSON)
│   ├── all_experiments.json         # Tổng hợp tất cả kết quả
│   ├── redd_exp1_overall.json       # Exp1: Overall REDD
│   ├── msnbc_exp1_overall.json      # Exp1: Overall MSNBC
│   ├── redd_exp2_scalability.json   # Exp2: Scalability
│   └── ...
│
├── figures/                         # 🖼️ Biểu đồ đã sinh
│   ├── fig_scalability_runtime.png/pdf
│   ├── fig_pattern_comparison.png/pdf
│   ├── fig_adaptive_memory.png/pdf
│   ├── fig_gap_impact.png/pdf
│   └── fig_overall_comparison.png/pdf
│
├── tests/                           # ✅ Unit tests
│   ├── test_toy_stream.py           # 4 test cases (basic, gap, adaptive, predict)
│   └── test_comparison.py           # Test đối chiếu với Java
│
├── reference/                       # 📚 Tham khảo
│   └── BFSPMiner-java/             # Mã nguồn Java gốc
│
├── requirements.txt                 # Thư viện Python cần thiết
├── conftest.py                      # Cấu hình pytest
├── rebuild_jar.bat                  # Script biên dịch Java Baseline
├── bfspminer_improved_vi.pdf        # 📄 Báo cáo khoa học (Tiếng Việt)
├── bfspminer_improved.pdf           # 📄 Báo cáo khoa học (Tiếng Anh)
└── README.md                        # Hướng dẫn tổng quan
```

---

## 📋 Checklist Demo Nhanh

Dùng checklist này để đảm bảo demo trình bày suôn sẻ:

- [ ] **Bước 0:** `pip install -r requirements.txt` — Cài đặt thư viện
- [ ] **Bước 1:** `python main.py` — Chạy toy stream, giải thích pattern + prediction
- [ ] **Bước 2:** `python main.py --compare --dataset redd` — Đối chiếu Python vs Java
- [ ] **Bước 3:** `python main.py --run-experiments --dataset redd --limit 10000` — Chạy benchmark nhanh
- [ ] **Bước 4:** `python evaluation/generate_figures.py` — Sinh biểu đồ
- [ ] **Bước 5:** `pytest tests/ -v` — Chạy unit tests
- [ ] **Bước 6:** Mở Python REPL và chạy đoạn code interactive — Minh họa cây T₀
- [ ] **Bước 7:** Trình bày bảng kết quả tóm tắt + biểu đồ

> **Tip:** Nếu bị giới hạn thời gian, ưu tiên Demo 1, Demo 5, Demo 6 và phần Tóm tắt Kết quả. Các demo còn lại có thể chạy trước và chiếu kết quả.

---

*Tài liệu này được tạo cho mục đích trình bày demo cuối kỳ. Mọi kết quả thí nghiệm đều có thể tái tạo (reproducible) bằng cách chạy lại các lệnh trên.*
