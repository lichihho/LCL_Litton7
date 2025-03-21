# Litton7-Internal

Litton7-Internal 是一個基於 Docker 的服務，提供視覺景觀模型的推論功能。本文檔說明如何部署、更新和卸載此服務。

## 系統需求

- 運行 Linux 的伺服器（已在 Ubuntu 上測試）
- Docker 和 Docker Compose
- NVIDIA GPU 和 NVIDIA 容器運行時（nvidia-docker）
- Root 權限

## 從 GitHub 下載

### 方法 1: 克隆整個倉庫

您可以使用以下命令克隆整個 Litton7-Internal 倉庫：

```bash
git clone https://github.com/lclab-thu/LCL_Litton7.git
cd LCL_Litton7
```

### 方法 2: 下載壓縮文件

如果您不想使用 git，也可以直接從 GitHub 下載壓縮包：

1. 訪問 [https://github.com/lclab-thu/LCL_Litton7](https://github.com/lclab-thu/LCL_Litton7)
2. 點擊 "Code" 按鈕，然後選擇 "Download ZIP"
3. 解壓下載的文件：
   ```bash
   unzip LCL_Litton7-main.zip
   cd LCL_Litton7-main
   ```

### 方法 3: 使用預打包的發行版

您也可以使用預先打包好的完整版本：

1. 下載 `litton7-internal.tar.gz` 文件
2. 解壓到您選擇的目錄：
   ```bash
   tar -xzf litton7-internal.tar.gz
   cd litton7-internal
   ```

## 部署

### 步驟 1: 準備環境文件

在部署前，請先檢查並按需修改 `.env` 文件中的設定：

```
HOST_IP=192.168.1.252  # 綁定的 IP 地址
HOST_PORT=8081         # 對外提供服務的端口
DATABASES_ROOT='/mnt/ai_data/'  # 資料庫目錄的路徑
COMPOSE_PROJECT_NAME=litton7-internal
BATCH_SIZE=16          # 批次處理大小
```

### 步驟 2: 執行部署腳本

使用 root 權限執行 `deploy.sh` 腳本：

```bash
sudo ./deploy.sh
```

此腳本將：
- 創建系統用戶 `lclwebservice`（如果不存在）
- 複製所有項目文件到 `/opt/litton7-internal/`
- 建立 Docker 映像檔
- 配置並啟動系統服務

### 步驟 3: 驗證部署

部署完成後，您可以通過以下方式檢查服務狀態：

```bash
sudo systemctl status litton7-internal
```

服務日誌可通過以下命令查看：

```bash
sudo journalctl -u litton7-internal
```

服務應該可以通過 `http://<HOST_IP>:<HOST_PORT>` 訪問。

## 更新服務

更新 Litton7-Internal 服務的步驟如下：

1. 停止現有服務：
   ```bash
   sudo systemctl stop litton7-internal
   ```

2. 更新代碼或配置文件

3. 重新部署：
   ```bash
   sudo ./deploy.sh
   ```

如果只需更新環境變數，可以：

1. 編輯 `/opt/litton7-internal/.env` 文件
2. 重啟服務：
   ```bash
   sudo systemctl restart litton7-internal
   ```

## 卸載

使用 root 權限執行 `uninstall.sh` 腳本：

```bash
sudo ./uninstall.sh
```

此腳本將：
- 停止 `litton7-internal` 服務
- 移除相關的 Docker 映像檔
- 刪除系統服務文件
- 移除 `/opt/litton7-internal/` 目錄

注意：此腳本不會刪除用戶 `lclwebservice`，因為該用戶也被實驗室中的其他服務使用。

## 故障排除

### 服務無法啟動

檢查服務狀態和日誌：

```bash
sudo systemctl status litton7-internal
sudo journalctl -u litton7-internal
```

### Docker 容器問題

檢查 Docker 容器狀態：

```bash
docker ps -a | grep litton7-internal
```

查看 Docker 容器日誌：

```bash
docker logs litton7-internal
```

### 重置失敗的服務

如果服務處於失敗狀態，可以重置：

```bash
sudo systemctl reset-failed litton7-internal
sudo systemctl restart litton7-internal
``` 