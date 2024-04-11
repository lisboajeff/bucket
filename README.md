# Projeto

# Sincronização de Certificados com S3

## Descrição
O script `bucket.py` é uma ferramenta de linha de comando desenvolvida para automatizar o processo de sincronização de certificados `.pem` e `.crt` com um bucket AWS S3. Essencial para manter a segurança e a integridade da comunicação em infraestruturas distribuídas, este script garante que os certificados necessários estejam sempre atualizados e acessíveis no ambiente AWS.

## Funcionalidades
- **Sincronização Automatizada:** Compara certificados locais com os armazenados no S3, realizando upload ou remoção conforme necessário para manter a sincronia.
- **Geração de Relatório:** Cria um relatório em formato Markdown (`s3_sync_report.md`) detalhando as ações realizadas durante a sincronização, incluindo quais arquivos foram adicionados ou removidos.
- **Hash de Verificação:** Utiliza hash SHA-256 para verificar a integridade dos arquivos e determinar a necessidade de sincronização.
- **Flexibilidade de Uso:** Permite a especificação de diferentes ambientes e países para a sincronização de certificados, aumentando a aplicabilidade em cenários multi-regionais.

## Pré-Requisitos
Para utilizar este script, é necessário ter instalado:
- Python 3
- Boto3 (SDK da AWS para Python)

Além disso, é preciso configurar as credenciais da AWS (AWS Access Key ID e AWS Secret Access Key), preferencialmente através do AWS CLI ou arquivo de configuração da AWS.

## Como Usar
1. **Configuração de Ambiente:**
   Certifique-se de que as variáveis de ambiente `AWS_REGION`, `BUCKET_NAME`, `TRUSTSTORE` e `TLS` estejam devidamente configuradas para refletir sua infraestrutura AWS.

2. **Para executar o script, use o seguinte comando:**

```bash
PAIS="Brasil"
AMBIENTE="DEV"
CERTIFICATE="env/$PAIS/$AMBIENTE/certificates"
bash src/generate.sh "projeto.corp" $CERTIFICATE/ssl "crt"
bash src/generate.sh "client" $CERTIFICATE/truststore "pem"
bash src/local.sh "$PAIS" "$AMBIENTE"
rm s3_sync_report.md
```