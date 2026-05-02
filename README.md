# 異環 NTE 自動釣魚程式

這是一個給遊戲《異環》（NTE）使用的自動釣魚輔助程式。程式會透過螢幕擷取與顏色辨識，判斷釣魚提示、拉竿時機與釣魚進度條，並自動送出滑鼠點擊與鍵盤操作，幫助玩家減少重複性的釣魚流程。

> 本專案主要作為個人自動化工具與學習範例。請自行確認遊戲規範、服務條款與使用風險，並負責任地使用。

## 中文介紹

這個腳本適合想研究 Python 螢幕辨識、自動輸入、遊戲 UI 偵測流程的人。它不是修改遊戲檔案，也不注入遊戲程式，而是使用目前畫面上的顏色區域來判斷狀態，再透過一般鍵盤與滑鼠輸入完成操作。

主要功能：

- 自動尋找並切換到《異環》遊戲視窗。
- 偵測釣魚提示出現後，自動按下互動鍵。
- 偵測釣魚進度條與目標區域，依照位置自動按 `A` / `D`。
- 支援從 `2560x1440` 參考解析度自動縮放偵測範圍。
- 可用 `F8` 安全停止程式。
- 可透過指令參數調整遊戲視窗標題與擷取 FPS。

## 安裝需求

- Windows 10/11
- Python 3.10 或更新版本
- 遊戲《異環》（NTE）需以可見視窗執行
- 依賴套件請見 `requirements.txt`

## 快速開始

```powershell
git clone https://github.com/kakko-jia/nte-auto-fishing-script.git
cd nte-auto-fishing-script
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python fishing_bot_release_v2.py
```

如果遊戲視窗標題不同，可以指定視窗名稱：

```powershell
python fishing_bot_release_v2.py --window-title "NTE"
```

如果電腦負載較高，可以降低擷取 FPS：

```powershell
python fishing_bot_release_v2.py --fps 30
```

## 操作方式

| 按鍵 | 功能 |
| --- | --- |
| `F8` | 停止程式 |
| `Ctrl+C` | 從終端機停止程式 |

## 偵測調整

預設偵測範圍是依照 `2560x1440` 畫面調整出來的。如果你的 UI 位置不同，可以修改 `fishing_bot_release_v2.py` 裡的區域常數：

```python
BAR_REGION_REF = (800, 70, 1770, 130)
ICON_REGION_REF = (REFERENCE_W - 750, REFERENCE_H - 220, REFERENCE_W - 100, REFERENCE_H - 40)
HOOK_REGION_REF = (REFERENCE_W - 280, REFERENCE_H - 220, REFERENCE_W - 100, REFERENCE_H - 40)
```

如果顏色判斷不穩，也可以調整 HSV 顏色門檻：

```python
YELLOW_LOWER = np.array([20, 80, 120])
YELLOW_UPPER = np.array([40, 255, 255])
GREEN_LOWER = np.array([45, 80, 80])
GREEN_UPPER = np.array([85, 255, 255])
STEP2_BLUE_THRESHOLD = 0.06
```

## 常見問題

### 找不到遊戲視窗

請使用 `--window-title` 指定完整或部分視窗標題：

```powershell
python fishing_bot_release_v2.py --window-title "Your Window Title"
```

### 啟動後沒有反應

- 確認遊戲視窗可見，且沒有被最小化。
- 如果輸入被擋下，嘗試用系統管理員身分開啟 PowerShell 或終端機。
- 確認顯示縮放、遊戲解析度與 UI 位置是否接近預設配置。

### 偵測位置不準

程式會從 `2560x1440` 參考解析度縮放偵測範圍，但不同 UI 配置仍可能需要手動調整。請參考上方「偵測調整」章節修改區域常數。

## 專案結構

```text
.
|-- fishing_bot_release_v2.py
|-- requirements.txt
|-- pyproject.toml
|-- README.md
|-- LICENSE
|-- CONTRIBUTING.md
|-- SECURITY.md
`-- .gitignore
```

## 免責聲明

本專案與《異環》（NTE）及其發行商、開發商沒有任何關聯，也未受到官方認可或贊助。使用者需自行承擔使用此腳本造成的任何後果。

---

# NTE Auto Fishing Script

Windows-only auto fishing helper for NTE. It uses screen capture plus simple color detection to identify the fishing prompt/bar, then sends keyboard and mouse input.

> This project is intended as a personal automation template and learning reference. Use it responsibly and check the rules or terms of service for any game or service you use it with.

## Features

- Automatically activates the game window by title.
- Detects the fishing prompt and fishing bar from the screen.
- Scales detection regions from the original `2560x1440` tuning to your current capture size.
- Press `F8` to stop safely.
- Configurable window title and capture FPS from the command line.

## Requirements

- Windows 10/11
- Python 3.10 or newer
- NTE running in a visible window
- Dependencies listed in `requirements.txt`

## Quick Start

```powershell
git clone https://github.com/kakko-jia/nte-auto-fishing-script.git
cd nte-auto-fishing-script
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python fishing_bot_release_v2.py
```

If your game window title is different:

```powershell
python fishing_bot_release_v2.py --window-title "NTE"
```

Lower capture FPS if your computer is under heavy load:

```powershell
python fishing_bot_release_v2.py --fps 30
```

## Controls

| Key | Action |
| --- | --- |
| `F8` | Stop the script |
| `Ctrl+C` | Stop from the terminal |

## Tuning

The default regions were tuned from a `2560x1440` layout:

- `BAR_REGION_REF`: fishing progress bar area
- `ICON_REGION_REF`: prompt/icon area
- `HOOK_REGION_REF`: hook prompt area

If detection is unreliable on your UI layout, adjust these constants in `fishing_bot_release_v2.py`:

```python
BAR_REGION_REF = (800, 70, 1770, 130)
ICON_REGION_REF = (REFERENCE_W - 750, REFERENCE_H - 220, REFERENCE_W - 100, REFERENCE_H - 40)
HOOK_REGION_REF = (REFERENCE_W - 280, REFERENCE_H - 220, REFERENCE_W - 100, REFERENCE_H - 40)
```

Color thresholds can also be tuned:

```python
YELLOW_LOWER = np.array([20, 80, 120])
YELLOW_UPPER = np.array([40, 255, 255])
GREEN_LOWER = np.array([45, 80, 80])
GREEN_UPPER = np.array([85, 255, 255])
STEP2_BLUE_THRESHOLD = 0.06
```

## Troubleshooting

### The script cannot find the game window

Run the script with the exact or partial window title:

```powershell
python fishing_bot_release_v2.py --window-title "Your Window Title"
```

### Nothing happens after starting

- Make sure the game window is visible and not minimized.
- Run PowerShell or your terminal as administrator if input is blocked.
- Check that your display scaling and game resolution are close to the expected UI layout.

### Detection is wrong on my resolution

The script scales from the reference `2560x1440` layout, but game UI position can still differ. Adjust the region constants listed in the tuning section.

## Project Structure

```text
.
|-- fishing_bot_release_v2.py
|-- requirements.txt
|-- pyproject.toml
|-- README.md
|-- LICENSE
|-- CONTRIBUTING.md
|-- SECURITY.md
`-- .gitignore
```

## Disclaimer

This repository is not affiliated with, endorsed by, or sponsored by NTE or its publishers. You are responsible for how you use this script.
