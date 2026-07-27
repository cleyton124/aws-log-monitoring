# 🚀 Sistema Automatizado de Monitoramento, Métricas e Alertas de Logs Serverless

---

## 📌 Contexto do Problema

Recentemente, atuei em um cenário crítico de observabilidade. A empresa enfrentava falhas intermitentes e silenciosas em suas aplicações hospedadas em instâncias **Amazon EC2**. Os logs do sistema eram armazenados localmente e comprimidos em formato `.tar.gz`, permanecendo isolados nas instâncias.

Isso gerava dois grandes gargalos de negócio:

1. **Falta de visibilidade em tempo real:** A equipe de SysOps só descobria que um serviço havia caído quando o cliente final abria um chamado de suporte.
2. **Processo manual e ineficiente:** Para diagnosticar falhas, era necessário acessar manualmente o servidor via SSH, buscar o arquivo `.tar.gz` mais recente, descompactá-lo e analisar milhares de linhas de log à procura de erros.

**O objetivo principal:** Construir uma solução $100\%$ automatizada, resiliente e *serverless* que ingerisse esses arquivos comprimidos, extraísse falhas críticas (`FATAL ERROR`) em tempo real e notificasse a equipe de engenharia em questão de minutos, antes que o impacto atingisse os clientes finais.

---

## 📐 Arquitetura da Solução

O fluxo foi desenhado utilizando o princípio do menor privilégio (IAM) e uma arquitetura orientada a eventos para garantir custo zero quando não houver processamento (*pay-per-use*):

```text
[ EC2 (Script Bash) ] 
       │
       ▼ (1. Compressão e Upload para S3 via AWS CLI)
[ Amazon S3 ]
       │
       ▼ (2. Gatilho s3:ObjectCreated:* na pasta /logs)
[ AWS Lambda ]
       │
       ▼ (3. Leitura do .tar.gz em memória & Envio de Métrica)
[ Amazon CloudWatch ]
       │
       ▼ (4. Avaliação do Alarme por Soma de Eventos)
[ Amazon SNS ]
       │
       ▼ (5. Notificação Crítica)
[ Equipe de Engenharia / SysOps ]

```

---

## ⚡ Desafios Encontrados e Como Foram Resolvidos

Durante o desenvolvimento e homologação da arquitetura, enfrentei e superei desafios técnicos complexos:

### 1. Descompactação e Leitura do `.tar.gz` Sem Impactar Performance

* **Desafio:** O AWS Lambda possui limitações de espaço em disco no diretório temporário (`/tmp`) e o download físico de arquivos compactados pesados aumentaria o tempo de execução (latência) e os custos.
* **Solução:** Implementei o processamento do arquivo totalmente **em memória** utilizando as bibliotecas `io.BytesIO` e `tarfile` em Python. O Lambda baixa o stream de dados do S3 e descompacta os arquivos diretamente no buffer de memória RAM, reduzindo drasticamente o tempo de execução e otimizando o uso do recurso.

### 2. Disparo de Alarmes Falsos-Negativos por Agregação Incorreta

* **Desafio:** Inicialmente, o alarme do CloudWatch não disparava mesmo após múltiplos arquivos de log com erros serem enviados em um curto espaço de tempo.
* **Solução:** Ao analisar os logs do CloudWatch, identifiquei que a estatística do alarme estava configurada por **Média (*Average*)**. Como o Lambda enviava a métrica individualmente por arquivo, a média permanecia baixa. Ajustei a regra de agregação do CloudWatch Alarm para **Soma (*Sum*)** dentro de uma janela temporal de 5 minutos, garantindo que o acúmulo de erros fosse contado com precisão matemática.

### 3. Comunicação Segura Entre Rede Pública e Serviços Gerenciados

* **Desafio:** Garantir que a instância EC2 (localizada dentro da Subnet Pública da VPC) conseguisse enviar dados ao S3 e que o S3 invocasse o Lambda com permissões estritas.
* **Solução:** Configurei políticas de recursos (*Resource-based policies*) no Lambda permitindo apenas o escopo `lambda:InvokeFunction` vindo do ARN do bucket de origem, além de estruturar permissões de execução IAM alinhadas aos padrões de segurança da AWS.

---

## 🛠️ Tecnologias e Ferramentas Utilizadas

| Categoria | Ferramenta / Serviço | Aplicação no Projeto |
| --- | --- | --- |
| **Compute / OS** | **Amazon EC2** | Servidor Linux hospedando a aplicação e gerando logs de sistema. |
| **Automation** | **Bash / Shell Script** | Script customizado para rotação, compressão e upload automatizado de logs. |
| **Storage** | **Amazon S3** | *Data Lake* de ingestão segura de arquivos comprimidos (`.tar.gz`). |
| **Serverless** | **AWS Lambda (Python 3.x)** | Processamento orientado a eventos, extração em memória e cálculo de métricas. |
| **Observability** | **Amazon CloudWatch** | Gestão de logs, métricas personalizadas (`Namespace: SysOps/Logs`) e alarmes. |
| **Messaging** | **Amazon SNS** | Tópico de notificação push para alertas de e-mail em tempo real. |
| **Security** | **AWS IAM** | Controle de acesso baseado em papéis (*Roles*) e políticas de recurso. |

---
