# Projeto

# Sincronizador de Certificados com AWS S3

Este script Python automatiza o processo de sincronização de certificados `.pem` e `.crt` com um bucket específico da AWS S3. Ele verifica os certificados locais contra os armazenados no S3, fazendo upload de novos ou modificados e removendo aqueles que não existem mais localmente.

## Dependências

* Python 3.6+
* boto3
* argparse
* hashlib

---

## Configuração

Antes de executar o script, configure as seguintes variáveis de ambiente:

- `AWS_REGION`: A região da AWS onde o bucket S3 está localizado.
- `BUCKET_NAME`: O nome do bucket S3 onde os certificados serão armazenados.
- `TRUSTSTORE`: O prefixo do caminho no bucket S3 para certificados `.pem`.
- `TLS`: O prefixo do caminho no bucket S3 para certificados `.crt`.

## Uso

Para executar o script, use o seguinte comando:

```bash
PAIS="Brasil"
AMBIENTE="DEV"
CERTIFICATE="env/$PAIS/$AMBIENTE/certificates"
bash generate.sh "projeto.corp" $CERTIFICATE/ssl "crt"
bash generate.sh "client" $CERTIFICATE/truststore "pem"
python3 src/bucket.py "$PAIS" "$AMBIENTE"
```