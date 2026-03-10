# 醫療影像 PACS 系統零接觸遠距操作系統
# Contactless PACS Medical Image Remote Control System

本專案實作了一套利用**電腦視覺**與**深度學習**技術的 PACS（醫療影像儲存與傳輸系統）零接觸操作介面。旨在讓執刀醫師在手術室的無菌環境中，無需物理接觸螢幕或透過他人轉達，即可自行操作病人醫療影像，降低感染風險並提升手術效率。

---

## 🚀 系統功能 (Features)
* **非接觸式影像操作**：支持平移、縮放、調整窗位、旋轉、切片選取及放大鏡功能。
* **雙重驗證機制**：結合**手勢辨識**（LSTM 模型）與**語音指令**進行雙重確認，大幅提高操作正確性並防止誤動作。
* **即時手部追蹤**：採用 **MediaPipe** 機器視覺技術，精確捕捉手部 21 個 3D 關鍵點特徵。
* **環境適應預處理**：利用 **k-means 分群演算法** 自動辨識醫療手套顏色（藍色/白色），並調整影像渲染參數以解決模型無法辨識手套的問題。

---

## 🛠️ 系統架構 (System Architecture)

系統主要由三個部分組成：

1. **輸入裝置**：RGB 網路攝影機（手勢捕捉）與麥克風（語音輸入）。
2. **系統程式**：包含 ROI 區域劃定、影像預處理、MediaPipe 特徵提取與 LSTM 手勢分類。
3. **DICOM 瀏覽器**：透過 **PyAutoGUI** 模擬滑鼠與鍵盤動作，呼叫 DICOM Library API 以執行操作。

---

## 🖐️ 手勢定義與操作 (Gestures)

系統設計了 6 種直覺且易記的基本手勢，搭配上、下、左、右移動來觸發 20 種動作序列：

| 基本手勢 | 對應功能 | 移動序列與效果 |
| :--- | :--- | :--- |
| **手勢一** (食指) | 平移功能 | 上、下、左、右移動影像位置 |
| **手勢二** (食指中指) | 縮放功能 | 向上移動放大、向下移動縮小 |
| **手勢三** (三指) | 調整窗位 | 上、下、左、右調整影像灰階（亮度/對比） |
| **手勢四** (四指) | 旋轉功能 | 向上逆時針旋轉、向下順時針旋轉 |
| **手勢五** (五指張開) | 選取影像 | 上下切換影像、左右切換切片 (Slice) |
| **手勢六** (五指收起) | 放大鏡功能 | 隨手部移動控制放大鏡範圍 |

---

## 💻 使用說明 (How to Use)

### 1. 資料蒐集 (Data Collection)

若需蒐集自定義手勢資料（需連接網路攝影機）：

* 請執行：`training\.ipynb_checkpoints\training-checkpoint.ipynb`
* 此程式會以 30 幀為單位錄製手部關鍵點序列並儲存為 NumPy 矩陣。

### 2. 模型訓練 (Model Training)

準備好資料後，訓練 LSTM 神經網路模型：

* 請執行：`training\training.ipynb`
* 該架構包含三層 LSTM 單元（64、128、64 units），捕捉動作的時間相依性。

### 3. 運行系統 (System Execution)

啟動最終整合系統：

* 在終端機執行：`python main\test.py`

**啟動流程**：

1. **手套校準**：程式啟動後將開啟相機，請將戴著手套的手覆蓋於畫面綠色偵測框 10 秒進行顏色校準。
2. **模式選取**：以語音下達功能模式指令（如「平移」、「縮放」、「窗位」、「旋轉」、「選取」、「放大鏡」）。
3. **手勢操作**：系統確認語音模式後，即可配合對應手勢進行即時影像操作。

---

## 📈 實驗結果 (Results)

本系統重新定義了資料結構，改採**相對位移向量**進行辨識（以 5 幀為一辨識單位）。這使模型達到約 **99% 的辨識率**，並將延遲降低至 **1/6 秒**，確保手術環境所需的即時回饋感。

---

<details>
<summary><b>English Version (Click to expand)</b></summary>

## 🚀 Features

* **Contactless Operation**: Supports pan, zoom, window level, rotate, image/slice selection, and magnifier functions.
* **Dual-Input Verification**: Combines **hand gestures** (LSTM) with **voice commands** to ensure accuracy.
* **Real-time Tracking**: Uses **MediaPipe** to capture 21 3D hand landmarks.
* **Glove Adaptation**: Uses **k-means clustering** to identify surgical glove colors and adjust image rendering for stable tracking.

## 🖐️ Gesture Definition

| Gesture | Function | Movement Sequence |
| :--- | :--- | :--- |
| **Gesture 1** (Index) | Pan | Move image Up, Down, Left, or Right |
| **Gesture 2** (Index+Middle) | Zoom | Move Up to Zoom In, Down to Zoom Out |
| **Gesture 3** (Three fingers) | Window Level | 2D adjustment of gray levels |
| **Gesture 4** (Four fingers) | Rotate | Move Up for CCW, Down for CW |
| **Gesture 5** (Five open) | Selection | Up/Down for Frames, Left/Right for Slices |
| **Gesture 6** (Fist) | Magnifier | Control magnifier position in 2D |

## 💻 How to Use

1. **Data Collection**: Run `training\.ipynb_checkpoints\training-checkpoint.ipynb` to record landmark sequences.
2. **Model Training**: Run `training\training.ipynb` to train the LSTM network.
3. **Run System**: Execute `python main\test.py`. Calibrate glove color for 10s, select mode via voice, then use gestures.

## 📈 Performance

The system uses a **relative displacement vector** structure (5-frame units), achieving **99% accuracy** with a low latency of **1/6 second**.

</details>
