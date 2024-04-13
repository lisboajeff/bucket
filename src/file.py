import os
import hashlib

class Device:

    def __init__(self, actions: dict[str], path: str) -> None:
        self.actions = actions
        self.path = path

    def write_summary_to_file(self, report_file):
        """Escreve o resumo das ações em formato Markdown."""
        lines = []
        if not self.actions["Uploaded"] and not self.actions["Removed"]:
            lines.append("Nenhum arquivo foi adicionado ou removido.")
        else:
            lines.append("| Ação       | Nome do Arquivo |")
            lines.append("|------------|-----------------|")
            for filename in self.actions["Uploaded"]:
                lines.append(f"| Uploaded    | {filename} |")
            for filename in self.actions["Removed"]:
                lines.append(f"| Removed     | {filename} |")

        with open(report_file, "w") as file:
            file.write("\n".join(lines))

    def calcular_hash_arquivo(self, full_path):
        sha256_hash = hashlib.sha256()
        with open(full_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def find_files(self, extension, folder=''):
    
        path=f'{self.path}/{folder}'

        files_with_hash = {}

        if not os.path.exists(path) or not os.listdir(path):
            return files_with_hash
        
        for f in os.listdir(path):
            if f.endswith(extension) and os.path.isfile(os.path.join(path, f)):
                full_path = os.path.join(path, f)
                file_hash = self.calcular_hash_arquivo(full_path)
                # Use o caminho relativo do arquivo como chave para evitar conflitos de nome
                files_with_hash[full_path] = {'hash': file_hash, 'virtual_path': f'{folder}/{os.path.basename(full_path)}'}

        return files_with_hash

