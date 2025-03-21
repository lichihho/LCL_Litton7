# LCLab's Litton7 Public Demo Proxy Server for Synology v.0.0.0

Represent LaDeco demo Gradio server from internal IP address to Synology NAS.
Used on iframe HTML tag showcase in LCLab's official site.

For example: visit `https://lclab.thu.edu.tw:8995` to get service on LAN `http://192.168.1.252:8083`.


## Deploy

1. Copy entries in this directory to `/volume1/docker/SynologyLitton7Proxy/` (if not exists, create one)
2. Open 'Container manager' on Synology DSM
3. Click '專案'
4. Name the Project name as 'LaDeco-Public-Proxy'
5. Set '路徑' as `/volume1/docker/SynologyLitton7Proxy/`
6. Comfirm '使用現有的 docker-compose.yml 來建立專案'
7. Click '下一步' (ignore '建立網頁入口' option) 
8. Click '建立'
