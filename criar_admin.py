from data.repo import administrador_repo
from data.model.administrador_model import Administrador
from util.security import criar_hash_senha


def criar_admin_inicial():
    """
    Função que cria um usuário administrador inicial, se ainda não existir.
    """
    try:
        admins = administrador_repo.obter_todos_administradores()
        print(f"🔍 Verificando administradores existentes... Encontrados: {len(admins)}")
    except Exception as e:
        print("❌ Erro ao acessar o banco de dados!")
        print(f"💡 Erro: {str(e)}")
        print("⚠️  Você precisa executar primeiro a migração do banco de dados (provavelmente 'python criar_banco.py')")
        return False

    if not admins:
        print("🚀 Criando primeiro administrador...")
        senha_hash = criar_hash_senha("admin123")
        print("✅ Senha criptografada gerada")
        admin = Administrador(
            id=None,
            email="admin@ifes.com",
            senha=senha_hash,  
        )

        admin_id = administrador_repo.inserir_administrador(admin)

        if admin_id:
            print("\n🎉 ADMIN CRIADO COM SUCESSO!")
            print("=" * 40)
            print("📧 Email: admin@ifes.com")
            print("🔑 Senha: admin123")
            print("=" * 40)
            print("⚠️  IMPORTANTE: Altere a senha após o primeiro login!")
            print("\n🌐 Acesse: http://localhost:8000/admin")
            return True
        else:
            print("❌ Erro ao inserir admin no banco!")
            return False
    else:
        print("ℹ️  ADMIN JÁ EXISTE!")
        print("=" * 40)
        for admin in admins:
            print(f"📧 Email: {admin.email}")
        print("=" * 40)
        print("🌐 Acesse: http://localhost:8000/admin")
        return False

if __name__ == "__main__":
    print("🔐 CRIADOR DE ADMINISTRADOR - IFES Ciência")
    print("=" * 50)
    criar_admin_inicial()