from typing import Optional
from fastapi import FastAPI, Request, Form, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import os
import shutil
import html
from datetime import datetime



# Importações dos repositórios e modelos
from data.repo import administrador_repo, integrante_repo, experimento_repo
from data.model.integrante_model import Integrante
from data.model.experimento_model import Experimento
from util.security import verificar_senha
from criar_admin import criar_admin_inicial

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="uma-chave-secreta-bem-forte")

# Diretórios
uploads_dir = "uploads"
static_dir = "static"
os.makedirs(uploads_dir, exist_ok=True)
os.makedirs(static_dir, exist_ok=True)

# Templates com filtros personalizados
templates = Jinja2Templates(directory="templates")

# Adiciona filtro personalizado para sanitizar HTML
def sanitize_html(text):
    """Sanitiza HTML básico mantendo apenas tags seguras"""
    if not text:
        return ""
    
    # Lista de tags permitidas para formatação básica
    allowed_tags = [
        'p', 'br', 'strong', 'b', 'em', 'i', 'u', 's', 'strike',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li',
        'blockquote',
        'a', 'span', 'div'
    ]
    
    # Aqui você pode implementar uma sanitização mais robusta usando bibliotecas como bleach
    # Por agora, retornamos o texto como está (assumindo que vem do editor controlado)
    return text

# Adiciona o filtro ao Jinja2
templates.env.filters['sanitize_html'] = sanitize_html

# Monta as pastas estáticas
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Funções utilitárias
def get_flash_messages(request: Request):
    return request.session.pop("flash_messages", [])

def verificar_login_admin(request: Request):
    if not request.session.get("admin_logado"):
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail="Não autorizado",
            headers={"Location": "/login_admin"}
        )

def sanitizar_conteudo_html(conteudo: str) -> str:
    """
    Sanitiza o conteúdo HTML recebido do editor
    Remove scripts maliciosos e mantém apenas formatação básica
    """
    if not conteudo:
        return ""
    
    # Remove tags script e style por segurança
    conteudo = conteudo.replace('<script', '&lt;script').replace('</script>', '&lt;/script&gt;')
    conteudo = conteudo.replace('<style', '&lt;style').replace('</style>', '&lt;/style&gt;')
    
    # Remove atributos on* (onclick, onload, etc.) por segurança
    import re
    conteudo = re.sub(r'\s+on\w+\s*=\s*["\'][^"\']*["\']', '', conteudo, flags=re.IGNORECASE)
    
    return conteudo

# FAVICON #
@app.get("/favicon.ico")
async def favicon():
    return RedirectResponse(url="/static/style/css/favicon.ico")


# --- LOGIN/LOGOUT ADMIN ---

@app.get("/login_admin", response_class=HTMLResponse)
async def login_admin(request: Request):
    context = {
        "request": request,
        "erro": get_flash_messages(request),
    }
    return templates.TemplateResponse("/admin/login_admin.html", context)

