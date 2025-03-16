# API para Plataforma de Agendamento de Barbearias  

Esta API permite gerenciar usuários, serviços e agendamentos em uma plataforma voltada para barbearios.  

## Desenvolvedores  

- **Murilo Santos**  
- **José Junior**  

---

## Modelos  

### 1. Usuários  

O modelo `User` estende `AbstractUser` do Django e possui os seguintes campos:  

| Campo                          | Tipo                  | Descrição                                                          |
|--------------------------------|----------------------|------------------------------------------------------------------|
| `email`                        | `EmailField`         | Email único usado para login.                                   |
| `profile_type`                 | `CharField`         | Define se o usuário é `barbeiro` ou `cliente`.                  |
| `is_active`                    | `BooleanField`      | Indica se a conta está ativa (padrão: `True`).                  |
| `username`                     | `CharField`         | Nome de usuário (opcional).                                      |
| `whatsapp`                     | `CharField`         | Número de WhatsApp (opcional).                                   |
| `avatar`                       | `CharField`         | URL da imagem de perfil (opcional).                             |
| `pix_key`                      | `CharField`         | Chave Pix para pagamentos (opcional).                           |
| `city`                         | `CharField`         | Cidade do usuário (ex.: `salinas_mg`).                          |
| `confirmed_appointments_count` | `PositiveIntegerField` | Contagem de agendamentos confirmados (padrão: `0`).              |

#### Tipos de Usuário  

| Valor     | Descrição   |
|-----------|------------|
| `BARBER`  | Barbeiro   |
| `CLIENT`  | Cliente    |

#### Cidades Suportadas  

| Valor        | Descrição |
|-------------|-----------|
| `SALINAS_MG` | Salinas  |

---

### 2. Serviços  

O modelo `Services` representa os serviços oferecidos pelos barbeiros.  

| Campo         | Tipo                | Descrição                                                  |
|--------------|--------------------|----------------------------------------------------------|
| `barber`     | `ForeignKey(User)`  | Referência ao barbeiro que oferece o serviço.           |
| `name`       | `CharField`         | Nome do serviço.                                        |
| `description` | `TextField`        | Descrição detalhada do serviço.                         |
| `price`      | `DecimalField`      | Preço (máximo de 8 dígitos e 2 casas decimais).         |
| `is_active`  | `BooleanField`      | Define se o serviço está disponível (padrão: `True`).   |
| `created_at` | `DateTimeField`     | Data/hora de criação (definido automaticamente).        |
| `image`      | `CharField`         | URL da imagem do serviço (opcional).                    |

---

### 3. Dias de Trabalho  

O modelo `WorkDay` define os dias e horários de expediente dos barbeiros.  

| Campo              | Tipo                   | Descrição                                                |
|--------------------|----------------------|--------------------------------------------------------|
| `barber`          | `ForeignKey(User)`    | Referência ao barbeiro.                                |
| `day_of_week`     | `CharField`           | Dia da semana.                                         |
| `is_active`       | `BooleanField`        | Define se o dia está ativo (padrão: `True`).           |
| `start_time`      | `TimeField`           | Horário de início do expediente (opcional).           |
| `end_time`        | `TimeField`           | Horário de término do expediente (opcional).          |
| `lunch_start_time` | `TimeField`          | Horário de início do almoço (opcional).               |
| `lunch_end_time`  | `TimeField`           | Horário de fim do almoço (opcional).                  |
| `slot_duration`   | `PositiveIntegerField` | Duração dos atendimentos em minutos (padrão: `30`).   |

#### Dias da Semana  

| Valor       | Descrição        |
|-------------|------------------|
| `MONDAY`    | Segunda-feira    |
| `TUESDAY`   | Terça-feira      |
| `WEDNESDAY` | Quarta-feira     |
| `THURSDAY`  | Quinta-feira     |
| `FRIDAY`    | Sexta-feira      |
| `SATURDAY`  | Sábado           |
| `SUNDAY`    | Domingo          |

---

### 4. Horários de Atendimento  

O modelo `TimeSlot` representa os horários disponíveis para agendamentos.  

| Campo        | Tipo                | Descrição                                                   |
|-------------|--------------------|-----------------------------------------------------------|
| `work_day`  | `ForeignKey(WorkDay)` | Referência ao dia de trabalho.                          |
| `time`      | `TimeField`         | Horário específico.                                      |
| `is_available` | `BooleanField`   | Indica se o horário está disponível (padrão: `True`).   |
| `is_active` | `BooleanField`      | Indica se o horário está ativo (padrão: `True`).        |

---

### 5. Agendamentos  

O modelo `Appointment` gerencia os agendamentos de serviços.  

| Campo       | Tipo                  | Descrição                                                |
|------------|----------------------|--------------------------------------------------------|
| `barber`   | `ForeignKey(User)`    | Barbeiro responsável pelo atendimento.                |
| `client`   | `ForeignKey(User)`    | Cliente que realizou o agendamento.                   |
| `service`  | `ForeignKey(Services)` | Serviço escolhido.                                    |
| `time_slot` | `ForeignKey(TimeSlot)` | Horário do agendamento.                              |
| `status`   | `CharField`           | Status do agendamento (`pending`, `confirmed`, `canceled`). |
| `price`    | `DecimalField`        | Valor do serviço (opcional).                          |
| `is_free`  | `BooleanField`        | Indica se o serviço é gratuito (padrão: `False`).    |
| `created_at` | `DateTimeField`     | Data/hora da criação do agendamento.                 |

#### Status do Agendamento  

| Valor       | Descrição    |
|-------------|--------------|
| `PENDING`   | Pendente     |
| `CONFIRMED` | Confirmado   |
| `CANCELED`  | Cancelado    |

---

## Sistema de Permissões da Api:

- **IsBarber**: Permite acesso apenas a usuários do tipo **BARBER**.
- **IsClient**: Permite acesso apenas a usuários do tipo **CLIENTE**.

---