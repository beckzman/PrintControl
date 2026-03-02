# Stage 1: Build the Angular app
FROM node:22-alpine AS build
WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm install

# Copy source and build
COPY . .
RUN npm run build -- --configuration production

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Copy custom Nginx configuration to proxy /api and handle SPA routing
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy build artifacts to Nginx
# Angular 17+ with @angular/build:application usually outputs to dist/<project-name>/browser
# If it outputs just to dist/frontend, Nginx will fail. We'll verify this during build or just copy the whole directory content using wildcards or specific path
COPY --from=build /app/dist/frontend/browser /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
