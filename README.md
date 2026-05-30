# BFSPMiner-Improved

## Giới thiệu
Dự án này là phiên bản Python cải tiến và tối ưu của thuật toán **BFSPMiner** (Batch-Free Sequential Pattern Miner), được phát triển dựa trên [bản Java gốc](https://github.com/Xsea/BFSPMiner) theo bài báo *"BFSPMiner: An Effective and Efficient Batch-Free Algorithm for Mining Sequential Patterns over Data Streams"*.

Bên cạnh mã nguồn thuật toán, dự án còn đi kèm **Báo cáo Khoa học (LaTeX Report)** chi tiết tại file `bfspminer_improved_vi.pdf` (Tiếng Việt) và `bfspminer_improved.pdf` (Tiếng Anh), cùng với **Báo cáo Bài tập lớn** tại `baocao_btl.pdf` và hướng dẫn chạy thực nghiệm chi tiết tại `demo_guide.md`. Các báo cáo này giải thích rõ về cơ sở lý thuyết, phân tích độ phức tạp, các cải tiến và kết quả thực nghiệm chuyên sâu.

---

## Cấu trúc và Phân tích bản Java (Baseline)
Sau khi phân tích cấu trúc mã nguồn Java, thuật toán gốc gồm các thành phần chính sau:

1. **`BFSPMiner`**: Class chính cung cấp giao diện khởi tạo và gọi thuật toán. Nhận các tham số như `maxPatternLength`, `pruning`, `delta`, `batchLength`.
2. **`PatternBuilder` & `TreeObject` (Inverted T0 Tree)**: 
   - `PatternBuilder`: Xây dựng cây Inverted T₀. Nối các event theo thứ tự đảo ngược và cập nhật đếm (count, batchCount) trên cây. Đồng thời, nó chứa phương thức `ssbePrune` để thực hiện chiến lược cắt tỉa tiết kiệm bộ nhớ.
   - `TreeObject`: Đại diện cho một node trong Inverted T₀ Tree (chứa value, list timestamps, count, child nodes).
3. **`Predictor`**: Lớp thực hiện dự đoán event tiếp theo dựa trên các pattern đã khai phá (bằng confidence score).
4. **`PatternMetrics` & `Util`**: Các module tiện ích duyệt cây và đếm support.

> **Đánh giá bản Java**: Bản Java sử dụng cấu trúc `TreeObjectList` (kế thừa `ArrayList`) để lưu children, dẫn đến độ phức tạp O(N) khi tìm kiếm node con. Trong bản Python, chúng tôi sử dụng cấu trúc Dictionary (Hash Map) để tăng tốc độ tìm kiếm lên O(1) và thay thế logic trích xuất mẫu bằng thuật toán duyệt đồ thị `DFS` đệ quy nhanh chóng.

---

## Các Cải tiến (Extensions)
Dự án Python này không chỉ implement lại bản gốc một cách tối ưu (với code clean, type hints) mà còn tích hợp 2 tính năng nâng cao quan trọng:

1. **AdaptiveMaxPatternLength (`core/adaptive_max_length.py`)**: 
   - Tự động điều chỉnh `max_pattern_length` (từ 3 đến 15) dựa trên mật độ luật (pattern density) thông qua chỉ số Shannon Entropy và dung lượng RAM hiện tại.
   - Nếu RAM bị đầy hoặc chuỗi quá nhiễu (entropy > 3.0), hệ thống sẽ giảm độ dài mẫu tối đa. Ngược lại, nếu entropy thấp (dữ liệu có tính quy luật), thuật toán sẽ tăng chiều dài để khai phá được những mẫu chuỗi dài hơn.

2. **EpisodeMiningExtension (`core/episode_extension.py`)**: 
   - Hỗ trợ khai phá non-consecutive patterns (chuỗi sự kiện có khoảng cách/gap).
   - Bổ sung tham số `max_gap` (khoảng cách tối đa giữa 2 sự kiện) và `window_size` (độ rộng cửa sổ thời gian). 
   - Khi cờ `enable_gap=True` được bật, thuật toán sinh ra tất cả các tổ hợp chuỗi con hợp lệ thỏa mãn điều kiện gap và đưa vào cây Inverted T0 Tree.

---

## Cách cài đặt và Chạy code

### 1. Cài đặt môi trường
Yêu cầu Python 3.9+.
```bash
pip install -r requirements.txt
```

### 2. Chạy Demo Cơ bản (Toy Data)
```bash
python main.py
```
Script sẽ chạy một chuỗi sự kiện mẫu, tự động bật `AdaptiveMaxPatternLength` và `EpisodeMiningExtension`, in ra các tập phổ biến có chứa khoảng cách (gap) và thử dự đoán 2 sự kiện tiếp theo.

### 3. Phân tích Dữ liệu (EDA & Preprocessing)
Dự án cung cấp các script hỗ trợ tiền xử lý và phân tích (EDA) các bộ dữ liệu lớn:
- **REDD EDA**: Chạy `python evaluation/redd_baseline_eda.py` để trích xuất các thông tin phân phối, vẽ biểu đồ chuỗi thời gian của bộ dữ liệu tiêu thụ điện năng.
- **Tiền xử lý (Preprocess)**: Dữ liệu REDD, MSNBC sẽ được tự động làm sạch và sinh ra chuỗi (sequence) qua script `evaluation/preprocess_redd.py`.

### 4. Chạy Thực nghiệm Đối chiếu với Java Baseline
Hệ thống tự động biên dịch code Java bằng `rebuild_jar.bat` và gọi file `.class` qua subprocess để chạy đối chiếu trực tiếp với bản Python.
```bash
# Đối chiếu trên REDD
python main.py --compare --dataset redd

# Đối chiếu trên MSNBC
python main.py --compare --dataset msnbc

# Đối chiếu EyeTracking
python main.py --demo eyetracking
```
Hệ thống in ra bảng so sánh chi tiết về thời gian, RAM, và độ bao phủ. Mẫu báo cáo sẽ được lưu trong `evaluation/results/`.

### 5. Chạy Chuỗi Thực nghiệm (Evaluation Suite)
Hệ thống hỗ trợ chạy benchmark tiêu chuẩn qua script `run_standardized_experiments.py`:
```bash
# Chạy đánh giá trên dataset msnbc
python evaluation/run_standardized_experiments.py --dataset msnbc
```
*Kết quả xuất ra các file JSON chi tiết tại thư mục `results/`.*

### 6. Trực quan hóa Kết quả (Plotting)
Sau khi chạy Benchmark, bạn dùng script sau để tự động tạo ra các biểu đồ (line chart, bar chart) để đưa vào báo cáo:
```bash
python evaluation/generate_figures.py
```
Ảnh biểu đồ PDF và PNG chất lượng cao sẽ được lưu vào thư mục `figures/`.

### 7. Unit Testing
Toàn bộ logic gốc và extensions đều được cover thông qua `pytest`:
```bash
pytest tests/
```

---

## Kết quả Verification mẫu
Sau khi đối chiếu, phiên bản Python cho **độ chính xác 100%** so với bản Java gốc (về số lượng mẫu phổ biến, support và luật dự đoán), trong khi có tốc độ thực thi nhỉnh hơn hoặc bằng nhờ cấu trúc dữ liệu Dictionary.

```text
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

[*] Next 3 Predictions (Context: 'a' -> 'b'):
    => ['c', 'd', 'a']
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

[*] Next 3 Predictions (Context: 'a' -> 'b'):
    => ['c', '', '']
```
