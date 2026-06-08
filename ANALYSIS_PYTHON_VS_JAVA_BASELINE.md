# So Sánh Thuật Toán: Python Baseline vs Java Baseline

## 📊 Kết Quả Thực Thi

### REDD Dataset
| Metric | Java Baseline | Python Baseline | Kết Luận |
|--------|---------------|-----------------|----------|
| Patterns Found | 76 | 76 | ✅ Trùng khớp |
| Runtime (s) | 0.2920 | 1.3705 | Java nhanh 4.7x |
| Memory (MB) | N/A | 22.52 | Python dùng 22.52 MB |
| Status | ✅ OK | ✅ OK | Cả hai chạy tốt |

### MSNBC Dataset
| Metric | Java Baseline | Python Baseline | Kết Luận |
|--------|---------------|-----------------|----------|
| Patterns Found | **6** | **523** | ❌ **KHÁC BIỆT LỚN** |
| Runtime (s) | 0.0040 | 1.8585 | Java nhanh nhưng sai dữ liệu |
| Memory (MB) | N/A | 57.78 | Python dùng 57.78 MB |
| Status | ⚠️ BUG | ✅ OK | Java có vấn đề |

---

## 🔍 Nguyên Nhân Khác Biệt

### 🐛 **BUG PHÁT HIỆN: Java TestRunner không xử lý MSNBC**

#### File: `evaluation/TestRunner.java` (Line 18-47)

```java
public class TestRunner {
    public static void main(String[] args) {
        BFSPMiner miner = new BFSPMiner(5, false, 4, 500, 0.00995, 0.00999);
        
        String[] stream;
        String datasetName = "toy";
        double minSup = 0.1;
        
        if (args.length > 0 && args[0].equals("redd")) {
            // ✅ Xử lý REDD
            datasetName = "redd";
            minSup = 0.001;
            // ... load từ file ...
        } else {
            // ❌ MỌI dataset khác (bao gồm MSNBC) đều rơi vào đây
            stream = new String[]{"a", "b", "c", "a", "b", "d", "a", "b", "c", "e", "a", "b"};
        }
        
        // ... xử lý ...
    }
}
```

**Vấn đề:** 
- Java chỉ có case đặc biệt cho `"redd"`
- Khi chạy với `"msnbc"`, nó không khớp condition `args[0].equals("redd")`
- Rơi vào `else` clause, sử dụng **toy stream** (12 items) thay vì MSNBC data (423,776 items)
- Kết quả: Java chỉ tìm 6 patterns từ toy stream, không phải từ MSNBC

---

## 📈 So Sánh Chi Tiết

### 1. **Data Loading**

**Java:**
```java
if (args.length > 0 && args[0].equals("redd")) {
    // Load file
} else {
    // Dùng hardcoded toy stream
}
```
❌ Không hỗ trợ MSNBC

**Python:**
```python
def load_dataset(dataset_name):
    if dataset_name == "toy":
        return ['a', 'b', 'c', ...]
    
    file_path = f"data/{dataset_name}.txt"
    if dataset_name == "redd":
        file_path = "data/redd_full_sequence.txt"
    elif dataset_name == "msnbc":
        file_path = "data/msnbc_sequence.txt"
    
    # Load từ file
    stream = []
    with open(file_path, 'r') as f:
        for line in f:
            stream.append(line.strip())
    return stream
```
✅ Hỗ trợ cả redd, msnbc, toy

### 2. **Data Format Processing**

**REDD Dataset (430,175 items):**

Java (đúng):
```
Input:  "microwave" "light" → "microwave|light"
```

Python (đúng):
```
Input:  "microwave light" → "microwave|light"
```
✅ Cả hai xử lý giống nhau

**MSNBC Dataset (423,776 items):**

Java: ❌ **Không xử lý, dùng toy stream**
```
Input:  ['a', 'b', 'c', 'a', 'b', 'd', ...]  (12 items)
Output: 6 patterns
```

Python: ✅ **Xử lý đúng**
```
Input:  Stream 423,776 items từ file
Output: 523 patterns
```

### 3. **Thuật Toán Core**

**Java BFSPMiner Constructor:**
```java
BFSPMiner miner = new BFSPMiner(
    5,           // maxPatternLength
    false,       // enableAdaptive
    4,           // maxEpisodeLength
    500,         // windowSize
    0.00995,     // alpha
    0.00999      // eps
);
```

**Python BFSPMiner Config:**
```python
config = BFSPMinerConfig(
    max_pattern_length=5,
    pruning=True,
    enable_adaptive=False,  # Baseline
    enable_gap=False,       # Baseline
)
```

✅ Cả hai dùng max_pattern_length=5

---

## 📋 Chi Tiết Pattern Phát Hiện

### MSNBC - Python Baseline (đúng):
```
1  | ('1')                              | Support: 0.272
2  | ('2')                              | Support: 0.119
3  | ('7')                              | Support: 0.092
4  | ('4')                              | Support: 0.086
5  | ('6')                              | Support: 0.075
...
Total: 523 patterns
```
✅ Processing 423,776 items từ file

### MSNBC - Java Baseline (sai):
```
1  | ('a')                              | Support: 0.333
2  | ('b')                              | Support: 0.333
3  | ('a', 'b')                         | Support: 0.333
4  | ('c')                              | Support: 0.167
5  | ('b', 'c')                         | Support: 0.167
6  | ('a', 'b', 'c')                    | Support: 0.167
```
❌ Processing toy stream (12 items)

---

## 💡 Kết Luận & Khuyến Nghị

### Kết Luận:
1. **Java Baseline có BUG**: TestRunner.java không xử lý MSNBC dataset
2. **Python Baseline chính xác**: Xử lý đúng cả REDD và MSNBC
3. **Hiệu suất**: Java nhanh hơn khi có dữ liệu đúng (REDD: 4.7x nhanh hơn)
4. **So sánh công bằng**: Chỉ có thể so sánh Java vs Python trên REDD dataset

### Khuyến Nghị:
1. **Sửa TestRunner.java** - Thêm hỗ trợ MSNBC:
   ```java
   if (args[0].equals("redd")) {
       // Load REDD
   } else if (args[0].equals("msnbc")) {
       // Load MSNBC
   } else {
       // Toy stream
   }
   ```

2. **Xác thực lại kết quả** sau khi sửa bug

3. **Cân nhắc cấu trúc TestRunner** để hỗ trợ dễ dàng nhiều datasets

---

## 📊 Bảng So Sánh Tính Năng

| Tính Năng | Java | Python |
|-----------|------|--------|
| REDD Support | ✅ | ✅ |
| MSNBC Support | ❌ (BUG) | ✅ |
| Toy Stream | ✅ | ✅ |
| Adaptive Length | Có (không dùng) | ✅ Dùng khi enable |
| Episode Gap | Có (không dùng) | ✅ Dùng khi enable |
| Memory Tracking | ❌ | ✅ |
| Progress Bar | ❌ | ✅ (tqdm) |
| Pattern Ranking | ✅ | ✅ |
| Prediction | ✅ | ✅ |

---

## 📌 Lưu Ý

**Để so sánh công bằng:**
- Chỉ so sánh trên REDD dataset (dữ liệu đúng cả 2 bên)
- Java: 0.2920s, 76 patterns
- Python: 1.3705s, 76 patterns
- **Java nhanh hơn ~4.7x nhưng với trade-off khác** (không có memory tracking, adaptive features, etc.)

