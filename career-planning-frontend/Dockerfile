# ---- 构建阶段 ----
FROM node:22-alpine AS build

WORKDIR /app

# 先复制依赖文件，利用 Docker 缓存层
COPY package.json ./

# 配置淘宝镜像并安装依赖
RUN npm config set registry https://registry.npmmirror.com && npm install

# 复制源码
COPY . .

# 构建生产包（跳过 type-check，仅执行 vite build）
RUN npm run build-only

# ---- 生产阶段 ----
FROM nginx:alpine AS production

# 复制自定义 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 将构建产物复制到 Nginx 静态资源目录
COPY --from=build /app/dist /usr/share/nginx/html

# 暴露 80 端口
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
