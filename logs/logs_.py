import logging
import os

def logging_():
    """Configuração centralizada de logging para toda a aplicação"""
    
    logging.getLogger("azure").setLevel(logging.ERROR)
    logging.getLogger("azure.core").setLevel(logging.ERROR)
    logging.getLogger("azure.core.pipeline").setLevel(logging.ERROR)
    logging.getLogger("azure.core.pipeline.policies").setLevel(logging.ERROR)
    logging.getLogger("httpx").setLevel(logging.ERROR)
    logging.getLogger("httpcore").setLevel(logging.ERROR)
    
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
    
    os.makedirs("logs", exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler("logs/app.log", encoding='utf-8'),
            logging.StreamHandler()
        ],
        force=True 
    )
    
    return logging.getLogger("arruda_consulting")