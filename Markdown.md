# API_Roto
============

Como activar el servicio de API en AWS

## Abrir consola en el proyecto VS COe o Cursor
Conectarse con el servidor EC2 de AWS por SSH.
 ![Comando:](C:\Users\gusta\Documents\Proyectos\Markdown\SSH_Conection.png)

 nohup uvicorn app:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &


# Activar el entorno virtual
source venv/bin/activate

# Iniciar la aplicación en segundo plano
nohup uvicorn app:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &

# Verificar que está corriendo
ps aux | grep uvicorn

# Ver los logs si es necesario
tail -f app.log