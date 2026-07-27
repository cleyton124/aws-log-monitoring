import urllib.parse
import tarfile
import io
import boto3

s3_client = boto3.client('s3')
cloudwatch_client = boto3.client('cloudwatch')

def lambda_handler(event, context):
    # Obtém o nome do bucket e da chave do objeto enviado via evento S3
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    
    try:
        # Busca o arquivo compactado no S3
        response = s3_client.get_object(Bucket=bucket, Key=key)
        buffer = io.BytesIO(response['Body'].read())
        
        erros_encontrados = 0
        
        # Descompacta e lê o arquivo em memória
        with tarfile.open(fileobj=buffer, mode="r:gz") as tar:
            for member in tar.getmembers():
                f = tar.extractfile(member)
                if f is not None:
                    content = f.read().decode('utf-8')
                    for line in content.splitlines():
                        if "FATAL ERROR" in line:
                            erros_encontrados += 1
                            
        print(f"Processamento concluído. Total de erros críticos: {erros_encontrados}")
        
        # Publica a Métrica Personalizada no CloudWatch
        cloudwatch_client.put_metric_data(
            Namespace='SysOps/Logs',
            MetricData=[
                {
                    'MetricName': 'FatalErrorCount',
                    'Value': erros_encontrados,
                    'Unit': 'Count'
                },
            ]
        )
        
        return {
            'statusCode': 200,
            'body': f'Sucesso! {erros_encontrados} erros reportados ao CloudWatch.'
        }

    except Exception as e:
        print(f"Erro ao processar o arquivo {key} do bucket {bucket}: {str(e)}")
        raise e
