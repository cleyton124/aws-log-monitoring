#!/bin/bash

# Configurações de diretório e S3
LOG_DIR="$HOME/logs_locais"
BUCKET_NAME="bucket-log-553547825"
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
ARCHIVE_NAME="log_${TIMESTAMP}.tar.gz"

mkdir -p "$LOG_DIR"

# Simula o arquivo de log para a pasta local
cp erro_teste.log "$LOG_DIR/app.log" 2>/dev/null || echo "FATAL ERROR: Falha de conexão com o banco de dados" > "$LOG_DIR/app.log"

echo "Compactando arquivo de log..."
tar -czf "$LOG_DIR/$ARCHIVE_NAME" -C "$LOG_DIR" app.log

echo "Enviando para o S3..."
aws s3 cp "$LOG_DIR/$ARCHIVE_NAME" "s3://$BUCKET_NAME/logs/$ARCHIVE_NAME"

echo "Processo de rotação concluído com sucesso!"
