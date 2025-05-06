# 🧹 打掃記錄系統 Cleaning Tracker

一個使用者登入後即可使用的全端 CRUD 專案，讓每個人都能建立並管理自己的打掃紀錄。畫面以一張「365 天 × 打掃地點」的表格呈現打掃歷程，適合用於習慣建立、家務管理。

---

## 🧱 技術架構

| 層級 | 技術 |
| --- | --- |
| 前端 | HTML + CSS + 原生 JavaScript |
| 後端 | Flask RESTful API |
| 資料庫 | PostgreSQL（Supabase） |
| 使用者認證 | Supabase Auth |
| 部署平台 | Vercel（Serverless API Routes） |

---

## 🗃️ 資料結構（簡化版）

### `locations`（打掃地點）

- `id` (UUID)
- `user_id` (UUID)
- `name` (TEXT)

### `cleaning_records`（打掃紀錄）

- `id` (UUID)
- `user_id` (UUID)
- `location_id` (UUID)
- `date` (DATE)
- `cleaned` (BOOLEAN)

---

## 🔐 核心功能與邏輯

- [ ]  使用者註冊 / 登入（Supabase Auth）
- [ ]  每位使用者的資料彼此隔離
- [ ]  CRUD 操作（地點、打掃紀錄）
- [ ]  365 天 × 多地點表格視圖
- [ ]  限制勾選範圍（只能修改當週及前後一週）
- [ ]  RESTful API 設計，支援 JSON 請求 / 回應
- [ ]  防止非法 API 存取（用戶驗證與日期驗證）
- [ ]  前後端部署完成，可供實際訪問

---

## 🧪 展示連結

- 🔗 專案網址（Demo）：👉 https://cleaning-tracker.vercel.app

---

## 🧭 如何使用

1. 進入首頁並註冊帳號
2. 登入後即可開始使用個人打掃紀錄表
3. 點選地點名稱右側可新增/刪除地點
4. 在表格內點選可記錄是否完成打掃（限時間範圍內）
5. 資料儲存在 Supabase PostgreSQL，所有操作透過 API 控制

---

## 📂 資料夾結構簡述

├── api/                  # Flask API Routes（部署到 Vercel）
│   ├── [locations.py](http://locations.py/)
│   ├── [records.py](http://records.py/)
│   └── [auth.py](http://auth.py/)
├── static/               # 前端 JS / CSS
├── templates/            # HTML 模板
├── vercel.json           # Vercel 設定
├── requirements.txt      # Python 套件清單
└── [README.md](http://readme.md/)

---

## 📌 延伸功能（可擴充）

- 使用者可切換週 / 月 / 年檢視模式
- 打掃頻率統計、報表分析
- 推播提醒（LINE / Email）
- 跨裝置同步