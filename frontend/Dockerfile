# 第一阶段：Node.js 编译打包
FROM node:22-alpine as build-stage
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# 第二阶段：Nginx 部署静态文件
FROM nginx:alpine as production-stage
# 将打包好的 dist 文件复制到 Nginx 的默认静态目录
COPY --from=build-stage /app/dist /usr/share/nginx/html
# 替换默认的 Nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]