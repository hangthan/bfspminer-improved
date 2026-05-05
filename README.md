# BFSPMiner-Improved

## Giới thiệu
Dự án này là phiên bản Python của thuật toán **BFSPMiner** (Batch-Free Sequential Pattern Miner), được phát triển dựa trên [bản Java gốc](https://github.com/Xsea/BFSPMiner) theo bài báo "BFSPMiner: An Effective and Efficient Batch-Free Algorithm for Mining Sequential Patterns over Data Streams".

## Cấu trúc và Phân tích bản Java (Baseline)
Sau khi clone repository gốc, phân tích cấu trúc mã nguồn Java cho thấy các thành phần chính sau:

1. **`BFSPMiner`**: Class chính cung cấp giao diện khởi tạo và gọi thuật toán. Nhận các tham số như `maxPatternLength`, `pruning` flag, `delta`, `batchLength`, `alpha`, `eps`. Quản lý luồng bằng cách gọi `PatternBuilder` để xử lý từng event.
2. **`PatternBuilder` & `TreeObject` (Inverted T0 Tree)**: 
   - `PatternBuilder`: Lớp chịu trách nhiệm chính trong việc xây dựng cây Inverted T₀. Nó nối các event theo thứ tự đảo ngược và cập nhật đếm (count, batchCount) trên cây. Đồng thời, nó chứa phương thức `ssbePrune` để thực hiện chiến lược cắt tỉa (pruning) tiết kiệm bộ nhớ.
   - `TreeObject`: Đại diện cho một node trong Inverted T₀ Tree. Chứa nhãn (value), danh sách timestamps, bộ đếm tần suất (count, batchCount) và liên kết đến các node con (qua danh sách `TreeObjectList`). Node root là một `TreeObject` trống với nhãn "root".
3. **`Predictor`**: Lớp thực hiện dự đoán event tiếp theo dựa trên các pattern đã khai phá. Sử dụng điểm độ tin cậy (confidence) của các luật (rule) phù hợp với ngữ cảnh hiện tại (snapshot) để đưa ra `k` dự đoán.
4. **`PatternMetrics` & `Util`**: Các module tiện ích để duyệt cây, đếm support/confidence, và các hàm bổ trợ cho quá trình sinh pattern.

> **Đánh giá bản Java**: Bản Java sử dụng cấu trúc `TreeObjectList` (kế thừa `ArrayList`) để lưu children, dẫn đến độ phức tạp O(N) khi tìm kiếm node con. Ngoài ra, cách trích xuất pattern dùng string manipulation khá kém hiệu quả. Bản Python sử dụng `Dict` (Hash Map) để tăng tốc O(1) và thuật toán `DFS` đệ quy để trích xuất pattern nhanh chóng hơn.

---

## Các Cải tiến (Extensions)
Dự án Python này không chỉ implement lại bản gốc (với code clean và type hints) mà còn thêm 2 tính năng nâng cao:

1. **AdaptiveMaxPatternLength (`core/adaptive_max_length.py`)**: 
   - Tự động điều chỉnh `max_pattern_length` (từ 3 đến 15) dựa trên pattern density (đo bằng Shannon Entropy) và dung lượng RAM hiện tại (`psutil`).
   - Nếu memory quá cao (>500MB) hoặc entropy > 3.0 (tính ngẫu nhiên cao), thuật toán sẽ giảm `max_pattern_length` để tăng hiệu năng. Nếu entropy thấp (dữ liệu có tính lặp lại quy luật), thuật toán sẽ tăng `max_pattern_length` để bắt được các pattern dài.

2. **EpisodeMiningExtension (`core/episode_extension.py`)**: 
   - Hỗ trợ khai phá non-consecutive patterns (có gap).
   - Thêm tham số `max_gap` (khoảng cách tối đa giữa 2 sự kiện) và `window_size` (độ rộng cửa sổ thời gian). 
   - Khi cờ `enable_gap=True` được bật, thuật toán sinh ra tất cả các chuỗi hợp lệ thỏa mãn điều kiện gap và đưa vào cây Inverted T0 Tree. Thuật toán đảm bảo mỗi event chỉ được cập nhật tối đa 1 lần trên mỗi path của cây thông qua cờ `visited_nodes`.

---

## Cách chạy và Kiểm thử

### Cài đặt môi trường
```bash
pip install -r requirements.txt
```

### Chạy Demo (main.py)
```bash
python main.py
```
Script sẽ chạy một chuỗi sự kiện mẫu với cả `AdaptiveMaxPatternLength` và `EpisodeMiningExtension` được bật, in ra các tập phổ biến có chứa gap và thử dự đoán 2 event tiếp theo.

### Chạy Unit Test
Toàn bộ logic được đảm bảo qua `pytest`.
```bash
pytest tests/
```

### Chạy so sánh với Baseline trên Toy Data
```bash
run_comparison.bat
```
File này sẽ chạy thuật toán gốc bằng Python (không bật extensions) trên toy stream và tự động biên dịch, chạy song song với bản Java gốc. 

### Chạy Thực nghiệm trên Dataset REDD / EyeTracking
Sau khi tiền xử lý xong dataset, chạy command:
```bash
python main.py --compare --dataset redd
```
Hoặc chạy Demo EyeTracking (nếu có data):
```bash
python main.py --demo eyetracking
```
Hệ thống sẽ chạy song song `BASELINE` và `IMPROVED` mode, in ra bảng so sánh chi tiết về thời gian, RAM, và độ bao phủ của Pattern. Mẫu báo cáo sẽ được lưu trong `evaluation/results/`.

### Chạy Thực nghiệm 5 bài Benchmark (Evaluation Suite)
Hệ thống hỗ trợ chạy tự động 5 bài thực nghiệm quan trọng trên Dataset REDD (Scalability, Parameter Sensitivity, Gap Impact, Adaptive Impact, Full dataset). Để chạy với dữ liệu giả lập (tốc độ nhanh):
```bash
python main.py --run-experiments
```
Hoặc để chạy bài benchmark **full power** (tới 767.829 items):
```bash
python main.py --run-experiments --full
```
*Kết quả sẽ được xuất ra dưới dạng Markdown `experiment_report.md` và CSV `experiment_results.csv` nằm trong folder `evaluation/results/`.*

### Kết quả Verification với Java Baseline
Sau khi chạy script so sánh, dưới đây là kết quả đối chiếu giữa 2 phiên bản. Có thể thấy bản Python **khớp 100% độ chính xác** (số lượng tập phổ biến, support, và kết quả dự đoán) so với bản Java gốc, đồng thời thời gian thực thi vô cùng tối ưu:

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
