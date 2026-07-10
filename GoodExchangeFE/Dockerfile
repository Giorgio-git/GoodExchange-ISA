# ——— STAGE 1: Build & Dependencies ———
# Riferimento Corso: Sezione 4356 "Dockerfile multistage"
FROM node:20-alpine AS builder

WORKDIR /app

# Copia dei file delle dipendenze per sfruttare la cache dei layer Docker
COPY package*.json ./

# Installazione pulita delle dipendenze Node.js
RUN npm install

# Copia di tutto il codice sorgente del Frontend Angular
COPY . .

# Esecuzione della compilazione di produzione
RUN npm run build

# ——— STAGE 2: Runtime Minimal Web Server ———
FROM nginx:alpine AS runtime

# Rimuove la configurazione e la pagina di default di NGINX
RUN rm -rf /usr/share/nginx/html/*

# Copia la configurazione personalizzata per la Single Page Application
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copia i file statici HTML/JS/CSS generati nello Stage 1
# Con il nuovo Application Builder di Angular 19, i file client si trovano nella cartella browser
COPY --from=builder /app/dist/good-exchange-fe/browser /usr/share/nginx/html

# Garantisce che index.csr.html sia accessibile come index.html di default per NGINX
RUN if [ -f /usr/share/nginx/html/index.csr.html ]; then cp /usr/share/nginx/html/index.csr.html /usr/share/nginx/html/index.html; fi

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
