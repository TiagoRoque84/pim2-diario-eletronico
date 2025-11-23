#include <iostream>
#include <fstream>
#include <filesystem>

namespace fs = std::filesystem;

int main() {
    std::string origem = "pim2.db";
    std::string destino = "backup.db";

    if (!fs::exists(origem)) {
        std::cout << "Erro: Arquivo pim2.db não encontrado!" << std::endl;
        return 1;
    }

    try {
        fs::copy_file(origem, destino, fs::copy_options::overwrite_existing);
        std::cout << "Backup realizado com sucesso!" << std::endl;
        std::cout << "Arquivo salvo como: " << destino << std::endl;
    }
    catch (std::exception &e) {
        std::cout << "Erro ao copiar: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
