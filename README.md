# Agenda Barbe - Backend

API rest para Sistema de agendamento para barbearias desenvolvido com Django REST Framework.


## 👥 Autores

- Murilo Santos
- José Junior


## 🛠️ Tecnologias Utilizadas

### Backend
- Python
- Django 
- Django REST Framework
- PostgreSQL
- Swagger/OpenAPI para documentação

### Autenticação e Segurança
- Django REST Auth
- Django Allauth
- CORS Headers

### Armazenamento e Upload
- Supabase para armazenamento de imagens
- Pillow para processamento de imagens

### Documentação e API
- drf-yasg (Yet Another Swagger Generator)
- Django REST Swagger

## 📋 Pré-requisitos

- Python 3.x
- pip (gerenciador de pacotes Python)
- PostgreSQL
- Conta no Supabase (para armazenamento de imagens)

## 🔧 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/agenda-barbe.git
cd agenda-barbe
```

2. Crie um ambiente virtual e ative-o:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

5. Execute as migrações:
```bash
python manage.py migrate
```

6. Inicie o servidor:
```bash
python manage.py runserver
```

## 📚 Documentação da API

A documentação completa da API está disponível através do Swagger UI no link:
[https://back-end-agendabarbe.onrender.com/](https://back-end-agendabarbe.onrender.com/)

## 🔗 Endpoints por App

### Users App
- `POST /api/v1/auth/register/` - Registro de novos usuários
- `POST /api/v1/auth/login/` - Login de usuários
- `POST /api/v1/auth/logout/` - Logout de usuários
- `GET /api/v1/auth/profile/` - Obtém dados do usuário autenticado
- `GET /api/v1/auth/barbers/` - Lista todos os barbeiros
- `POST /api/v1/auth/ratings/` - Criação de avaliações

### Appointments App
- `POST /api/v1/appointments/create/` - Criação de agendamentos
- `POST /api/v1/appointments/cancel/<id>/` - Cancelamento de agendamentos
- `POST /api/v1/appointments/confirm/<id>/` - Confirmação de agendamentos
- `POST /api/v1/appointments/complete/<id>/` - Marcação de atendimento realizado
- `GET /api/v1/appointments/barber/list/` - Lista agendamentos do barbeiro
- `GET /api/v1/appointments/client/list/` - Lista agendamentos do cliente
- `GET /api/v1/appointments/barber/statistics/` - Estatísticas do barbeiro
- `GET /api/v1/appointments/client/statistics/` - Estatísticas do cliente

### Schedule App
- `GET /api/v1/schedule/workdays/` - Lista dias de trabalho
- `POST /api/v1/schedule/workdays/` - Cria dia de trabalho
- `PUT /api/v1/schedule/workdays/<id>/` - Atualiza dia de trabalho
- `DELETE /api/v1/schedule/workdays/<id>/` - Remove dia de trabalho
- `GET /api/v1/schedule/available-slots/` - Lista horários disponíveis
- `POST /api/v1/schedule/available-slots/` - Cria horários disponíveis
- `DELETE /api/v1/schedule/available-slots/<id>/` - Remove horário disponível

### Services App
- `GET /api/v1/services/` - Lista serviços
- `POST /api/v1/services/` - Cria novo serviço
- `PUT /api/v1/services/<id>/` - Atualiza serviço
- `DELETE /api/v1/services/<id>/` - Remove serviço

## 🔒 Permissões

### Barbeiros
- Ver, criar, atualizar, excluir(soft-delete) dias de trabalho e os slots(horarios)
- Ver, criar, atualizar, excluir(soft-delete) serviços
- Visualizar histórico de agendamentos
- Confirmar agendamentos
- Marcar atendimentos como realizados
- Visualizar estatísticas de agendamentos
- Visualizar avaliações recebidas

### Clientes
- Criar agendamentos
- Cancelar seus próprios agendamentos(após confirmados)
- Avaliar barbeiros
- Visualizar histórico de agendamentos

## 📊 Estrutura do Projeto

```
agenda-barbe/
├── core/                 # Configurações principais
├── users/               # Gerenciamento de usuários
├── appointments/        # Gerenciamento de agendamentos
├── schedule/           # Gerenciamento de horários
├── services/           # Gerenciamento de serviços
└── requirements.txt    # Dependências do projeto
```

## 🏗️ Arquitetura Django REST Framework

O projeto segue a arquitetura padrão do Django REST Framework, que implementa o padrão MVC (Model-View-Controller) adaptado para APIs REST:

### 1. Models (Modelos)
- Localização: `app/models.py`
- Responsabilidade: Definição da estrutura de dados e regras de negócio
- Exemplo: `User`, `Appointment`, `Service`, `WorkDay`, `TimeSlot`, `Rating`

### 2. Serializers (Serializadores)
- Localização: `app/serializers.py`
- Responsabilidade: Conversão entre objetos Python e JSON
- Funcionalidades:
  - Validação de dados
  - Transformação de dados
  - Relacionamentos aninhados
  - Campos personalizados

### 3. Views (Visualizações)
- Localização: `app/views.py`
- Responsabilidade: Lógica de negócios e manipulação de requisições
- Tipos utilizados:
  - `APIView`: Views baseadas em classes
  - `ViewSet`: Conjunto de operações CRUD
  - `ModelViewSet`: Implementação completa de CRUD

### 4. URLs (Rotas)
- Localização: `app/urls.py`
- Responsabilidade: Mapeamento de URLs para views
- Estrutura:
  - URLs por aplicativo
  - Versionamento de API (v1)

Esta arquitetura permite:
- Separação clara de responsabilidades
- Código organizado e manutenível
- Fácil escalabilidade
- Reutilização de componentes
- Testabilidade
- Segurança robusta

## 🛠️ Ferramentas Utilizadas

### Desenvolvimento
- Git para controle de versão
- VS Code como IDE
- Insomnia para testes de API

### Hospedagem e Infraestrutura
- Render
- Supabase para armazenamento de imagens
- PostgreSQL para banco de dados

## 📖 Documentação Detalhada

### Modelos

#### User
- Campos:
  - `username`: Nome de usuário único
  - `email`: Email único
  - `profile_type`: Tipo de usuário (BARBER ou CLIENT)
  - `is_active`: Esta ativo ou não
  - `username`: Nome do usuário
  - `whatsapp`: Número de WhatsApp
  - `avatar`: Imagem de perfil
  - `pix_key`: Chave PIX (apenas para barbeiros)
  - `city`: Cidade do barbeiro ou cliente usada para filtrar barbeiro nas telas de cliente
  - `appointments_count`: Contador de agendamentos(clientes)
  - `address`: Endereço do barbeiro
  

#### Appointment
- Campos:
  - `barber`: Barbeiro responsável
  - `client`: Cliente que fez o agendamento
  - `service`: Serviço escolhido
  - `time_slot`: Horário do agendamento
  - `status`: Status do agendamento (PENDING, CONFIRMED, COMPLETED, CANCELED)
  - `price`: Preço do agendamento(valor do serviço)
  - `is_free`: Indica se é um agendamento gratuito
  - `created_at`: Data de criação

#### WorkDay
- Campos
  - `barber`: Barbeiro dono do dia de trabalho
  - `day_of_week`: Dia de trabalho na semana
  - `is_active`: Esta ativo ou não
  - `start_time`: Hora de início do expediente
  - `end_time`: Hora de fim do expediente
  - `lunch_start_time`: Hora de início do almoço
  - `lunch_end_time`: Hora de fim do almoço
  - `slot_duration`: Duração de cada horário em minutos

#### TimeSlot
- Campos:
  - `work_day`: Dia da semana
  - `time`: Horário 
  - `is_available`: Indica se o horário esta disponivel ou não
  - `is_active`: Indica se está disponível

#### Service
- Campos:
  - `barber`: Barbeiro que oferece o serviço
  - `name`: Nome do serviço
  - `description`: Descrição do serviço
  - `price`: Preço do serviço
  - `is_active`: Esta ativo ou não
  - `created_at`: Data da criação
  - `image`: url Imagem do serviço


#### Rating
- Campos:
  - `barber`: Barbeiro avaliado
  - `client`: Cliente que fez a avaliação
  - `rating`: Avaliação (1-5 estrelas)
  - `created_at`: Data da avaliação
  - `updated_at`: Última atualização

### Regras de Negócio

1. **Agendamentos**
   - Clientes podem agendar apenas com barbeiros
   - Um horário não pode ser agendado duas vezes
   - Barbeiros podem confirmar, marcar como atendido ou cancelar agendamentos
   - Clientes podem cancelar agendamento (após confirmado)
   - A cada 5 atendimentos, o cliente ganha um agendamento gratuito

2. **Avaliações**
   - Apenas clientes podem avaliar barbeiros
   - Uma avaliação por barbeiro por cliente
   - Avaliações variam de 1 a 5 estrelas

3. **Horários**
   - Barbeiros definem seus dias de trabalho
   - Horários são calculados para cada dia da semana

4. **Serviços**
   - Barbeiros podem cadastrar seus serviços
   - Cada serviço tem preço, descrição e imagem
   - Serviços podem ser editados ou removidos(sof-delete)

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.