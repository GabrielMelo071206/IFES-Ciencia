from typing import Optional, List
from fastapi import FastAPI, Request, Form, Depends, HTTPException, status, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles
import shutil
import os

# Importações dos repositórios
from data.repo import administrador_repo, integrante_repo, experimento_repo
from data.model.integrante_model import Integrante
from data.model.experimento_model import Experimento
from util.security import verificar_senha
from criar_admin import criar_admin_inicial

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="uma-chave-secreta-bem-forte")

# CRIA AS PASTAS DE UPLOADS E STATIC
uploads_dir = "uploads"
static_dir = "static"
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

templates = Jinja2Templates(directory="templates")
# Monta as pastas para ser acessível publicamente na URL
app.mount("/static", StaticFiles(directory=uploads_dir), name="uploads")
app.mount("/static_css", StaticFiles(directory=static_dir), name="static_css")


def get_flash_messages(request: Request):
    return request.session.pop("flash_messages", [])

def verificar_login_admin(request: Request):
    if not request.session.get("admin_logado"):
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail="Não autorizado",
            headers={"Location": "/login_admin"}
        )

# --- Rotas para o Sistema (Login/Logout) ---

# A rota principal agora renderiza a página de cliente diretamente
@app.get("/", response_class=HTMLResponse)
async def inicio_cliente(request: Request):
    info_projeto = {
        "titulo": "Sobre o Projeto IFES Ciência",
        "texto": "O projeto 'Ifes Ciência' do campus Cachoeiro, iniciado em setembro de 2024, mostra experiências científicas curiosas e tem alcançado destaque nacional. A equipe consegue manter uma frequência de postagens constante, pois a maior parte do conteúdo é gravada com antecedência, com a produção de cada vídeo levando cerca de 15 dias.",
    }
    context = {
        "request": request,
        "info_projeto": info_projeto,
        "flash_messages": get_flash_messages(request),
    }
    return templates.TemplateResponse("/cliente/index.html", context)

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
        request.session.setdefault("flash_messages", []).append({"message": "Email ou senha inválidos. Tente novamente.", "type": "danger"})
        return RedirectResponse(url="/login_admin", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/admin/logout", response_class=RedirectResponse)
async def logout_admin(request: Request):
    request.session.pop("admin_logado", None)
    request.session.setdefault("flash_messages", []).append({"message": "Você saiu da área de administrador.", "type": "info"})
    return RedirectResponse(url="/login_admin", status_code=status.HTTP_303_SEE_OTHER)

# --- Rotas para Administrador (CRUD) ---

@app.get("/admin/integrantes", response_class=HTMLResponse)
async def listar_integrantes(request: Request, _=Depends(verificar_login_admin)):
    integrantes = integrante_repo.obter_todos_integrantes()
    context = {
        "request": request,
        "integrantes": integrantes,
        "flash_messages": get_flash_messages(request),
    }
    return templates.TemplateResponse("/admin/admin_dashboard.html", context)

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
        
    foto_url = f"/static/{foto_file.filename}"
    
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
    integrante_existente = integrante_repo.obter_integrante_por_id(id_integrante)
    if not integrante_existente:
        request.session.setdefault("flash_messages", []).append({"message": "Integrante não encontrado.", "type": "danger"})
        return RedirectResponse(url="/admin/integrantes", status_code=status.HTTP_303_SEE_OTHER)

    foto_url = integrante_existente.foto
    if foto_file and foto_file.filename:
        file_path = os.path.join(uploads_dir, foto_file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(foto_file.file, buffer)
        foto_url = f"/static/{foto_file.filename}"
        
    integrante_atualizado = Integrante(id=id_integrante, nome=nome, turma=turma, funcao=funcao, foto=foto_url, redes_sociais=redes_sociais)
    integrante_repo.alterar_integrante(integrante_atualizado)
    
    request.session.setdefault("flash_messages", []).append({"message": "Integrante atualizado com sucesso!", "type": "success"})
    return RedirectResponse(url="/admin/integrantes", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/admin/integrantes/excluir/{id_integrante}", response_class=RedirectResponse)
async def excluir_integrante(request: Request, id_integrante: int, _=Depends(verificar_login_admin)):
    integrante = integrante_repo.obter_integrante_por_id(id_integrante)
    if integrante and integrante.foto:
        try:
            file_name = integrante.foto.split('/')[-1]
            file_path = os.path.join(uploads_dir, file_name)
            os.remove(file_path)
        except OSError as e:
            print(f"Erro ao tentar remover a foto: {e.filename} - {e.strerror}")

    if integrante_repo.excluir_integrante(id_integrante):
        request.session.setdefault("flash_messages", []).append({"message": "Integrante excluído com sucesso!", "type": "success"})
    else:
        request.session.setdefault("flash_messages", []).append({"message": "Erro ao excluir integrante.", "type": "danger"})
        
    return RedirectResponse(url="/admin/integrantes", status_code=status.HTTP_303_SEE_OTHER)

# --- Rotas para Experimentos (CRUD) ---

@app.get("/admin/experimentos", response_class=HTMLResponse)
async def listar_experimentos(request: Request, _=Depends(verificar_login_admin)):
    experimentos = experimento_repo.obter_todos_experimentos()
    
    context = {
        "request": request,
        "experimentos": experimentos,
        "flash_messages": get_flash_messages(request),
    }
    return templates.TemplateResponse("/admin/experimentos_dashboard.html", context)


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
    if not capa_file or not capa_file.filename:
        request.session.setdefault("flash_messages", []).append({"message": "A capa do experimento é obrigatória.", "type": "danger"})
        return RedirectResponse(url="/admin/experimentos", status_code=status.HTTP_303_SEE_OTHER)

    file_path = os.path.join(uploads_dir, capa_file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(capa_file.file, buffer)
        
    capa_url = f"/static/{capa_file.filename}"
    
    novo_experimento = Experimento(id=None, titulo=titulo, descricao=descricao, materiais=materiais, capa=capa_url, video_explicativo=video_explicativo)
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
    experimento_existente = experimento_repo.obter_experimento_por_id(id_experimento)
    if not experimento_existente:
        request.session.setdefault("flash_messages", []).append({"message": "Experimento não encontrado.", "type": "danger"})
        return RedirectResponse(url="/admin/experimentos", status_code=status.HTTP_303_SEE_OTHER)

    capa_url = experimento_existente.capa
    if capa_file and capa_file.filename:
        file_path = os.path.join(uploads_dir, capa_file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(capa_file.file, buffer)
        capa_url = f"/static/{capa_file.filename}"
        
    experimento_atualizado = Experimento(id=id_experimento, titulo=titulo, descricao=descricao, materiais=materiais, capa=capa_url, video_explicativo=video_explicativo)
    experimento_repo.alterar_experimento(experimento_atualizado)
    
    request.session.setdefault("flash_messages", []).append({"message": "Experimento atualizado com sucesso!", "type": "success"})
    return RedirectResponse(url="/admin/experimentos", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/admin/experimentos/excluir/{id_experimento}", response_class=RedirectResponse)
async def excluir_experimento(request: Request, id_experimento: int, _=Depends(verificar_login_admin)):
    experimento = experimento_repo.obter_experimento_por_id(id_experimento)
    if experimento and experimento.capa:
        try:
            file_name = experimento.capa.split('/')[-1]
            file_path = os.path.join(uploads_dir, file_name)
            os.remove(file_path)
        except OSError as e:
            print(f"Erro ao tentar remover a capa: {e.filename} - {e.strerror}")

    if experimento_repo.excluir_experimento(id_experimento):
        request.session.setdefault("flash_messages", []).append({"message": "Experimento excluído com sucesso!", "type": "success"})
    else:
        request.session.setdefault("flash_messages", []).append({"message": "Erro ao excluir experimento.", "type": "danger"})
        
    return RedirectResponse(url="/admin/experimentos", status_code=status.HTTP_303_SEE_OTHER)

# --- Rotas para a Área do Cliente ---

# A rota de cliente agora pode ser acessada diretamente por sua URL
@app.get("/cliente", response_class=HTMLResponse)
async def inicio_cliente_route(request: Request):
    info_projeto = {
        "titulo": "Sobre o Projeto IFES Ciência",
        "texto": "O projeto 'Ifes Ciência' do campus Cachoeiro, iniciado em setembro de 2024, mostra experiências científicas curiosas e tem alcançado destaque nacional. A equipe consegue manter uma frequência de postagens constante, pois a maior parte do conteúdo é gravada com antecedência, com a produção de cada vídeo levando cerca de 15 dias.",
    }
    context = {
        "request": request,
        "info_projeto": info_projeto,
        "flash_messages": get_flash_messages(request),
    }
    return templates.TemplateResponse("/cliente/index.html", context)

@app.get("/cliente/sobre_nos", response_class=HTMLResponse)
async def sobre_nos_cliente(request: Request):
    integrantes = integrante_repo.obter_todos_integrantes()
    context = {
        "request": request,
        "integrantes": integrantes,
        "flash_messages": get_flash_messages(request),
    }
    return templates.TemplateResponse("/cliente/sobre_nos.html", context)

@app.get("/cliente/experimentos", response_class=HTMLResponse)
async def experimentos_cliente(request: Request):
    experimentos = experimento_repo.obter_todos_experimentos()
    context = {
        "request": request,
        "experimentos": experimentos,
        "flash_messages": get_flash_messages(request),
    }
    return templates.TemplateResponse("/cliente/experimentos.html", context)

# --- Eventos de Inicialização ---

@app.on_event("startup")
async def startup_event():
    criar_admin_inicial()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)