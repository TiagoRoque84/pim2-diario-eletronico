import shutil
import os

origem = "pim2.db"
destino = "backup.db"

if not os.path.exists(origem):
    print("Erro: Arquivo pim2.db não encontrado!")
else:
    shutil.copy2(origem, destino)
    print("Backup realizado com sucesso!")
    print("Arquivo salvo como:", destino)
