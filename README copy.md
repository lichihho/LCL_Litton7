# 用在實驗室的服務

| 名稱 | 描述 |
|------|------|
| litton7-internal | 給內部成員的 Litton7 分析服務 |
| litton7-public | 用於展示研究成果的 Litton7 分析服務，與 internal 版比較起來缺少批次分析功能。<br>須與 litton7-proxy 一併使用 |
| litton7-proxy | 將 litton7-public 接到 lclab.thu.edu.tw 的轉接器。<br>讓運作 Litton7 的工作負載可以轉移到實驗室內部網路上其中一台運算專用主機上，不必強求 NAS 本身的運算能力 |

目前（2025 年 2 月 27 日）litton7-internal 與 litton7-public 部屬在 UB5 上，而 litton7-proxy 運作在 NAS-Holi 上。
部屬操作說明請洽各資料夾內的專屬 README.md。