@app.post("/login_admin", response_class=RedirectResponse)
async def processar_login_admin(request: Request, email: str = Form(...), senha: str = Form(...)):
    admin = administrador_repo.obter_administrador_por_email(email)
    if admin and verificar_senha(senha, admin.senha):
        request.session["admin_logado"] = True
        request.session.setdefault("flash_messages", []).append({"message": "Login bem-sucedido!", "type": "success"})
        return RedirectResponse(url="/admin/integrantes", status_code=status.HTTP_303_SEE_OTHER)
    else:
        request.session.setdefault("flash_messages", []).append({"message": "Email ou senha inválidos.", "type": "danger"})
        return RedirectResponse(url="/login_admin", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/admin/logout", response_class=RedirectResponse)
async def logout_admin(request: Request):
    request.session.pop("admin_logado", None)
    request.session.setdefault("flash_messages", []).append({"message": "Você saiu da área de administrador.", "type": "info"})
    return RedirectResponse(url="/login_admin", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/admin", response_class=RedirectResponse)
async def admin_dashboard(request: Request, _=Depends(verificar_login_admin)):
    return RedirectResponse(url="/admin/integrantes", status_code=status.HTTP_303_SEE_OTHER)


# --- UPLOAD DE IMAGENS PARA EDITOR ---

@app.post("/admin/upload_image")
async def upload_image(request: Request, file: UploadFile = File(...), _=Depends(verificar_login_admin)):
    """Upload de imagens para o editor de texto rico"""
    # Verifica se é uma imagem
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Apenas arquivos de imagem são permitidos.")

    # Gera nome único para evitar conflitos
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"editor_img_{timestamp}{file_extension}"
    
    file_path = os.path.join(uploads_dir, unique_filename)
    
    try:
        # Salva o arquivo
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Retorna a URL pública para o editor
        url = f"/static/{unique_filename}"
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao fazer upload da imagem: {str(e)}")

# --- ADMIN INTEGRANTES ---

@app.get("/admin/integrantes", response_class=HTMLResponse)
async def listar_integrantes(request: Request, _=Depends(verificar_login_admin)):
    integrantes = integrante_repo.obter_todos_integrantes()
    return templates.TemplateResponse("/admin/admin_dashboard.html", {
        "request": request,
        "integrantes": integrantes,
        "flash_messages": get_flash_messages(request)
    })

@app.post("/admin/integrantes", response_class=RedirectResponse)
async def adicionar_integrante(
    request: Request,
    nome: str = Form(...),
    turma: str = Form(...),
    funcao: str = Form(...),
    foto_file: UploadFile = File(...),
    redes_sociais: Optional[str] = Form(None),
    _=Depends(verificar_login_admin)
):
    if not foto_file or not foto_file.filename:
        request.session.setdefault("flash_messages", []).append({"message": "A foto do integrante é obrigatória.", "type": "danger"})
        return RedirectResponse(url="/admin/integrantes", status_code=status.HTTP_303_SEE_OTHER)

    file_path = os.path.join(uploads_dir, foto_file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(foto_file.file, buffer)
    foto_url = f"/uploads/{foto_file.filename}"

    novo_integrante = Integrante(id=None, nome=nome, turma=turma, funcao=funcao, foto=foto_url, redes_sociais=redes_sociais)
    integrante_repo.inserir_integrante(novo_integrante)

    request.session.setdefault("flash_messages", []).append({"message": "Integrante adicionado com sucesso!", "type": "success"})
    return RedirectResponse(url="/admin/integrantes", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/admin/integrantes/editar/{id_integrante}", response_class=RedirectResponse)
async def editar_integrante(
    request: Request,
    id_integrante: int,
    nome: str = Form(...),
    turma: str = Form(...),
    funcao: str = Form(...),
    foto_file: Optional[UploadFile] = File(None),
    redes_sociais: Optional[str] = Form(None),
    _=Depends(verificar_login_admin)
):
    integrante = integrante_repo.obter_integrante_por_id(id_integrante)
    if not integrante:
        request.session.setdefault("flash_messages", []).append({"message": "Integrante não encontrado.", "type": "danger"})
        return RedirectResponse(url="/admin/integrantes", status_code=status.HTTP_303_SEE_OTHER)

    foto_url = integrante.foto
    if foto_file and foto_file.filename:
        file_path = os.path.join(uploads_dir, foto_file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(foto_file.file, buffer)
        foto_url = f"/uploads/{foto_file.filename}"

    integrante_atualizado = Integrante(id=id_integrante, nome=nome, turma=turma, funcao=funcao, foto=foto_url, redes_sociais=redes_sociais)
    integrante_repo.alterar_integrante(integrante_atualizado)

    request.session.setdefault("flash_messages", []).append({"message": "Integrante atualizado com sucesso!", "type": "success"})
    return RedirectResponse(url="/admin/integrantes", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/admin/integrantes/excluir/{id_integrante}", response_class=RedirectResponse)
async def excluir_integrante(request: Request, id_integrante: int, _=Depends(verificar_login_admin)):
    integrante = integrante_repo.obter_integrante_por_id(id_integrante)
    if integrante and integrante.foto:
        try:
            file_name = integrante.foto.split("/")[-1]
            os.remove(os.path.join(uploads_dir, file_name))
        except OSError:
            pass
    integrante_repo.excluir_integrante(id_integrante)
    request.session.setdefault("flash_messages", []).append({"message": "Integrante excluído!", "type": "success"})
    return RedirectResponse(url="/admin/integrantes", status_code=status.HTTP_303_SEE_OTHER)

# --- ADMIN EXPERIMENTOS ---

@app.get("/admin/experimentos", response_class=HTMLResponse)
async def listar_experimentos(request: Request, _=Depends(verificar_login_admin)):
    experimentos = experimento_repo.obter_todos_experimentos()
    return templates.TemplateResponse("/admin/experimentos_dashboard.html", {
        "request": request,
        "experimentos": experimentos,
        "flash_messages": get_flash_messages(request)
    })

@app.post("/admin/experimentos", response_class=RedirectResponse)
async def adicionar_experimento(
    request: Request,
    titulo: str = Form(...),
    descricao: str = Form(...),
    materiais: str = Form(...),
    capa_file: UploadFile = File(...),
    video_explicativo: Optional[str] = Form(None),
    _=Depends(verificar_login_admin)
):
    # Sanitiza o conteúdo HTML
    descricao_sanitizada = sanitizar_conteudo_html(descricao)
    materiais_sanitizados = sanitizar_conteudo_html(materiais)
    
    # Valida se o arquivo de capa foi enviado
    if not capa_file or not capa_file.filename:
        request.session.setdefault("flash_messages", []).append({"message": "A capa do experimento é obrigatória.", "type": "danger"})
        return RedirectResponse(url="/admin/experimentos", status_code=status.HTTP_303_SEE_OTHER)
    
    # Salva a capa
    file_path = os.path.join(uploads_dir, capa_file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(capa_file.file, buffer)
    capa_url = f"/uploads/{capa_file.filename}"

    # Cria o experimento com conteúdo sanitizado
    novo_experimento = Experimento(
        id=None, 
        titulo=titulo, 
        descricao=descricao_sanitizada, 
        materiais=materiais_sanitizados, 
        capa=capa_url, 
        video_explicativo=video_explicativo
    )
    experimento_repo.inserir_experimento(novo_experimento)

    request.session.setdefault("flash_messages", []).append({"message": "Experimento adicionado com sucesso!", "type": "success"})
    return RedirectResponse(url="/admin/experimentos", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/admin/experimentos/editar/{id_experimento}", response_class=RedirectResponse)
async def editar_experimento(
    request: Request,
    id_experimento: int,
    titulo: str = Form(...),
    descricao: str = Form(...),
    materiais: str = Form(...),
    capa_file: Optional[UploadFile] = File(None),
    video_explicativo: Optional[str] = Form(None),
    _=Depends(verificar_login_admin)
):
    # Busca o experimento existente
    experimento = experimento_repo.obter_experimento_por_id(id_experimento)
    if not experimento:
        request.session.setdefault("flash_messages", []).append({"message": "Experimento não encontrado.", "type": "danger"})
        return RedirectResponse(url="/admin/experimentos", status_code=status.HTTP_303_SEE_OTHER)
    
    # Sanitiza o conteúdo HTML
    descricao_sanitizada = sanitizar_conteudo_html(descricao)
    materiais_sanitizados = sanitizar_conteudo_html(materiais)
    
    # Atualiza a capa se uma nova foi enviada
    capa_url = experimento.capa
    if capa_file and capa_file.filename:
        file_path = os.path.join(uploads_dir, capa_file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(capa_file.file, buffer)
        capa_url = f"/uploads/{capa_file.filename}"

    # Atualiza o experimento
    experimento_atualizado = Experimento(
        id=id_experimento, 
        titulo=titulo, 
        descricao=descricao_sanitizada, 
        materiais=materiais_sanitizados, 
        capa=capa_url, 
        video_explicativo=video_explicativo
    )
    experimento_repo.alterar_experimento(experimento_atualizado)

    request.session.setdefault("flash_messages", []).append({"message": "Experimento atualizado com sucesso!", "type": "success"})
    return RedirectResponse(url="/admin/experimentos", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/admin/experimentos/excluir/{id_experimento}", response_class=RedirectResponse)
async def excluir_experimento(request: Request, id_experimento: int, _=Depends(verificar_login_admin)):
    experimento = experimento_repo.obter_experimento_por_id(id_experimento)
    if experimento and experimento.capa:
        try:
            file_name = experimento.capa.split("/")[-1]
            os.remove(os.path.join(uploads_dir, file_name))
        except OSError:
            pass
    experimento_repo.excluir_experimento(id_experimento)
    request.session.setdefault("flash_messages", []).append({"message": "Experimento excluído!", "type": "success"})
    return RedirectResponse(url="/admin/experimentos", status_code=status.HTTP_303_SEE_OTHER)

# --- CLIENTE ---

# Adiciona uma rota de redirecionamento para evitar o erro 404
@app.get("/cliente/integrantes", response_class=RedirectResponse)
async def redirect_integrantes():
    return RedirectResponse(url="/cliente/sobre_nos", status_code=301)

@app.get("/", response_class=HTMLResponse)
async def index_cliente(request: Request):
    info_projeto = {
        "titulo": "Sobre o Projeto IFES Ciência",
        "texto": "O projeto 'IFES Ciência', iniciado em setembro de 2024, visa apresentar experiências científicas curiosas. A equipe produz conteúdo antecipadamente, e cada vídeo leva cerca de 15 dias para ser finalizado. O projeto já ganhou destaque nacional por sua qualidade e dedicação.",
    }
    return templates.TemplateResponse("/cliente/index.html", {
        "request": request,
        "info_projeto": info_projeto,
        "flash_messages": get_flash_messages(request)
    })

@app.get("/cliente/sobre_nos", response_class=HTMLResponse)
async def sobre_nos_cliente(request: Request):
    integrantes = integrante_repo.obter_todos_integrantes()
    return templates.TemplateResponse("/cliente/sobre_nos.html", {
        "request": request,
        "integrantes": integrantes,
        "flash_messages": get_flash_messages(request)
    })

@app.get("/cliente/experimentos", response_class=HTMLResponse)
async def experimentos_cliente(request: Request):
    experimentos = experimento_repo.obter_todos_experimentos()
    return templates.TemplateResponse("/cliente/experimentos.html", {
        "request": request,
        "experimentos": experimentos,
        "flash_messages": get_flash_messages(request)
    })

@app.get("/cliente/experimentos/{id_experimento}", response_class=HTMLResponse)
async def detalhes_experimento(request: Request, id_experimento: int):
    experimento = experimento_repo.obter_experimento_por_id(id_experimento)
    if not experimento:
        request.session.setdefault("flash_messages", []).append({
            "message": "Experimento não encontrado.",
            "type": "danger"
        })
        return RedirectResponse(url="/cliente/experimentos", status_code=status.HTTP_303_SEE_OTHER)
    
    return templates.TemplateResponse("/cliente/detalhes_experimento.html", {
        "request": request,
        "experimento": experimento,
        "flash_messages": get_flash_messages(request)
    })

# --- Startup ---
@app.on_event("startup")
async def startup_event():
    criar_admin_inicial()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)